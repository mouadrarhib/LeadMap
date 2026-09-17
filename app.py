import logging

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from ui import analytics_page, campaign_page, leads_page, search_page
from ui.theme import apply_theme

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

st.set_page_config(page_title="LeadMap", page_icon="📍", layout="wide", initial_sidebar_state="expanded")
apply_theme()

with st.sidebar:
    st.markdown("## LeadMap")
    st.caption("Local lead operations")
    page = st.radio(
        "Workspace",
        ["Search businesses", "Lead workspace", "Email campaign", "Activity"],
        label_visibility="collapsed",
    )
    st.divider()
    selected_count = len(st.session_state.get("selected_lead_ids", []))
    st.caption(f"{selected_count} leads selected")

pages = {
    "Search businesses": search_page.render,
    "Lead workspace": leads_page.render,
    "Email campaign": campaign_page.render,
    "Activity": analytics_page.render,
}

try:
    with SessionLocal() as db_session:
        pages[page](db_session)
except SQLAlchemyError as exc:
    st.error(
        "LeadMap could not connect to PostgreSQL. Confirm the server is running and DATABASE_URL in .env is correct."
    )
    st.code(str(exc), language=None)

