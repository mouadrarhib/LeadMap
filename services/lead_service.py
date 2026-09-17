from sqlalchemy.orm import Session

from database.models import Lead
from repositories.lead_repository import LeadRepository
from services.lead_scoring import calculate_lead_score
from utils.deduplication import deduplicate_leads
from utils.url_utils import domain_from_url


class LeadService:
    def __init__(self, session: Session):
        self.repo = LeadRepository(session)

    def import_leads(self, leads: list[dict]) -> tuple[int, int]:
        created = skipped = 0
        for data in deduplicate_leads(leads):
            data["domain"] = data.get("domain") or domain_from_url(data.get("website"))
            if self.repo.find_duplicate(data):
                skipped += 1
                continue
            data["score"] = calculate_lead_score(data)
            self.repo.add(data)
            created += 1
        self.repo.commit()
        return created, skipped

    def update_email(self, lead: Lead, email: str | None) -> Lead:
        lead.email = email
        if email and lead.status == "NEW":
            lead.status = "EMAIL_FOUND"
        lead.score = calculate_lead_score(lead)
        self.repo.commit()
        return lead

