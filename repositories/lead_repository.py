from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from database.models import Lead
from utils.deduplication import normalize_phone


class LeadRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, data: dict) -> Lead:
        allowed = {column.name for column in Lead.__table__.columns if column.name != "id"}
        lead = Lead(**{key: value for key, value in data.items() if key in allowed})
        self.session.add(lead)
        return lead

    def find_duplicate(self, data: dict) -> Lead | None:
        clauses = []
        if data.get("place_id"):
            clauses.append(Lead.place_id == data["place_id"])
        if data.get("domain"):
            clauses.append(Lead.domain == data["domain"])
        if data.get("email"):
            clauses.append(Lead.email == data["email"].lower())
        normalized_phone = normalize_phone(data.get("phone"))
        if normalized_phone:
            candidates = self.session.scalars(select(Lead).where(Lead.phone.is_not(None))).all()
            for lead in candidates:
                if normalize_phone(lead.phone) == normalized_phone:
                    return lead
        if not clauses:
            return None
        return self.session.scalar(select(Lead).where(or_(*clauses)).limit(1))

    def list_all(self) -> list[Lead]:
        return list(self.session.scalars(select(Lead).order_by(Lead.created_at.desc())).all())

    def get(self, lead_id: int) -> Lead | None:
        return self.session.get(Lead, lead_id)

    def delete_many(self, ids: list[int]) -> int:
        count = 0
        for lead_id in ids:
            lead = self.get(lead_id)
            if lead:
                self.session.delete(lead)
                count += 1
        self.commit()
        return count

    def commit(self) -> None:
        self.session.commit()

