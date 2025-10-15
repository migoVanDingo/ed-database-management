import asyncio
import subprocess
from typing import List, Type
from sqlmodel import SQLModel
from platform_common.db.engine import get_engine  # adjust the import if needed
from platform_common.models.annotation import Annotation
from platform_common.models.audit_log import AuditLog
from platform_common.models.datafile import DataFile
from platform_common.models.dataset_file_link import DatasetFileLink
from platform_common.models.dataset_version_file_link import DatasetVersionFileLink
from platform_common.models.dataset_version import DatasetVersion
from platform_common.models.dataset import Dataset
from platform_common.models.datastore import Datastore
from platform_common.models.external_dataset import ExternalDataset
from platform_common.models.file import File
from platform_common.models.generated_file import GeneratedFile
from platform_common.models.organization_member import OrganizationMember
from platform_common.models.organization import Organization
from platform_common.models.project_dataset_link import ProjectDatasetLink
from platform_common.models.project import Project
from platform_common.models.role import Role
from platform_common.models.user_profile import UserProfile
from platform_common.models.user import User
from platform_common.models.notification import Notification
from platform_common.models.user_invite import UserInvite
from platform_common.models.user_session import UserSession
from platform_common.models.upload_session import UploadSession

__all__ = [
    "Annotation",
    "AuditLog",
    "DataFile",
    "DatasetFileLink",
    "DatasetVersionFileLink",
    "DatasetVersion",
    "Dataset",
    "Datastore",
    "ExternalDataset",
    "File",
    "GeneratedFile",
    "OrganizationMember",
    "Organization",
    "ProjectDatasetLink",
    "Project",
    "Role",
    "UserProfile",
    "User",
    "Notification",
    "UserInvite",
    "UserSession",
    "UploadSession",
]


# Import all models here so their metadata is registered
# from your_project.models import User, Project  # example; import all your models


def rebuild_models(models: List[Type[SQLModel]]):
    for model in models:
        model.model_rebuild()


async def init_db():
    rebuild_models(
        [
            Annotation,
            AuditLog,
            DataFile,
            DatasetFileLink,
            DatasetVersionFileLink,
            DatasetVersion,
            Dataset,
            Datastore,
            ExternalDataset,
            File,
            GeneratedFile,
            OrganizationMember,
            Organization,
            ProjectDatasetLink,
            Project,
            Role,
            UserProfile,
            User,
            Notification,
            UserInvite,
            UserSession,
            UploadSession,
        ]
    )

    engine = await get_engine()  # Ensure this function returns an async engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Database initialized.")

    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Database migrations applied.")


if __name__ == "__main__":
    asyncio.run(init_db())
