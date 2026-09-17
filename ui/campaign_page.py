from string import Formatter

import streamlit as st
from sqlalchemy.orm import Session

from config.settings import get_settings
from repositories.email_repository import EmailRepository
from repositories.lead_repository import LeadRepository
from services.gmail_service import GmailService
from ui.theme import page_intro

DEFAULT_SUBJECT = "A quick idea for {business_name}"
DEFAULT_BODY = """Hello {business_name},

I came across your business while researching companies in {city}.

I noticed an opportunity to improve your online presence and would be happy to show you a quick idea.

Best regards,
Mouad"""
ALLOWED_FIELDS = {"business_name", "city", "website", "first_name"}


class SafeFields(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _render_template(template: str, lead) -> str:
    fields = {field for _, field, _, _ in Formatter().parse(template) if field}
    unknown = fields - ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"Unsupported variables: {', '.join(sorted(unknown))}")
    return template.format_map(
        SafeFields(
            business_name=lead.business_name,
            city=lead.city or "your area",
            website=lead.website or "",
            first_name="",
        )
    )


def render(session: Session) -> None:
    settings = get_settings()
    page_intro(
        "Compose with a human checkpoint",
        "Create personalized drafts, inspect every recipient, then approve before Gmail can send anything.",
    )
    selected_ids = st.session_state.get("selected_lead_ids", [])
    leads = [LeadRepository(session).get(lead_id) for lead_id in selected_ids]
    leads = [lead for lead in leads if lead and lead.email and lead.status != "DO_NOT_CONTACT"]
    if not leads:
        st.info("Select leads with email addresses in the Lead workspace before preparing a campaign.")
        return

    email_repo = EmailRepository(session)
    sent_today = email_repo.sent_today()
    st.metric("Emails sent today", f"{sent_today} / {settings.daily_email_limit}")

    with st.form("campaign_template"):
        name = st.text_input("Campaign name", value="Local business introduction")
        subject_template = st.text_input("Subject template", value=DEFAULT_SUBJECT)
        body_template = st.text_area("Email body template", value=DEFAULT_BODY, height=240)
        daily_limit = st.number_input(
            "Daily hard limit", min_value=1, max_value=100, value=settings.daily_email_limit
        )
        st.caption("Available variables: {business_name}, {city}, {website}, {first_name}")
        preview_clicked = st.form_submit_button("Build previews", type="primary")

    if preview_clicked:
        try:
            previews = [
                {
                    "lead_id": lead.id,
                    "recipient": lead.email,
                    "subject": _render_template(subject_template, lead),
                    "body": _render_template(body_template, lead),
                }
                for lead in leads
            ]
            st.session_state.campaign_draft = {
                "name": name,
                "subject_template": subject_template,
                "body_template": body_template,
                "daily_limit": int(daily_limit),
                "previews": previews,
            }
        except ValueError as exc:
            st.error(str(exc))

    draft = st.session_state.get("campaign_draft")
    if draft:
        st.subheader("Preview queue")
        for preview in draft["previews"]:
            with st.expander(f'{preview["recipient"]} — {preview["subject"]}'):
                st.text(preview["body"])
        st.warning(
            "Approval creates send-ready messages. It does not send them. Review the recipients and copy above first."
        )
        if st.button("Approve all previews", type="primary"):
            campaign = email_repo.save_campaign(
                draft["name"], draft["subject_template"], draft["body_template"], draft["daily_limit"]
            )
            approved = 0
            for preview in draft["previews"]:
                if email_repo.is_suppressed(preview["recipient"]):
                    continue
                email_repo.create_message(campaign.id, **preview)
                lead = LeadRepository(session).get(preview["lead_id"])
                lead.status = "APPROVED"
                session.commit()
                approved += 1
            st.session_state.approved_campaign_id = campaign.id
            st.session_state.pop("campaign_draft", None)
            st.success(f"Approved {approved} messages. They are ready, but not yet sent.")
            st.rerun()

    campaign_id = st.session_state.get("approved_campaign_id")
    if campaign_id:
        messages = email_repo.approved_messages(campaign_id)
        if messages:
            st.divider()
            st.subheader("Approved send queue")
            st.write(f"{len(messages)} messages are awaiting your final send action.")
            if st.button("Send approved through Gmail", type="primary"):
                _send_messages(session, campaign_id)


def _send_messages(session: Session, campaign_id: int) -> None:
    settings = get_settings()
    repo = EmailRepository(session)
    messages = repo.approved_messages(campaign_id)
    campaign_limit = messages[0].campaign.daily_limit if messages else settings.daily_email_limit
    effective_limit = min(settings.daily_email_limit, campaign_limit, 100)
    remaining = effective_limit - repo.sent_today()
    if remaining <= 0:
        st.error("The configured daily sending limit has been reached.")
        return
    gmail = GmailService(settings.google_client_id, settings.google_client_secret)
    sent = 0
    failures = []
    progress = st.progress(0, text="Connecting to Gmail…")
    for index, message in enumerate(messages[:remaining], 1):
        if (
            repo.is_suppressed(message.recipient)
            or message.lead.status == "DO_NOT_CONTACT"
            or repo.was_sent(message.recipient)
        ):
            failures.append(f"{message.recipient}: suppressed or already contacted")
            continue
        try:
            gmail_id, sent_at = gmail.send(message.recipient, message.subject, message.body)
            repo.mark_sent(message, gmail_id, sent_at)
            sent += 1
        except Exception as exc:
            message.status = "FAILED"
            session.commit()
            failures.append(f"{message.recipient}: {exc}")
        progress.progress(index / min(len(messages), remaining), text=f"Processed {index} messages")
    progress.empty()
    if sent:
        st.success(f"Sent {sent} messages through Gmail.")
    if failures:
        st.error("Some messages were not sent:\n" + "\n".join(failures))
