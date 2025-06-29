from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.init_db import init_db
from platform_common.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"databaseURL: {settings.database_url}")
    # Startup logic
    await init_db()

    yield  # The app runs here

    # Shutdown logic (optional)
    # e.g., close connections or cleanup resources


app = FastAPI(title="ed-database-management", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}
