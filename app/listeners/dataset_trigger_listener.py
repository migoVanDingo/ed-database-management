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


def map_dataset_event(payload: str) -> PubSubEvent:
    p = json.loads(payload)
    event_name = (p.get("event_name") or "DATASET_FILES_CHANGED").upper()

    et = (
        _et_or_none(event_name)
        or _et_or_none("DB_ROW_CHANGED")
        or next(iter(EventType))
    )
    return PubSubEvent(event_type=et, payload=p)


async def listen_to_dataset_files_changes():
    await listen_to_pg_channel(
        dsn=settings.asyncpg_dsn,
        pg_channel="dataset_files_changed",
        pubsub_topic="dataset:updated",
        event_mapper=map_dataset_event,
    )
