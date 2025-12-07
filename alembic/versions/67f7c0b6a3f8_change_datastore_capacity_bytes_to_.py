"""change datastore capacity_bytes to bigint

Revision ID: 67f7c0b6a3f8
Revises: 72cb4d53717c
Create Date: 2025-12-07 10:44:02.945372

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "67f7c0b6a3f8"
down_revision: Union[str, Sequence[str], None] = "72cb4d53717c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "datastore",
        "capacity_bytes",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        "datastore",
        "capacity_bytes",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
