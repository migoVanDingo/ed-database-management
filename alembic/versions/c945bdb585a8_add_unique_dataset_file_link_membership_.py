"""add unique dataset_file_link membership index

Revision ID: c945bdb585a8
Revises: 4d2098a5022e
Create Date: 2025-12-27 11:26:58.786707

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c945bdb585a8"
down_revision: Union[str, Sequence[str], None] = "4d2098a5022e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_dataset_file_link_dataset_file
        ON dataset_file_link (dataset_id, file_id);
    """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS uq_dataset_file_link_dataset_file;
    """
    )
