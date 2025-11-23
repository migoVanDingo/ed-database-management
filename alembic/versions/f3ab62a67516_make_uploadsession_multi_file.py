"""Make UploadSession multi-file

Revision ID: f3ab62a67516
Revises: 6a0ec1b19c59
Create Date: 2025-11-23 09:58:32.836047

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3ab62a67516"
down_revision: Union[str, Sequence[str], None] = "6a0ec1b19c59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1) Add upload_session_id to file
    op.add_column(
        "file",
        sa.Column("upload_session_id", sa.String(), nullable=True),
    )
    op.create_index(
        "ix_file_upload_session_id",
        "file",
        ["upload_session_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_file_upload_session_id_upload_session",
        "file",
        "upload_session",
        ["upload_session_id"],
        ["id"],
    )

    # 2) Backfill upload_session_id on file from old 1:1 mapping
    #    (upload_session.file_id -> file.id)
    op.execute(
        """
        UPDATE file
        SET upload_session_id = us.id
        FROM upload_session AS us
        WHERE us.file_id = file.id
        """
    )

    # 3) Drop the old 1:1-style columns from upload_session

    # Drop FK constraint from upload_session.file_id -> file.id
    op.drop_constraint(
        "upload_session_file_id_fkey",
        "upload_session",
        type_="foreignkey",
    )

    # Now drop the columns that made UploadSession 1:1 with File.
    op.drop_column("upload_session", "file_id")
    op.drop_column("upload_session", "filename")
    op.drop_column("upload_session", "content_type")
    op.drop_column("upload_session", "size_estimate")
    op.drop_column("upload_session", "object_key")


def downgrade():
    # NOTE: This downgrade restores the schema, but it cannot perfectly
    #       reconstruct the original 1:1 mapping if multiple files now
    #       point to the same upload_session. It will leave file_id NULL.

    # 1) Re-add old columns to upload_session

    op.add_column(
        "upload_session",
        sa.Column("object_key", sa.String(), nullable=False),
    )
    op.add_column(
        "upload_session",
        sa.Column("size_estimate", sa.Integer(), nullable=True),
    )
    op.add_column(
        "upload_session",
        sa.Column("content_type", sa.String(), nullable=False),
    )
    op.add_column(
        "upload_session",
        sa.Column("filename", sa.String(), nullable=False),
    )
    op.add_column(
        "upload_session",
        sa.Column("file_id", sa.String(), nullable=True),
    )

    # Recreate FK from upload_session.file_id -> file.id
    op.create_foreign_key(
        "upload_session_file_id_fkey",
        "upload_session",
        "file",
        ["file_id"],
        ["id"],
    )

    # 3) Drop the new FK + index + column from file

    op.drop_constraint(
        "fk_file_upload_session_id_upload_session",
        "file",
        type_="foreignkey",
    )
    op.drop_index("ix_file_upload_session_id", table_name="file")
    op.drop_column("file", "upload_session_id")
