import streamlit as st
from sqlalchemy.orm import Session

from config.settings import get_settings
from services.google_places import GooglePlacesService, PlacesError
from services.lead_service import LeadService
from ui.theme import page_intro


def render(session: Session) -> None:
    settings = get_settings()
    page_intro(
        "Find businesses worth a closer look",
        "Search Google Places by niche and area. Results are deduplicated and saved directly to your lead workspace.",
    )
    st.markdown(
        '<div class="coordinate-panel"><strong>Search coordinate</strong><br>Choose a focused niche and a real city or district. A narrow search usually produces a cleaner outreach list.</div>',
        unsafe_allow_html=True,
    )
    with st.form("places_search"):
        niche_col, location_col = st.columns(2, gap="medium")
        niche = niche_col.text_input(
            "Business niche",
            placeholder="e.g. Dentists",
            help="Use a specific business category for more relevant results.",
        )
        location = location_col.text_input(
            "City or area",
            placeholder="e.g. Casablanca or Maarif",
            help="Enter a city, district, or neighborhood.",
        )

        limit_col, action_col = st.columns([0.34, 0.66], gap="medium")
        max_results = limit_col.number_input(
            "Result limit", min_value=1, max_value=100, value=20, step=5
        )
        action_col.markdown('<div class="search-action-spacer"></div>', unsafe_allow_html=True)
        submitted = action_col.form_submit_button(
            "Search Google Places", type="primary", width="stretch"
        )

    if submitted:
        if not niche.strip() or not location.strip():
            st.markdown(
                """
                <div class="form-validation" role="alert">
                  <span class="form-validation-mark">!</span>
                  <div>
                    <div class="form-validation-title">Complete the search details</div>
                    <div class="form-validation-copy">Enter a business niche and a city or area to continue.</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return
        if not settings.google_maps_api_key:
            st.error("Google Places is not configured. Add GOOGLE_MAPS_API_KEY to .env and restart the app.")
            return
        try:
            with st.status("Searching Google Places…", expanded=True) as status:
                service = GooglePlacesService(
                    settings.google_maps_api_key, settings.request_timeout_seconds
                )
                businesses = service.search(niche, location, int(max_results))
                st.write(f"Found {len(businesses)} businesses. Checking for duplicates…")
                created, skipped = LeadService(session).import_leads(businesses)
                st.session_state.active_niche = niche.strip().title()
                status.update(label="Search complete", state="complete")
            st.success(f"Saved {created} new leads. Skipped {skipped} duplicates.")
        except PlacesError as exc:
            st.error(str(exc))
        except Exception as exc:
            session.rollback()
            st.error(f"The search could not be saved: {exc}")

    with st.expander("Google Places setup"):
        st.markdown(
            "Enable **Places API (New)** in a Google Cloud project, create an API key, and add it as "
            "`GOOGLE_MAPS_API_KEY` in `.env`. Restrict the key to the Places API before regular use."
        )
