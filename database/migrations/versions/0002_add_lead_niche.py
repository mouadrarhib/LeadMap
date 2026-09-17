"""Add a persistent niche list to leads."""

from alembic import op
import sqlalchemy as sa

revision = "0002_lead_niche"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("niche", sa.String(255), nullable=True, server_default="Uncategorized"),
    )
    op.execute(
        """
        UPDATE leads
        SET niche = CASE
            WHEN category = 'Car Rental Agency' THEN 'Car rental agencies'
            ELSE 'Dentists'
        END
        """
    )
    op.alter_column("leads", "niche", nullable=False)
    op.create_index("ix_leads_niche", "leads", ["niche"])


def downgrade() -> None:
    op.drop_index("ix_leads_niche", table_name="leads")
    op.drop_column("leads", "niche")

