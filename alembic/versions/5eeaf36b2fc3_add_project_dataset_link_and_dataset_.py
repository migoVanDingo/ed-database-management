"""Add project_dataset_link and dataset_file_link

Revision ID: 5eeaf36b2fc3
Revises: 6b0728a1d712
Create Date: 2025-12-23 11:24:28.682335

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5eeaf36b2fc3"
down_revision: Union[str, Sequence[str], None] = "6b0728a1d712"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ─────────────────────────────────────────
    # Safety: drop stray tables if they exist
    # (e.g., created by metadata.create_all before migrations run)
    # ─────────────────────────────────────────
    op.execute("DROP TABLE IF EXISTS project_dataset_link CASCADE;")
    op.execute("DROP TABLE IF EXISTS dataset_file_link CASCADE;")

    # ─────────────────────────────────────────
    # project_dataset_link
    # ─────────────────────────────────────────
    op.create_table(
        "project_dataset_link",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("dataset_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("default_version_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.ForeignKeyConstraint(["default_version_id"], ["dataset_version.id"]),
    )
    op.create_index(
        "ix_project_dataset_link_project_id",
        "project_dataset_link",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_project_dataset_link_dataset_id",
        "project_dataset_link",
        ["dataset_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_project_dataset_link_project_dataset",
        "project_dataset_link",
        ["project_id", "dataset_id"],
    )

    # ─────────────────────────────────────────
    # dataset_file_link  (new version, points to file)
    # ─────────────────────────────────────────
    op.create_table(
        "dataset_file_link",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("dataset_id", sa.String(), nullable=False),
        sa.Column("file_id", sa.String(), nullable=False),
        sa.Column(
            "role",
            sa.String(),
            nullable=True,
            comment="input | annotation | derived | etc.",
        ),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.ForeignKeyConstraint(["file_id"], ["file.id"]),
    )

    op.create_index(
        "ix_dataset_file_link_dataset_id",
        "dataset_file_link",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "ix_dataset_file_link_file_id",
        "dataset_file_link",
        ["file_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_dataset_file_link_dataset_file",
        "dataset_file_link",
        ["dataset_id", "file_id"],
    )


def downgrade():
    # Reverse order: drop constraints/tables we just created

    op.drop_constraint(
        "uq_dataset_file_link_dataset_file",
        "dataset_file_link",
        type_="unique",
    )
    op.drop_index("ix_dataset_file_link_file_id", table_name="dataset_file_link")
    op.drop_index("ix_dataset_file_link_dataset_id", table_name="dataset_file_link")
    op.drop_table("dataset_file_link")

    op.drop_constraint(
        "uq_project_dataset_link_project_dataset",
        "project_dataset_link",
        type_="unique",
    )
    op.drop_index(
        "ix_project_dataset_link_dataset_id",
        table_name="project_dataset_link",
    )
    op.drop_index(
        "ix_project_dataset_link_project_id",
        table_name="project_dataset_link",
    )
    op.drop_table("project_dataset_link")
