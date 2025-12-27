# app/main.py
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from platform_common.config.settings import get_settings
from platform_common.middleware.request_id_middleware import RequestIDMiddleware
from platform_common.exception_handling.handlers import add_exception_handlers
from app.db.init_db import init_db
from app.db.seed_dev_data import seed_dev_data
from app.listeners.user_trigger_listener import listen_to_user_changes
from app.debug.debug_subscriber import start_debug_subscriber  # see notes below
from app.listeners.upload_session_trigger_listener import (
    listen_to_upload_session_changes,
)
from app.listeners.file_listener import listen_to_file_status_changes
from app.listeners.outbox_poller import listen_to_outbox_events
from app.listeners.dataset_trigger_listener import listen_to_dataset_files_changes

settings = get_settings()  # single source of truth


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"databaseURL (SQLAlchemy): {settings.database_url}")
    try:
        print(f"databaseURL (asyncpg):  {settings.asyncpg_dsn}")
    except Exception:
        pass

    await init_db()
    await seed_dev_data()

    # Start PG -> Redis listeners
    app.state.user_listener_task = asyncio.create_task(listen_to_user_changes())
    app.state.outbox_listener_task = asyncio.create_task(
        listen_to_outbox_events(
            entity_type_filter="dataset"
        )  # start with datasets only
    )
    app.state.upload_session_listener_task = asyncio.create_task(
        listen_to_upload_session_changes()
    )
    app.state.file_status_listener_task = asyncio.create_task(
        listen_to_file_status_changes()
    )
    app.state.dataset_listener_task = asyncio.create_task(
        listen_to_dataset_files_changes()
    )

    # Optional debug subscriber
    app.state.debug_task = None
    if getattr(settings, "DEBUG_PUBSUB_PRINT", False):
        app.state.debug_task = asyncio.create_task(start_debug_subscriber())

    try:
        yield
    finally:
        # user listener
        app.state.user_listener_task.cancel()
        try:
            await app.state.user_listener_task
        except asyncio.CancelledError:
            pass

        # upload_session listener
        app.state.upload_session_listener_task.cancel()
        try:
            await app.state.upload_session_listener_task
        except asyncio.CancelledError:
            pass

        # file_status listener
        app.state.file_status_listener_task.cancel()
        try:
            await app.state.file_status_listener_task
        except asyncio.CancelledError:
            pass

        if app.state.debug_task:
            app.state.debug_task.cancel()
            try:
                await app.state.debug_task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="ed-database-management", lifespan=lifespan)
app.add_middleware(RequestIDMiddleware)
add_exception_handlers(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}
