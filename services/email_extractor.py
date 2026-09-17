from bs4 import BeautifulSoup

from services.email_validator import extract_valid_emails, is_valid_business_email
from utils.url_utils import domain_from_url


def extract_emails_from_html(html: str) -> set[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    emails = extract_valid_emails(soup.get_text(" ", strip=True))
    for link in soup.select('a[href^="mailto:"]'):
        raw = link.get("href", "").removeprefix("mailto:").split("?", 1)[0]
        for candidate in raw.split(","):
            candidate = candidate.strip().lower()
            if is_valid_business_email(candidate):
                emails.add(candidate)
    return emails


def choose_preferred_email(emails: set[str], website: str | None) -> str | None:
    if not emails:
        return None
    domain = domain_from_url(website)
    role_order = {"contact": 0, "hello": 1, "info": 2, "office": 3, "sales": 4}

    def rank(email: str) -> tuple[int, int, str]:
        local, email_domain = email.split("@", 1)
        domain_rank = 0 if domain and (email_domain == domain or email_domain.endswith(f".{domain}")) else 1
        role_rank = role_order.get(local, 10)
        return domain_rank, role_rank, email

    return sorted(emails, key=rank)[0]

