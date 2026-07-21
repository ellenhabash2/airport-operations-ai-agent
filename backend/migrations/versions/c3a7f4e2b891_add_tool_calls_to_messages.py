"""Add persisted tool calls to messages.

Revision ID: c3a7f4e2b891
Revises: 94df0a751919
Create Date: 2026-07-21

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3a7f4e2b891"
down_revision = "94df0a751919"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "messages",
        sa.Column("tool_calls", sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_column("messages", "tool_calls")
