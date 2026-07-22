"""Add structured presentation metadata to messages.

Revision ID: 8f31d75b42ae
Revises: c3a7f4e2b891
Create Date: 2026-07-22
"""
from alembic import op
import sqlalchemy as sa

revision = "8f31d75b42ae"
down_revision = "c3a7f4e2b891"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("messages", sa.Column("presentation", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("messages", "presentation")
