"""Middleware for Telegram bot: logging, throttling."""

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    """Log incoming updates and measure processing time."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Wrap handler with logging and timing."""
        started = time.monotonic()

        if isinstance(event, Update):
            update_info = self._extract_update_info(event)
            logger.info(f"Incoming update: {update_info}")

        try:
            result = await handler(event, data)
            elapsed_ms = (time.monotonic() - started) * 1000
            logger.debug(f"Update processed in {elapsed_ms:.1f}ms")
            return result
        except Exception:
            elapsed_ms = (time.monotonic() - started) * 1000
            logger.exception(f"Update failed after {elapsed_ms:.1f}ms")
            raise

    @staticmethod
    def _extract_update_info(update: Update) -> str:
        """Extract human-readable update description."""
        if update.message:
            user_id = update.message.from_user.id if update.message.from_user else "?"
            text = (update.message.text or update.message.caption or "")[:50]
            return f"msg from={user_id} text={text!r}"
        if update.callback_query:
            user_id = update.callback_query.from_user.id
            return f"callback from={user_id} data={update.callback_query.data!r}"
        return f"update_id={update.update_id}"
