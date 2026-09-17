import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700&display=swap');
        :root {
          --ocean: #0b2c3d;
          --ocean-2: #154b62;
          --paper: #f6f8f7;
          --ink: #13262e;
          --amber: #ef9f27;
          --line: #d7e0df;
          --mist: #eaf0ef;
        }
        .stApp { background: var(--paper); color: var(--ink); font-family: 'DM Sans', sans-serif; }
        h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: var(--ocean) !important; letter-spacing: -0.035em; }
        h1 { font-size: clamp(2.1rem, 4vw, 3.7rem) !important; line-height: 1.02 !important; max-width: 820px; }
        [data-testid="stSidebar"] { background: var(--ocean); border-right: 0; }
        [data-testid="stSidebar"] * { color: #f4f8f8; }
        [data-testid="stSidebar"] [role="radiogroup"] label {
          padding: .45rem .65rem; border-radius: 7px; margin-bottom: .2rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: #19485b; }
        [data-testid="stMetric"] {
          background: white; border: 1px solid var(--line); border-top: 3px solid var(--amber);
          padding: 1rem 1.1rem; border-radius: 7px;
        }
        [data-testid="stMetricValue"] { color: var(--ocean); font-family: 'Manrope', sans-serif; }
        .coordinate-panel {
          background: var(--ocean); color: #f6fbfb; padding: 1.3rem 1.5rem;
          border-radius: 9px; border-left: 5px solid var(--amber); margin: .5rem 0 1.25rem;
        }
        .coordinate-panel strong { color: #ffd38b; }
        .eyeline { color: #557079; font-size: .92rem; max-width: 720px; margin-top: -.75rem; margin-bottom: 1.5rem; }
        .status-pill { display: inline-block; padding: .2rem .55rem; border-radius: 99px; background: var(--mist); color: var(--ocean); font-size: .8rem; }
        .stButton > button, .stDownloadButton > button {
          border-radius: 6px; border: 1px solid var(--ocean); font-weight: 600;
        }
        .stButton > button[kind="primary"] { background: var(--ocean); color: white; }
        a { color: var(--ocean-2); }
        div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 7px; overflow: hidden; }
        [data-testid="stForm"] {
          background: #ffffff;
          border: 1px solid #cfdbd9;
          border-radius: 10px;
          padding: 1.35rem 1.4rem 1.45rem;
          box-shadow: 0 1px 0 rgba(11, 44, 61, .04);
        }
        [data-testid="stForm"] label p {
          color: var(--ocean);
          font-weight: 600;
          font-size: .91rem;
        }
        [data-testid="stForm"] input {
          min-height: 46px;
          background: #f8faf9;
          border-color: #c9d6d4;
          border-radius: 6px;
        }
        [data-testid="stForm"] input::placeholder { color: #7b8e94; }
        [data-testid="stForm"] [data-testid="InputInstructions"] {
          display: none !important;
        }
        [data-testid="stFormSubmitButton"] button {
          min-height: 46px;
          border-radius: 6px;
        }
        .search-action-spacer { height: 1.78rem; }
        .form-validation {
          display: flex;
          align-items: flex-start;
          gap: .8rem;
          margin: .85rem 0 1rem;
          padding: .85rem 1rem;
          background: #fff8e9;
          border: 1px solid #efd39b;
          border-left: 4px solid var(--amber);
          border-radius: 7px;
        }
        .form-validation-mark {
          display: inline-grid;
          place-items: center;
          flex: 0 0 1.35rem;
          width: 1.35rem;
          height: 1.35rem;
          margin-top: .1rem;
          border-radius: 50%;
          background: var(--amber);
          color: var(--ocean);
          font-size: .82rem;
          font-weight: 800;
        }
        .form-validation-title {
          color: var(--ocean);
          font-size: .94rem;
          font-weight: 700;
          line-height: 1.35;
        }
        .form-validation-copy {
          color: #526971;
          font-size: .89rem;
          line-height: 1.45;
          margin-top: .08rem;
        }
        .list-context {
          display: flex;
          flex-direction: column;
          justify-content: center;
          min-height: 4.35rem;
          margin-top: 1.72rem;
          padding: .65rem .9rem;
          border-left: 3px solid var(--amber);
          color: var(--ocean);
        }
        .list-context strong { font-size: .95rem; line-height: 1.3; }
        .list-context span { color: #60767d; font-size: .84rem; margin-top: .08rem; }
        input:focus, textarea:focus, button:focus-visible { outline: 3px solid rgba(239,159,39,.45) !important; }
        @media (max-width: 640px) {
          [data-testid="stForm"] { padding: 1rem; }
          .search-action-spacer { height: .25rem; }
        }
        @media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; transition: none !important; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_intro(title: str, description: str) -> None:
    st.title(title)
    st.markdown(f'<p class="eyeline">{description}</p>', unsafe_allow_html=True)
