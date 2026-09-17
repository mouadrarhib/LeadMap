"""Initial LeadMap schema."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("place_id", sa.String(255), unique=True),
        sa.Column("business_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(255)),
        sa.Column("address", sa.Text()),
        sa.Column("city", sa.String(255)),
        sa.Column("phone", sa.String(80)),
        sa.Column("website", sa.Text()),
        sa.Column("domain", sa.String(255)),
        sa.Column("email", sa.String(320)),
        sa.Column("maps_url", sa.Text()),
        sa.Column("rating", sa.Float()),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("opportunity_score", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(40), nullable=False, server_default="NEW"),
        sa.Column("source", sa.String(80), nullable=False, server_default="GOOGLE_PLACES"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True)),
    )
    for name, column in [
        ("ix_leads_place_id", "place_id"), ("ix_leads_business_name", "business_name"),
        ("ix_leads_city", "city"), ("ix_leads_phone", "phone"), ("ix_leads_domain", "domain"),
        ("ix_leads_email", "email"), ("ix_leads_score", "score"), ("ix_leads_status", "status"),
    ]:
        op.create_index(name, "leads", [column])
    op.create_index("ix_leads_domain_email", "leads", ["domain", "email"])

    op.create_table(
        "email_campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("subject_template", sa.String(500), nullable=False),
        sa.Column("body_template", sa.Text(), nullable=False),
        sa.Column("daily_limit", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "email_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("email_campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient", sa.String(320), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("gmail_message_id", sa.String(255)),
        sa.Column("status", sa.String(40), nullable=False, server_default="DRAFT"),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    for name, column in [
        ("ix_email_messages_lead_id", "lead_id"), ("ix_email_messages_campaign_id", "campaign_id"),
        ("ix_email_messages_recipient", "recipient"), ("ix_email_messages_status", "status"),
        ("ix_email_messages_sent_at", "sent_at"),
    ]:
        op.create_index(name, "email_messages", [column])
    op.create_table(
        "suppressions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("reason", sa.String(255), nullable=False, server_default="Opted out"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_suppressions_email", "suppressions", ["email"])


def downgrade() -> None:
    op.drop_table("suppressions")
    op.drop_table("email_messages")
    op.drop_table("email_campaigns")
    op.drop_table("leads")

