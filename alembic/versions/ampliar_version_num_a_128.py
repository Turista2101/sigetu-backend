"""
Migración Alembic para ampliar el tamaño de version_num en alembic_version a VARCHAR(128)
"""
from alembic import op
import sqlalchemy as sa

# Reemplaza estos valores por los correctos según tu historial
revision = 'ampliar_version_num_a_128'
down_revision = None  # Si tienes un head anterior, pon su revision aquí
depends_on = None
branch_labels = None

def upgrade():
    op.alter_column('alembic_version', 'version_num',
        existing_type=sa.VARCHAR(length=32),
        type_=sa.VARCHAR(length=128),
        existing_nullable=False)

def downgrade():
    op.alter_column('alembic_version', 'version_num',
        existing_type=sa.VARCHAR(length=128),
        type_=sa.VARCHAR(length=32),
        existing_nullable=False)
