"""enable pgcrypto extension

Revision ID: b2225ec62883
Revises: 04274c8e89f6
Create Date: 2025-12-24 10:27:13.929045

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2225ec62883"
down_revision: Union[str, Sequence[str], None] = "04274c8e89f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')


def downgrade():
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
