import re

from utils.url_utils import domain_from_url


def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    prefix = "+" if phone.strip().startswith("+") else ""
    digits = re.sub(r"\D", "", phone)
    return f"{prefix}{digits}" if digits else None


def duplicate_keys(lead: dict) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    values = {
        "place_id": lead.get("place_id"),
        "domain": lead.get("domain") or domain_from_url(lead.get("website")),
        "email": (lead.get("email") or "").strip().lower() or None,
        "phone": normalize_phone(lead.get("phone")),
    }
    for name, value in values.items():
        if value:
            keys.add((name, str(value).lower()))
    return keys


def deduplicate_leads(leads: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    unique: list[dict] = []
    for lead in leads:
        keys = duplicate_keys(lead)
        if keys & seen:
            continue
        unique.append(lead)
        seen.update(keys)
    return unique

