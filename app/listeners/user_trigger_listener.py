# wherever your user listener lives (ed-database-management)
from platform_common.config.settings import get_settings
from platform_common.pubsub.trigger_listener import listen_to_pg_channel
from platform_common.pubsub.event import PubSubEvent
from platform_common.utils.enums import EventType
import json

settings = get_settings()


def _et_or_none(name: str):
    try:
        return getattr(EventType, name)
    except AttributeError:
        return None


def map_user_event(payload: str) -> PubSubEvent:
    p = json.loads(payload)
    event_name = (p.get("event_name") or "").upper()
    op = (p.get("operation") or "").upper()

    # Prefer explicit user events if they exist in your enum
    op_to_name = {
        "INSERT": "USER_CREATED",
        "UPDATE": "USER_UPDATED",
        "DELETE": "USER_DELETED",
    }
    desired_name = event_name or op_to_name.get(op)

    et = _et_or_none(desired_name) if desired_name else None
    if et is None:
        et = _et_or_none("DB_ROW_CHANGED")  # generic fallback if you have it
    if et is None:
        # absolute fallback: first enum member (guaranteed to exist)
        et = next(iter(EventType))

    return PubSubEvent(event_type=et, payload=p)


async def listen_to_user_changes():
    await listen_to_pg_channel(
        dsn=settings.asyncpg_dsn,  # ← critical fix
        pg_channel="user_changes",
        pubsub_topic="user:changes",
        event_mapper=map_user_event,
    )
