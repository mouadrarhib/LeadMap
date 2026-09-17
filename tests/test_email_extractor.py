from services.email_extractor import choose_preferred_email, extract_emails_from_html


def test_extracts_visible_and_mailto_emails() -> None:
    html = '<p>Write to hello@acme.ma</p><a href="mailto:sales@acme.ma?subject=Hi">Email</a>'
    assert extract_emails_from_html(html) == {"hello@acme.ma", "sales@acme.ma"}


def test_rejects_known_placeholders() -> None:
    assert extract_emails_from_html(
        "example@example.com, info@example.com, info@yourcompany.example.com and test@test.com"
    ) == set()


def test_prefers_role_address_on_business_domain() -> None:
    emails = {"owner@gmail.com", "info@acme.ma", "person@acme.ma"}
    assert choose_preferred_email(emails, "https://www.acme.ma") == "info@acme.ma"
