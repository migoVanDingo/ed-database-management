"""add capacity_bytes to datastore

Revision ID: 72cb4d53717c
Revises: f3ab62a67516
Create Date: 2025-12-07 08:02:49.457732

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "72cb4d53717c"
down_revision: Union[str, Sequence[str], None] = "f3ab62a67516"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "datastore",
        sa.Column(
            "capacity_bytes",
            sa.BigInteger(),
            nullable=True,
            server_default=sa.text("10737418240"),  # 10 GB
        ),
    )

    # If you want existing rows to be explicitly set (optional but nice):
    op.execute(
        "UPDATE datastore SET capacity_bytes = 10737418240 WHERE capacity_bytes IS NULL"
    )


def downgrade():
    op.drop_column("datastore", "capacity_bytes")
