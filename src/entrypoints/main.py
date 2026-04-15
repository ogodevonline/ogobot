"""Main entry point for S.E.A.C."""

import asyncio
import os

from dotenv import load_dotenv
from loguru import logger

from src.infrastructure.db.session import init_db
from src.infrastructure.logging.config import setup_logging
from src.entrypoints.telegram_bot import start_bot

load_dotenv()


async def main() -> None:
    """Main entry point"""
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))

    logger.info("Starting S.E.A.C.")

    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./seac.db")
    await init_db(db_url)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return

    await start_bot(bot_token)


if __name__ == "__main__":
    asyncio.run(main())
