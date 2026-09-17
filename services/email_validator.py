import re

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,24}\b")
INVALID_EMAILS = {"example@example.com", "name@domain.com", "test@test.com"}
INVALID_PREFIXES = ("noreply@", "no-reply@", "donotreply@")
INVALID_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")
PLACEHOLDER_DOMAINS = {"example.com", "example.org", "example.net", "domain.com"}


def is_valid_business_email(email: str) -> bool:
    value = email.strip().lower().strip(".,;:<>[]()\"'")
    if not EMAIL_RE.fullmatch(value):
        return False
    if value in INVALID_EMAILS or value.startswith(INVALID_PREFIXES):
        return False
    if value.endswith(INVALID_SUFFIXES) or ".." in value:
        return False
    local, domain = value.rsplit("@", 1)
    if domain in PLACEHOLDER_DOMAINS or domain.endswith(".example.com"):
        return False
    return bool(local and "." in domain and not domain.startswith(".") and not domain.endswith("."))


def extract_valid_emails(text: str) -> set[str]:
    return {match.lower() for match in EMAIL_RE.findall(text or "") if is_valid_business_email(match)}
