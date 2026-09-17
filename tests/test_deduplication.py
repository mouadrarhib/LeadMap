from utils.deduplication import deduplicate_leads, normalize_phone


def test_normalize_phone() -> None:
    assert normalize_phone("+212 6 12-34-56-78") == "+212612345678"


def test_deduplicates_by_domain() -> None:
    leads = [
        {"business_name": "A", "website": "https://www.acme.ma"},
        {"business_name": "A branch", "website": "https://acme.ma/contact"},
    ]
    assert len(deduplicate_leads(leads)) == 1

