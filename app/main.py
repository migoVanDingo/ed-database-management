# app/main.py
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from platform_common.config.settings import get_settings
from app.db.init_db import init_db
from app.listeners.user_trigger_listener import listen_to_user_changes
from app.debug.debug_subscriber import start_debug_subscriber  # see notes below

settings = get_settings()  # single source of truth


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"databaseURL (SQLAlchemy): {settings.database_url}")
    # optional: verify the asyncpg DSN you're actually using in the listener
    try:
        print(f"databaseURL (asyncpg):  {settings.asyncpg_dsn}")
    except Exception:
        pass

    await init_db()

    # Start the PG -> Redis listener
    app.state.user_listener_task = asyncio.create_task(listen_to_user_changes())

    # Optional: in-process debug subscriber so you see events in the same logs
    app.state.debug_task = None
    if getattr(settings, "DEBUG_PUBSUB_PRINT", False):
        # EITHER: if your helper reads settings internally (no args):
        app.state.debug_task = asyncio.create_task(start_debug_subscriber())
        # OR, if your helper expects a URL param, pass the effective one:
        # app.state.debug_task = asyncio.create_task(
        #     start_debug_subscriber(settings.redis_url_effective)
        # )

    try:
        yield
    finally:
        app.state.user_listener_task.cancel()
        try:
            await app.state.user_listener_task
        except asyncio.CancelledError:
            pass

        if app.state.debug_task:
            app.state.debug_task.cancel()
            try:
                await app.state.debug_task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="ed-database-management", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}
