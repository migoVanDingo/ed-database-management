"""Add annotation_artifact table

Revision ID: 62559db29ad8
Revises: 14bd1cb292f1
Create Date: 2025-12-23 11:51:18.726952

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "62559db29ad8"
down_revision: Union[str, Sequence[str], None] = "14bd1cb292f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Safety: if something already created this (e.g. metadata.create_all),
    # drop it so we can recreate under Alembic.
    op.execute("DROP TABLE IF EXISTS annotation_artifact CASCADE;")

    op.create_table(
        "annotation_artifact",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("dataset_id", sa.String(), nullable=False),
        sa.Column("datastore_id", sa.String(), nullable=False),
        sa.Column("file_id", sa.String(), nullable=False),
        sa.Column("label_ontology_id", sa.String(), nullable=True),
        sa.Column("label_studio_project_id", sa.String(), nullable=True),
        sa.Column("export_run_id", sa.String(), nullable=True),
        sa.Column(
            "source",
            sa.String(),
            nullable=False,
            server_default="label-studio",
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="pending_ingest",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.ForeignKeyConstraint(["datastore_id"], ["datastore.id"]),
        sa.ForeignKeyConstraint(["file_id"], ["file.id"]),
        sa.ForeignKeyConstraint(["label_ontology_id"], ["label_ontology.id"]),
    )

    op.create_index(
        "ix_annotation_artifact_dataset_id",
        "annotation_artifact",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "ix_annotation_artifact_datastore_id",
        "annotation_artifact",
        ["datastore_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_annotation_artifact_datastore_id",
        table_name="annotation_artifact",
    )
    op.drop_index(
        "ix_annotation_artifact_dataset_id",
        table_name="annotation_artifact",
    )
    op.drop_table("annotation_artifact")
