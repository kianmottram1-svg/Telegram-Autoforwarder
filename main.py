import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SOURCE_CHAT = os.environ["SOURCE_CHAT"]
DEST_CHAT = os.environ["DEST_CHAT"]

SESSION_FILE = "session"


async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

    # Connect using the pre-authenticated session — no interactive prompts.
    await client.connect()

    if not await client.is_user_authorized():
        logger.error(
            "Session is not authorized. Re-authenticate locally and commit "
            "the updated session.session file."
        )
        raise RuntimeError("Telegram session is not authorized")

    me = await client.get_me()
    logger.info("Logged in as %s (id=%s)", me.username or me.first_name, me.id)

    source = await client.get_entity(SOURCE_CHAT)
    dest = await client.get_entity(DEST_CHAT)
    logger.info(
        "Forwarding messages from '%s' → '%s'",
        getattr(source, "title", SOURCE_CHAT),
        getattr(dest, "title", DEST_CHAT),
    )

    @client.on(events.NewMessage(chats=source))
    async def handler(event):
        try:
            await client.forward_messages(dest, event.message)
            logger.info("Forwarded message id=%s", event.message.id)
        except Exception as exc:
            logger.error("Failed to forward message id=%s: %s", event.message.id, exc)

    logger.info("Listening for new messages…")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
