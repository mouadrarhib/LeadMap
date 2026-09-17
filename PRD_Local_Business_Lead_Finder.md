# PRD — Local Business Lead Finder & Outreach Tool

## 1. Product Overview

Build a lightweight web application that helps a user find local businesses by niche and location, collect publicly available business contact information, discover public email addresses from business websites, organize leads, and send personalized outreach emails through Gmail after user approval.

The product is intended as a small lead-generation CRM for local business outreach.

---

## 2. Product Goal

The MVP should allow the user to:

1. Enter a business niche and city/area.
2. Search businesses using Google Places API.
3. Collect useful business information.
4. Visit business websites and extract publicly listed email addresses.
5. Save, deduplicate, filter, and score leads.
6. Open the business directly in Google Maps.
7. Prepare personalized outreach emails.
8. Preview and approve emails before sending.
9. Send emails through Gmail API.
10. Track outreach status and basic results.

---

## 3. Target User

A freelancer, developer, agency owner, or salesperson who wants to find local businesses and offer services such as:

- Website development
- E-commerce
- WhatsApp automation
- Booking systems
- Business automation
- Digital presence improvements

---

## 4. Recommended MVP Stack

### Backend / Core
- Python 3.12+
- Requests or HTTPX
- BeautifulSoup4
- Regex
- Pandas

### UI
- Streamlit

### Database
- PostgreSQL
- SQLAlchemy recommended
- Alembic for database migrations

### External APIs
- Google Places API
- Gmail API

### Authentication
- Google OAuth 2.0 for Gmail

### Optional Later
- FastAPI backend
- React frontend
- Celery / Redis for background jobs

---

## 5. Core User Flow

### Step 1 — Search
User enters:

- Niche
- City / area
- Maximum number of businesses

Example:

```text
Niche: Dentists
Location: Casablanca
Max results: 100
```

The application searches Google Places.

### Step 2 — Collect Business Data

For every business, collect when available:

- Business name
- Google Place ID
- Address
- Phone number
- Website
- Google Maps link
- Business category
- Rating
- Review count

### Step 3 — Find Email

If a website exists:

1. Visit the website.
2. Inspect the homepage.
3. Look for likely contact pages:
   - /contact
   - /contact-us
   - /about
   - /about-us
4. Extract public email addresses.
5. Reject obviously invalid emails.
6. Prefer business-domain emails.

Example:

```text
contact@company.ma
hello@company.com
info@company.ma
```

Do not attempt to bypass authentication, CAPTCHAs, access controls, or private areas.

### Step 4 — Store Leads

Save all leads in PostgreSQL.

Automatically detect duplicates using:

1. Google Place ID
2. Website domain
3. Email address
4. Phone number

### Step 5 — Review Leads

Display leads in a table.

Suggested columns:

| Select | Business | Phone | Email | Website | Maps | Score | Status |
|---|---|---|---|---|---|---|---|

User can:

- Search
- Filter
- Sort
- Select leads
- Edit a lead
- Delete a lead
- Open website
- Open Google Maps

### Step 6 — Email Preparation

User creates an email template.

Supported variables:

```text
{business_name}
{city}
{website}
{first_name}
```

Example:

```text
Hello {business_name},

I came across your business while researching companies in {city}.

I noticed an opportunity to improve your online presence and would be happy to show you a quick idea.

Best regards,
Mouad
```

### Step 7 — Preview & Approval

Before sending:

- Render the personalized email.
- Show recipient.
- Show subject.
- Show body.
- Require user approval.

MVP must NOT automatically send every discovered lead without review.

### Step 8 — Send

Send approved emails using Gmail API.

Track:

- Email sent timestamp
- Gmail message ID
- Lead status

### Step 9 — Track

Lead statuses:

```text
NEW
EMAIL_FOUND
READY
APPROVED
SENT
REPLIED
BOUNCED
DO_NOT_CONTACT
```

---

## 6. Dashboard Pages

### Page 1 — Search Businesses

Fields:

- Niche
- Location
- Maximum results
- Search button

Show progress and number of businesses found.

---

### Page 2 — Leads

Table with:

- Checkbox
- Business name
- Phone
- Email
- Website
- Google Maps link
- Address
- Score
- Status

Filters:

- Has email
- Has phone
- Has website
- Status
- Minimum score

Actions:

- Select all
- Delete
- Export CSV
- Prepare email

---

### Page 3 — Email Campaign

Fields:

- Subject template
- Email body template

Actions:

- Preview
- Approve selected
- Send approved

Show:

```text
Emails sent today: 18 / 100
```

The daily limit must be configurable.

---

### Page 4 — Activity / Tracking

Show:

- Total leads
- Emails found
- Emails sent
- Replies
- Bounces
- Do-not-contact leads

MVP only needs simple counters and tables.

---

## 7. Google Maps Integration

Each business should have a direct Google Maps URL.

Prefer using Google Place ID.

Store:

```text
place_id
maps_url
```

The UI should provide an:

```text
Open Maps
```

button/link for every business.

---

## 8. Lead Scoring

Create a simple score from 0 to 100.

Example MVP scoring:

```text
+25 email found
+15 phone found
+15 website exists
+15 Google rating available
+10 review count > 5
+20 configurable opportunity score
```

Keep scoring logic in a separate service/module so it can easily be changed.

Do not use AI scoring in V1 unless explicitly enabled.

---

## 9. Email Discovery Rules

The crawler should:

- Only visit publicly accessible web pages.
- Use reasonable request timeouts.
- Use a clear user agent.
- Limit pages visited per domain.
- Avoid repeated crawling.
- Respect robots.txt where applicable.
- Never bypass login pages or access controls.
- Never scrape private personal data.

Suggested maximum:

```text
5 pages per domain
```

Suggested timeout:

```text
10 seconds per request
```

Email regex must be combined with validation logic.

Exclude obvious false positives such as:

```text
example@example.com
name@domain.com
test@test.com
```

---

## 10. Email Safety & Sending Rules

The application must include:

- Configurable daily hard limit.
- Default daily limit: 20 for new setup.
- Maximum configurable MVP limit: 100.
- Manual approval before sending.
- Deduplication.
- Do-not-contact list.
- Bounce tracking field.
- Unsubscribe / opt-out tracking field.
- No repeated email to the same address unless explicitly approved.

Do not implement techniques intended to bypass Gmail anti-spam systems.

---

## 11. Data Model

### Lead

```text
id
place_id
business_name
category
address
city
phone
website
domain
email
maps_url
rating
review_count
score
status
source
created_at
updated_at
last_contacted_at
```

### EmailCampaign

```text
id
name
subject_template
body_template
daily_limit
created_at
updated_at
```

### EmailMessage

```text
id
lead_id
campaign_id
recipient
subject
body
gmail_message_id
status
sent_at
created_at
```

### Suppression

```text
id
email
reason
created_at
```

---

## 12. Suggested Project Structure

```text
leadfinder/
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
│
├── config/
│   └── settings.py
│
├── database/
│   ├── db.py
│   ├── models.py
│   └── migrations/
│
├── services/
│   ├── google_places.py
│   ├── website_crawler.py
│   ├── email_extractor.py
│   ├── email_validator.py
│   ├── lead_service.py
│   ├── lead_scoring.py
│   └── gmail_service.py
│
├── repositories/
│   ├── lead_repository.py
│   └── email_repository.py
│
├── ui/
│   ├── search_page.py
│   ├── leads_page.py
│   ├── campaign_page.py
│   └── analytics_page.py
│
├── utils/
│   ├── url_utils.py
│   ├── deduplication.py
│   └── logging.py
│
└── tests/
    ├── test_email_extractor.py
    ├── test_deduplication.py
    ├── test_scoring.py
    └── test_places_service.py
```

---

## 13. Environment Variables

Use a `.env` file.

Example:

```env
GOOGLE_MAPS_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

DATABASE_URL=postgresql+psycopg://leadfinder:password@localhost:5432/leadfinder

DAILY_EMAIL_LIMIT=20
MAX_PAGES_PER_DOMAIN=5
REQUEST_TIMEOUT_SECONDS=10
```

Never commit API keys or OAuth secrets.

---

## 14. Functional Requirements

### FR-01
User can search businesses by niche and location.

### FR-02
Application can retrieve business details from Google Places.

### FR-03
Application stores Google Maps links.

### FR-04
Application can crawl the public website of a business.

### FR-05
Application extracts public business emails.

### FR-06
Application deduplicates businesses and emails.

### FR-07
Application stores leads in PostgreSQL.

### FR-08
User can filter and sort leads.

### FR-09
User can export leads to CSV.

### FR-10
User can define an email template.

### FR-11
Application personalizes the template for each lead.

### FR-12
User can preview emails before sending.

### FR-13
User must explicitly approve emails before sending.

### FR-14
Application sends approved messages through Gmail API.

### FR-15
Application enforces a daily email limit.

### FR-16
Application records email send status.

### FR-17
Application supports a do-not-contact list.

---

## 15. Non-Functional Requirements

- Clean modular Python code.
- PostgreSQL must be the primary database in development and production.
- Use Alembic migrations for schema changes.
- Type hints where useful.
- Clear error messages.
- API failures must not crash the whole app.
- Database transactions should be safe.
- Secrets must not appear in source control.
- Network requests require timeouts.
- Logging should avoid storing OAuth tokens or secrets.
- UI should remain simple and fast.
- Code should be easy to migrate from Streamlit to FastAPI later.

---

## 16. Error Handling

Handle at minimum:

- Google API key missing
- Google API quota exceeded
- Google Places API error
- Website unreachable
- Invalid SSL certificate
- Request timeout
- No email found
- Gmail authentication failure
- Gmail send failure
- Duplicate lead
- Daily sending limit reached

Display human-readable messages in the UI.

---

## 17. MVP Acceptance Criteria

The MVP is complete when the user can:

1. Start the Streamlit application locally.
2. Enter `Dentists` and `Casablanca`.
3. Retrieve businesses from Google Places.
4. See business name, address, website, phone, and Maps link when available.
5. Run email discovery against business websites.
6. Save leads in PostgreSQL.
7. Filter leads that have emails.
8. Select one or more leads.
9. Create an email template.
10. Preview personalized messages.
11. Approve selected messages.
12. Send them through Gmail API.
13. See their status change to `SENT`.
14. Export the lead table to CSV.
15. Prevent sending beyond the configured daily limit.

---

## 18. Out of Scope for V1

Do NOT build these initially:

- AI-generated emails
- Automatic mass sending without approval
- LinkedIn scraping
- Browser automation against Google Maps UI
- CAPTCHA bypassing
- Proxy rotation
- Email open tracking pixels
- Complex CRM integrations
- Multi-user accounts
- Payments
- Mobile application
- Full React frontend
- Kubernetes deployment

These can be considered later.

---

## 19. Future Improvements

Possible V2 features:

- FastAPI REST backend
- React frontend
- PostgreSQL
- AI-based lead scoring
- AI-assisted email personalization
- Reply detection
- Gmail inbox synchronization
- Follow-up scheduling
- Campaign analytics
- Multiple campaigns
- Team accounts
- CRM integrations
- Website quality analysis
- Detect businesses without websites
- WhatsApp outreach workflows
- Notion integration

---

## 20. Development Order

Implement in this order:

### Phase 1
- Initialize project
- Config
- PostgreSQL setup
- SQLAlchemy + Alembic
- Lead model
- Streamlit base UI

### Phase 2
- Google Places search
- Business details
- Google Maps links
- Lead storage

### Phase 3
- Website crawler
- Contact page discovery
- Email extraction
- Email validation
- Deduplication

### Phase 4
- Leads dashboard
- Filters
- Lead scoring
- CSV export

### Phase 5
- Gmail OAuth
- Email templates
- Preview
- Approval
- Sending
- Daily limit

### Phase 6
- Tracking
- Error handling
- Tests
- README
- `.env.example`

---

## 21. Implementation Instructions

The implementation should:

1. Build the application incrementally.
2. Keep modules small and separated by responsibility.
3. Never hardcode credentials.
4. Use environment variables.
5. Include setup instructions.
6. Add unit tests for core logic.
7. Prefer simple, maintainable code over overengineering.
8. Do not add functionality outside this PRD unless required technically.
9. Do not implement scraping techniques that bypass platform protections.
10. Ensure the app can run locally with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 22. Definition of Done

The project is considered MVP-ready when a new developer can:

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Add Google and Gmail credentials.
4. Install dependencies.
5. Start Streamlit.
6. Search businesses.
7. collect public business contact data.
8. Discover public emails from websites.
9. Review and approve outreach messages.
10. Send approved messages.
11. Track lead status in PostgreSQL.
