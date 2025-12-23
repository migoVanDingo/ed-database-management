"""Add label_ontology and link to dataset

Revision ID: 14bd1cb292f1
Revises: 516e6e9acdc5
Create Date: 2025-12-23 11:50:27.182646

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "14bd1cb292f1"
down_revision: Union[str, Sequence[str], None] = "516e6e9acdc5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ─────────────────────────────────────────
    # Safety: drop stray label_ontology if it exists
    # (in case metadata.create_all created it early)
    # ─────────────────────────────────────────
    op.execute("DROP TABLE IF EXISTS label_ontology CASCADE;")

    # ─────────────────────────────────────────
    # Create label_ontology table
    # ─────────────────────────────────────────
    op.create_table(
        "label_ontology",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        # If your BaseModel usually has timestamps, you can add them later;
        # keeping it minimal for now.
        sa.Column("datastore_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "source",
            sa.String(),
            nullable=False,
            server_default="label-studio",
        ),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.ForeignKeyConstraint(["datastore_id"], ["datastore.id"]),
    )

    op.create_index(
        "ix_label_ontology_datastore_id",
        "label_ontology",
        ["datastore_id"],
        unique=False,
    )

    # ─────────────────────────────────────────
    # Add label_ontology_id column to dataset
    # ─────────────────────────────────────────
    op.add_column(
        "dataset",
        sa.Column("label_ontology_id", sa.String(), nullable=True),
    )

    op.create_foreign_key(
        "fk_dataset_label_ontology",
        "dataset",
        "label_ontology",
        ["label_ontology_id"],
        ["id"],
    )


def downgrade():
    # Drop FK + column on dataset
    op.drop_constraint(
        "fk_dataset_label_ontology",
        "dataset",
        type_="foreignkey",
    )
    op.drop_column("dataset", "label_ontology_id")

    # Drop label_ontology table + index
    op.drop_index(
        "ix_label_ontology_datastore_id",
        table_name="label_ontology",
    )
    op.drop_table("label_ontology")
