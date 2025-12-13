import json

from platform_common.config.settings import get_settings
from platform_common.pubsub.trigger_listener import listen_to_pg_channel
from platform_common.pubsub.event import PubSubEvent
from platform_common.utils.enums import EventType

settings = get_settings()


def _et_or_none(name: str):
    try:
        return getattr(EventType, name)
    except AttributeError:
        return None


def map_upload_session_event(payload: str) -> PubSubEvent:
    """
    Map the raw JSON payload from the Postgres trigger into a PubSubEvent
    that will be published to Redis.
    """
    p = json.loads(payload)

    # If we ever add event_name in the trigger payload, prefer that.
    # For now, default to a descriptive name.
    event_name = (p.get("event_name") or "UPLOAD_SESSION_STATUS_CHANGED").upper()

    et = _et_or_none(event_name)
    if et is None:
        # Fallback to a generic DB-row-changed event if you have it
        et = _et_or_none("DB_ROW_CHANGED")
    if et is None:
        # Absolute fallback: first enum member so we don't crash
        et = next(iter(EventType))

    return PubSubEvent(event_type=et, payload=p)


async def listen_to_upload_session_changes():
    """
    LISTEN on the Postgres channel 'upload_session_status_changed'
    and publish events to Redis on topic 'upload_session:status'.
    """
    await listen_to_pg_channel(
        dsn=settings.asyncpg_dsn,
        pg_channel="upload_session_status_changed",
        pubsub_topic="upload_session:status",
        event_mapper=map_upload_session_event,
    )
