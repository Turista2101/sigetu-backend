
"""Permitir student_id nulo en appointment_history

Revision ID: 20260315_permitir_student_id_nulo
Revises: fa07559ca85f
Create Date: 2026-03-15
"""

revision = '20260315_permitir_student_id_nulo'
down_revision = 'fa07559ca85f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column('appointment_history', 'student_id', existing_type=sa.INTEGER(), nullable=True)

def downgrade():
    op.alter_column('appointment_history', 'student_id', existing_type=sa.INTEGER(), nullable=False)
