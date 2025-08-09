# app/debug/debug_subscriber.py (in ed-database-management)
import json
from platform_common.config.settings import get_settings
from platform_common.logging.logging import get_logger
from platform_common.pubsub.factory import get_subscriber

logger = get_logger("debug_subscriber")
settings = get_settings()


async def start_debug_subscriber():
    sub = get_subscriber()

    async def printer(event):
        logger.info(
            "[debug-subscriber] %s",
            json.dumps(
                {"event_type": str(event.event_type), "payload": event.payload},
                default=str,
            ),
        )

    await sub.subscribe(
        {
            "user:changes": {
                "USER_CREATED": printer,
                "USER_UPDATED": printer,
                "USER_DELETED": printer,
                "DB_ROW_CHANGED": printer,  # safe catch-all
            }
        }
    )
