import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from config.settings import get_settings
from repositories.lead_repository import LeadRepository
from services.lead_service import LeadService
from services.website_crawler import WebsiteCrawler
from ui.theme import page_intro

STATUSES = ["NEW", "EMAIL_FOUND", "READY", "APPROVED", "SENT", "REPLIED", "BOUNCED", "DO_NOT_CONTACT"]


def _lead_rows(leads) -> list[dict]:
    return [
        {
            "Select": lead.id in st.session_state.get("selected_lead_ids", []),
            "#": position,
            "_lead_id": lead.id,
            "Business": lead.business_name,
            "Phone": lead.phone or "",
            "Email": lead.email or "",
            "Website": lead.website or "",
            "Maps": lead.maps_url or "",
            "Address": lead.address or "",
            "Score": lead.score,
            "Status": lead.status,
        }
        for position, lead in enumerate(leads, start=1)
    ]


def render(session: Session) -> None:
    page_intro(
        "Lead workspace",
        "Filter, inspect, enrich, and select businesses before they enter an outreach campaign.",
    )
    repo = LeadRepository(session)
    leads = repo.list_all()
    if not leads:
        st.info("No leads yet. Start with Search businesses to build your first list.")
        return

    niche_counts: dict[str, int] = {}
    for lead in leads:
        niche_counts[lead.niche] = niche_counts.get(lead.niche, 0) + 1
    recent_niche = st.session_state.get("active_niche") or leads[0].niche
    if recent_niche not in niche_counts:
        recent_niche = leads[0].niche
    niche_labels = {
        f"{name} ({count})": name for name, count in sorted(niche_counts.items())
    }
    all_label = f"All lead lists ({len(leads)})"
    niche_labels[all_label] = "__all__"
    default_label = next(
        label for label, value in niche_labels.items() if value == recent_niche
    )

    list_col, list_context_col = st.columns([1.4, 1.6])
    selected_label = list_col.selectbox(
        "Lead list",
        list(niche_labels),
        index=list(niche_labels).index(default_label),
    )
    selected_niche = niche_labels[selected_label]
    if selected_niche != "__all__":
        st.session_state.active_niche = selected_niche
        list_context_col.markdown(
            f'<div class="list-context"><strong>{niche_counts[selected_niche]} leads</strong><span>Showing only {selected_niche}</span></div>',
            unsafe_allow_html=True,
        )
    else:
        list_context_col.markdown(
            f'<div class="list-context"><strong>{len(leads)} leads</strong><span>Showing every lead list</span></div>',
            unsafe_allow_html=True,
        )

    filter_col, status_col, score_col = st.columns([1.2, 1, 1])
    query = filter_col.text_input("Search leads", placeholder="Name, city, email…")
    status_filter = status_col.multiselect("Status", STATUSES)
    min_score = score_col.slider("Minimum score", 0, 100, 0, 5)
    flags = st.columns(3)
    email_only = flags[0].checkbox("Has email")
    phone_only = flags[1].checkbox("Has phone")
    website_only = flags[2].checkbox("Has website")

    def matches(lead) -> bool:
        haystack = " ".join(
            [lead.business_name or "", lead.city or "", lead.email or "", lead.address or ""]
        ).lower()
        return (
            (selected_niche == "__all__" or lead.niche == selected_niche)
            and (not query or query.lower() in haystack)
            and (not status_filter or lead.status in status_filter)
            and lead.score >= min_score
            and (not email_only or bool(lead.email))
            and (not phone_only or bool(lead.phone))
            and (not website_only or bool(lead.website))
        )

    filtered = [lead for lead in leads if matches(lead)]
    st.markdown(f"**{len(filtered)} leads in this list**")
    edited = st.data_editor(
        pd.DataFrame(_lead_rows(filtered)),
        hide_index=True,
        use_container_width=True,
        disabled=[
            "#",
            "_lead_id",
            "Business",
            "Phone",
            "Email",
            "Website",
            "Maps",
            "Address",
            "Score",
            "Status",
        ],
        column_config={
            "Select": st.column_config.CheckboxColumn("Select"),
            "#": st.column_config.NumberColumn("#", width="small"),
            "_lead_id": None,
            "Website": st.column_config.LinkColumn("Website", display_text="Open website"),
            "Maps": st.column_config.LinkColumn("Maps", display_text="Open Maps"),
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100),
        },
        key="lead_table",
    )
    selected_ids = (
        edited.loc[edited["Select"], "_lead_id"].astype(int).tolist() if not edited.empty else []
    )
    st.session_state.selected_lead_ids = selected_ids
    st.caption(f"{len(filtered)} leads shown · {len(selected_ids)} selected")

    action_cols = st.columns([1, 1, 1, 2])
    if action_cols[0].button("Select shown", use_container_width=True):
        st.session_state.selected_lead_ids = [lead.id for lead in filtered]
        st.rerun()
    if action_cols[1].button("Find emails", disabled=not selected_ids, use_container_width=True):
        _discover_emails(session, selected_ids)
    if action_cols[2].button("Delete selected", disabled=not selected_ids, use_container_width=True):
        deleted = repo.delete_many(selected_ids)
        st.session_state.selected_lead_ids = []
        st.success(f"Deleted {deleted} leads.")
        st.rerun()

    export_rows = _lead_rows(filtered)
    for row in export_rows:
        row.pop("Select", None)
        row.pop("_lead_id", None)
    csv = pd.DataFrame(export_rows).to_csv(index=False).encode("utf-8")
    action_cols[3].download_button(
        "Export filtered CSV", csv, "leadmap_leads.csv", "text/csv", use_container_width=True
    )

    if not any(lead.email for lead in leads) and any(lead.website for lead in leads):
        st.info(
            "Google Places does not provide email addresses. Select leads with websites, then use "
            "Find emails to scan their public pages."
        )

    with st.expander("Edit one lead"):
        options = {f"{lead.business_name} (#{lead.id})": lead for lead in filtered}
        if options:
            label = st.selectbox("Lead", options)
            lead = options[label]
            with st.form(f"edit_{lead.id}"):
                name = st.text_input("Business name", value=lead.business_name)
                email = st.text_input("Email", value=lead.email or "")
                phone = st.text_input("Phone", value=lead.phone or "")
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(lead.status))
                opportunity = st.slider("Opportunity score", 0, 20, lead.opportunity_score)
                if st.form_submit_button("Save changes", type="primary"):
                    from repositories.email_repository import EmailRepository
                    from services.lead_scoring import calculate_lead_score

                    lead.business_name, lead.email, lead.phone = name, email.strip().lower() or None, phone or None
                    lead.status, lead.opportunity_score = status, opportunity
                    lead.score = calculate_lead_score(lead)
                    repo.commit()
                    if status == "DO_NOT_CONTACT" and lead.email:
                        EmailRepository(session).suppress(lead.email)
                    st.success("Lead updated.")
                    st.rerun()


def _discover_emails(session: Session, selected_ids: list[int]) -> None:
    settings = get_settings()
    repo = LeadRepository(session)
    service = LeadService(session)
    crawler = WebsiteCrawler(
        settings.request_timeout_seconds, settings.max_pages_per_domain, settings.app_user_agent
    )
    found = 0
    progress = st.progress(0, text="Starting public email discovery…")
    for index, lead_id in enumerate(selected_ids, 1):
        lead = repo.get(lead_id)
        if lead and lead.website:
            email, _ = crawler.find_email(lead.website)
            if email:
                service.update_email(lead, email)
                found += 1
        progress.progress(index / len(selected_ids), text=f"Checked {index} of {len(selected_ids)} websites")
    progress.empty()
    st.success(f"Email discovery finished. Found {found} preferred business emails.")
    st.rerun()
