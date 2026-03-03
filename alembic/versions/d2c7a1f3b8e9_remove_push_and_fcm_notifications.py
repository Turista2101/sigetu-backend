"""remove push and fcm notifications

Revision ID: d2c7a1f3b8e9
Revises: a6d8b2e4c9f1
Create Date: 2026-03-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d2c7a1f3b8e9"
down_revision: Union[str, Sequence[str], None] = "a6d8b2e4c9f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_fcm_device_tokens_user_id", table_name="fcm_device_tokens")
    op.drop_index("ix_fcm_device_tokens_id", table_name="fcm_device_tokens")
    op.drop_table("fcm_device_tokens")

    op.drop_index("ix_push_subscriptions_user_id", table_name="push_subscriptions")
    op.drop_index("ix_push_subscriptions_id", table_name="push_subscriptions")
    op.drop_table("push_subscriptions")


def downgrade() -> None:
    raise NotImplementedError("Downgrade not supported for notification rollback migration")
