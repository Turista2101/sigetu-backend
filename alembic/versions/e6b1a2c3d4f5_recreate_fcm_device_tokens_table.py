"""recreate fcm device tokens table

Revision ID: e6b1a2c3d4f5
Revises: c3d4e5f6a7b9
Create Date: 2026-03-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6b1a2c3d4f5"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fcm_device_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_fcm_device_tokens_token"),
        sa.UniqueConstraint("user_id", "device_id", name="uq_fcm_device_tokens_user_device"),
    )

    op.create_index(op.f("ix_fcm_device_tokens_id"), "fcm_device_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_fcm_device_tokens_user_id"), "fcm_device_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fcm_device_tokens_user_id"), table_name="fcm_device_tokens")
    op.drop_index(op.f("ix_fcm_device_tokens_id"), table_name="fcm_device_tokens")
    op.drop_table("fcm_device_tokens")
