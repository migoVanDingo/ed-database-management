import asyncio
from typing import Optional

from platform_common.config.settings import get_settings
from platform_common.db.session import get_session  # your async session generator
from platform_common.db.dal.event_outbox_dal import EventOutboxDAL
from platform_common.pubsub.event import PubSubEvent
from platform_common.pubsub.factory import get_publisher
from platform_common.utils.enums import EventType
from platform_common.logging.logging import get_logger

logger = get_logger("outbox_listener")
settings = get_settings()


def _safe_event_type(name: str, fallback: str = "DB_ROW_CHANGED"):
    try:
        return getattr(EventType, name)
    except Exception:
        try:
            return getattr(EventType, fallback)
        except Exception:
            return next(iter(EventType))


def topic_for_entity(entity_type: str) -> str:
    # match your existing topic conventions
    if entity_type == "dataset":
        return "dataset:updated"
    if entity_type == "file":
        return "file:status"
    if entity_type == "upload_session":
        return "upload_session:status"
    return "db:row_changed"


def event_for_outbox(entity_type: str, payload: dict) -> PubSubEvent:
    # Keep it simple for now
    if entity_type == "dataset":
        et = _safe_event_type("DATASET_UPDATED")
    elif entity_type == "file":
        et = _safe_event_type("FILE_STATUS_CHANGED")
    else:
        et = _safe_event_type("DB_ROW_CHANGED")
    return PubSubEvent(event_type=et, payload=payload)


async def listen_to_outbox_events(
    *,
    interval_seconds: float = 0.5,
    idle_sleep_seconds: float = 1.5,
    batch_size: int = 200,
    entity_type_filter: Optional[str] = None,
):
    """
    Drains event_outbox and republishes to Redis.

    Safe to run multiple replicas because claim_batch uses SKIP LOCKED.
    """
    publisher = get_publisher()

    while True:
        try:
            any_processed = False

            async for session in get_session():
                dal = EventOutboxDAL(session)
                rows = await dal.claim_batch(limit=batch_size)

                if entity_type_filter:
                    rows = [r for r in rows if r["entity_type"] == entity_type_filter]

                if not rows:
                    break

                processed_ids: list[int] = []

                for r in rows:
                    try:
                        p = dict(r.get("payload") or {})
                        p.update(
                            {
                                "outbox_id": r["id"],
                                "entity_type": r["entity_type"],
                                "entity_id": r["entity_id"],
                                "datastore_id": r.get("datastore_id"),
                                "upload_session_id": r.get("upload_session_id"),
                                "old_status": r.get("old_status"),
                                "new_status": r.get("new_status"),
                                "occurred_at": r["occurred_at"].isoformat(),
                            }
                        )

                        topic = topic_for_entity(r["entity_type"])
                        event = event_for_outbox(r["entity_type"], p)

                        await publisher.publish(topic, event)
                        processed_ids.append(r["id"])
                        any_processed = True

                    except Exception as e:
                        logger.exception("Failed processing outbox id=%s", r["id"])
                        await dal.mark_error(id=r["id"], error=str(e))

                await dal.mark_processed(ids=processed_ids)

                # claim next batch in a new session tick
                break

            await asyncio.sleep(
                interval_seconds if any_processed else idle_sleep_seconds
            )

        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Outbox poller crashed; retrying")
            await asyncio.sleep(2.0)
