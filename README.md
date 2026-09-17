# LeadMap

LeadMap is a local-business lead finder and approval-first Gmail outreach workspace. It searches Google Places, stores deduplicated leads in PostgreSQL, discovers public business emails while respecting `robots.txt`, scores leads, and sends only messages a user has previewed and approved.

## Requirements

- Python 3.12+
- PostgreSQL
- A Google Cloud project with Places API (New) enabled
- Gmail API OAuth desktop credentials for sending

## Local setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` and the Google credentials in `.env`. Then initialize the schema and start the app:

```powershell
alembic upgrade head
streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`).

## Google Places setup

1. Enable **Places API (New)** in Google Cloud.
2. Create an API key and restrict it to Places API.
3. Add it to `.env` as `GOOGLE_MAPS_API_KEY`.

## Gmail setup

1. Enable Gmail API in the Google Cloud project.
2. Configure the OAuth consent screen.
3. Create an OAuth client with application type **Desktop app**.
4. Add its client ID and secret to `.env`.
5. The first approved send opens the Google authorization flow. The resulting token is stored locally in `.gmail_token.json`, which is ignored by Git.

LeadMap requests only the `gmail.send` scope. Every message must be previewed, approved, and then explicitly sent. The default daily hard limit is 20 and the app refuses repeat sends to an address unless the previous message record is changed deliberately.

## Tests

```powershell
pytest -q
```

To discover emails for every stored lead that has a website:

```powershell
python -m scripts.discover_emails
```

## Project layout

- `config/` — environment-backed settings
- `database/` — SQLAlchemy models and Alembic migrations
- `repositories/` — persistence operations
- `services/` — Places, crawling, scoring, validation, and Gmail
- `ui/` — Streamlit pages and visual theme
- `tests/` — core logic tests

## Safety notes

The crawler visits at most five public pages per domain, uses timeouts and a clear user agent, stays on the business domain, and respects `robots.txt` when available. It does not bypass authentication or access controls. Keep outreach relevant, accurate, and compliant with local anti-spam and privacy laws.
