"""Discover public business emails for stored leads with websites."""

from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy import select

from config.settings import get_settings
from database.db import SessionLocal
from database.models import Lead
from services.lead_scoring import calculate_lead_score
from services.website_crawler import WebsiteCrawler


def crawl_one(lead_id: int, website: str) -> tuple[int, str | None]:
    settings = get_settings()
    crawler = WebsiteCrawler(
        timeout=settings.request_timeout_seconds,
        max_pages=settings.max_pages_per_domain,
        user_agent=settings.app_user_agent,
    )
    email, _ = crawler.find_email(website)
    return lead_id, email


def main() -> None:
    with SessionLocal() as session:
        targets = list(
            session.execute(
                select(Lead.id, Lead.website).where(
                    Lead.website.is_not(None), Lead.email.is_(None)
                )
            ).all()
        )

    found = checked = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(crawl_one, lead_id, website): lead_id
            for lead_id, website in targets
            if website
        }
        for future in as_completed(futures):
            checked += 1
            lead_id = futures[future]
            try:
                _, email = future.result()
            except Exception as exc:
                print(f"[{checked}/{len(futures)}] lead {lead_id}: {type(exc).__name__}")
                continue
            if email:
                with SessionLocal() as session:
                    lead = session.get(Lead, lead_id)
                    if lead and not lead.email:
                        lead.email = email
                        lead.status = "EMAIL_FOUND" if lead.status == "NEW" else lead.status
                        lead.score = calculate_lead_score(lead)
                        session.commit()
                        found += 1
                print(f"[{checked}/{len(futures)}] lead {lead_id}: {email}")
            else:
                print(f"[{checked}/{len(futures)}] lead {lead_id}: no public email")
    print(f"Completed: checked={checked}, found={found}")


if __name__ == "__main__":
    main()

