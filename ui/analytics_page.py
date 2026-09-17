import pandas as pd
import streamlit as st
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.models import EmailMessage, Lead
from ui.theme import page_intro


def render(session: Session) -> None:
    page_intro(
        "Activity and outcomes",
        "A compact view of list quality and outreach state. Reply and bounce statuses can be updated from the lead editor.",
    )
    leads = list(session.scalars(select(Lead).order_by(Lead.updated_at.desc())).all())
    total = len(leads)
    metrics = st.columns(5)
    metrics[0].metric("Total leads", total)
    metrics[1].metric("Emails found", sum(bool(lead.email) for lead in leads))
    metrics[2].metric("Sent", sum(lead.status == "SENT" for lead in leads))
    metrics[3].metric("Replies", sum(lead.status == "REPLIED" for lead in leads))
    metrics[4].metric("Do not contact", sum(lead.status == "DO_NOT_CONTACT" for lead in leads))

    status_counts = session.execute(
        select(Lead.status, func.count(Lead.id)).group_by(Lead.status).order_by(Lead.status)
    ).all()
    if status_counts:
        st.subheader("Pipeline distribution")
        chart = pd.DataFrame(status_counts, columns=["Status", "Leads"]).set_index("Status")
        st.bar_chart(chart, color="#ef9f27")

    sent = session.execute(
        select(EmailMessage.recipient, EmailMessage.subject, EmailMessage.status, EmailMessage.sent_at)
        .order_by(EmailMessage.created_at.desc())
        .limit(100)
    ).all()
    st.subheader("Recent email activity")
    if sent:
        st.dataframe(
            pd.DataFrame(sent, columns=["Recipient", "Subject", "Status", "Sent at"]),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No campaign messages have been created yet.")

