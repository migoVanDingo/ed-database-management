"""add unique index for dataset_file_link

Revision ID: f442ef3ceae1
Revises: cf7468594358
Create Date: 2025-12-27 11:08:24.198922

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f442ef3ceae1"
down_revision: Union[str, Sequence[str], None] = "cf7468594358"
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
