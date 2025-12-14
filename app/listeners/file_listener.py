# app/pubsub/file_listener.py

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


def map_file_status_event(payload: str) -> PubSubEvent:
    """
    Map the raw JSON payload from the Postgres trigger into a PubSubEvent
    that will be published to Redis.
    """
    p = json.loads(payload)

    # If we later decide to add event_name to the payload, prefer that.
    event_name = (p.get("event_name") or "FILE_STATUS_CHANGED").upper()

    et = _et_or_none(event_name)
    if et is None:
        et = _et_or_none("DB_ROW_CHANGED")
    if et is None:
        et = next(iter(EventType))

    return PubSubEvent(event_type=et, payload=p)


async def listen_to_file_status_changes():
    """
    LISTEN on the Postgres channel 'file_status_changed'
    and publish events to Redis on topic 'file:status'.
    """
    await listen_to_pg_channel(
        dsn=settings.asyncpg_dsn,
        pg_channel="file_status_changed",  # 👈 matches pg_notify
        pubsub_topic="file:status",  # 👈 choose a topic name
        event_mapper=map_file_status_event,
    )
