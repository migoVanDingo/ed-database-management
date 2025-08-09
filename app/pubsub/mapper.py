# mapper.py
import json
from platform_common.pubsub.event import PubSubEvent
from platform_common.utils.enums import (
    EventType,
)  # e.g., DB_ROW_CHANGED or USER_CHANGED


def map_user_change(payload: str) -> PubSubEvent:
    p = json.loads(payload)
    return PubSubEvent(
        event_type=EventType.DB_ROW_CHANGED,  # or EventType.USER_CHANGED if you have it
        payload={
            "table": p["table"],  # "user"
            "operation": p["operation"],  # INSERT | UPDATE | DELETE
            "data": p.get("data"),  # may be None
            "old_data": p.get("old_data"),  # may be None
        },
    )
