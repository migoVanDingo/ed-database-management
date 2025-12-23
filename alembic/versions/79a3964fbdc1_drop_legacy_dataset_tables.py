"""Drop legacy dataset tables

Revision ID: 79a3964fbdc1
Revises: 68a867090400
Create Date: 2025-12-23 10:39:12.206363

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "79a3964fbdc1"
down_revision: Union[str, Sequence[str], None] = "68a867090400"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop legacy tables we no longer want to use.
    # Order matters: drop link tables before datafile.
    op.drop_table("dataset_version_file_link")
    op.drop_table("dataset_file_link")
    op.drop_table("datafile")


def downgrade():
    # If you don't care about downgrades, you can leave this as a stub.
    # Implementing full recreation isn't worth it for legacy tables.
    pass
