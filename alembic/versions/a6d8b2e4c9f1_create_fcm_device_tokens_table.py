"""create fcm device tokens table

Revision ID: a6d8b2e4c9f1
Revises: f7a2c9d1e4b3
Create Date: 2026-02-28 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6d8b2e4c9f1"
down_revision: Union[str, Sequence[str], None] = "f7a2c9d1e4b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fcm_device_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_fcm_device_tokens_token"),
    )

    op.create_index(op.f("ix_fcm_device_tokens_id"), "fcm_device_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_fcm_device_tokens_user_id"), "fcm_device_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fcm_device_tokens_user_id"), table_name="fcm_device_tokens")
    op.drop_index(op.f("ix_fcm_device_tokens_id"), table_name="fcm_device_tokens")
    op.drop_table("fcm_device_tokens")
