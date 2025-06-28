import asyncio
from typing import List, Type
from sqlmodel import SQLModel
from platform_common.db.engine import engine  # adjust the import if needed
from platform_common.models.base import Base  # your models should inherit from this

# Import all models here so their metadata is registered
# from your_project.models import User, Project  # example; import all your models


def rebuild_models(models: List[Type[SQLModel]]):
    for model in models:
        model.model_rebuild()


async def init_db():
    rebuild_models([])  # Replace with your actual model imports

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Database initialized.")


if __name__ == "__main__":
    asyncio.run(init_db())
