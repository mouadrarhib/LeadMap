from urllib.parse import urljoin, urlparse


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    value = url.strip()
    if not value:
        return None
    if not value.startswith(("http://", "https://")):
        value = f"https://{value}"
    return value


def domain_from_url(url: str | None) -> str | None:
    normalized = normalize_url(url)
    if not normalized:
        return None
    hostname = (urlparse(normalized).hostname or "").lower()
    return hostname.removeprefix("www.") or None


def same_domain(url: str, expected_domain: str) -> bool:
    domain = domain_from_url(url)
    return domain == expected_domain or bool(domain and domain.endswith(f".{expected_domain}"))


def absolute_url(base: str, href: str) -> str:
    return urljoin(base, href)

