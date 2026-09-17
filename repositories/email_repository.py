from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.models import EmailCampaign, EmailMessage, Suppression


class EmailRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_campaign(self, name: str, subject: str, body: str, daily_limit: int) -> EmailCampaign:
        campaign = EmailCampaign(
            name=name, subject_template=subject, body_template=body, daily_limit=daily_limit
        )
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        return campaign

    def create_message(
        self, campaign_id: int, lead_id: int, recipient: str, subject: str, body: str
    ) -> EmailMessage:
        message = EmailMessage(
            campaign_id=campaign_id,
            lead_id=lead_id,
            recipient=recipient,
            subject=subject,
            body=body,
            status="APPROVED",
        )
        self.session.add(message)
        self.session.commit()
        return message

    def approved_messages(self, campaign_id: int) -> list[EmailMessage]:
        return list(
            self.session.scalars(
                select(EmailMessage).where(
                    EmailMessage.campaign_id == campaign_id,
                    EmailMessage.status == "APPROVED",
                )
            ).all()
        )

    def sent_today(self) -> int:
        today = datetime.now(UTC).date()
        return int(
            self.session.scalar(
                select(func.count()).select_from(EmailMessage).where(
                    EmailMessage.status == "SENT",
                    func.date(EmailMessage.sent_at) == today,
                )
            )
            or 0
        )

    def is_suppressed(self, email: str) -> bool:
        return self.session.scalar(select(Suppression.id).where(Suppression.email == email.lower())) is not None

    def suppress(self, email: str, reason: str = "Do not contact") -> None:
        value = email.strip().lower()
        if value and not self.is_suppressed(value):
            self.session.add(Suppression(email=value, reason=reason))
            self.session.commit()

    def was_sent(self, email: str) -> bool:
        return self.session.scalar(
            select(EmailMessage.id).where(
                EmailMessage.recipient == email.lower(), EmailMessage.status == "SENT"
            )
        ) is not None

    def mark_sent(self, message: EmailMessage, gmail_id: str, sent_at: datetime) -> None:
        message.gmail_message_id = gmail_id
        message.sent_at = sent_at
        message.status = "SENT"
        message.lead.status = "SENT"
        message.lead.last_contacted_at = sent_at
        self.session.commit()
