# app/db/seed_dev_data.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from platform_common.db.engine import get_engine
from platform_common.models.user import User
from platform_common.models.datastore import Datastore

SYSTEM_USER_ID = "USR123SYSTEM456USER789"
TEST_DATASTORE_ID = "test-datastore-id"


async def seed_dev_data() -> None:
    """
    Seed a system user + test datastore for local upload tests.
    Safe to run multiple times (id-based upsert).
    """
    engine = await get_engine()

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # ---------- Seed system user ----------
        result = await session.execute(select(User).where(User.id == SYSTEM_USER_ID))
        system_user = result.scalar_one_or_none()

        if system_user is None:
            system_user = User(
                id=SYSTEM_USER_ID,
                email="system.user@example.com",
                username="system-user",
                idp_uid="system-user-idp",  # any stable idp UID you like
                is_verified=True,
                status="active",
            )
            session.add(system_user)

        # ---------- Seed test datastore ----------
        result = await session.execute(
            select(Datastore).where(Datastore.id == TEST_DATASTORE_ID)
        )
        datastore = result.scalar_one_or_none()

        if datastore is None:
            datastore = Datastore(
                id=TEST_DATASTORE_ID,
                name="Test Datastore",
                description="Seeded for local upload tests",
                type="generic",
                owner_id=SYSTEM_USER_ID,
                owner_type="user",
                user_id=SYSTEM_USER_ID,
                organization_id=None,
            )
            session.add(datastore)

        await session.commit()
