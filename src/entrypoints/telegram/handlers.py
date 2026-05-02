"""Telegram bot command and message handlers (router registration only)."""

from pathlib import Path

from aiogram import Router, types
from aiogram.filters import Command
from loguru import logger

from src.domain.value_objects import UserId
from src.entrypoints.telegram.formatters import (
    format_help,
    format_status,
    format_welcome,
)
from src.tools.registry import ToolRegistry

router = Router(name="handlers")

# Imported and used by bot.py for graph execution
GRAPH_TIMEOUT = 300.0


# --- Command handlers ---


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Handle /start command."""
    if not message.from_user:
        logger.warning("Received /start without from_user")
        return
    logger.info(f"User {message.from_user.id} issued /start")
    await message.answer(format_welcome())


@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """Handle /help command."""
    if not message.from_user:
        return
    logger.info(f"User {message.from_user.id} issued /help")
    await message.answer(format_help())


@router.message(Command("status"))
async def cmd_status(message: types.Message) -> None:
    """Handle /status command — show current task status."""
    if not message.from_user:
        return
    from src.entrypoints.telegram.bot import get_user_state

    user_id = UserId(message.from_user.id)
    state = get_user_state(user_id)
    if state is None:
        await message.answer("⚠️ Нет активной задачи. Создайте через /task.")
        return
    logger.info(f"User {user_id} requested status for task {state.task_id}")
    await message.answer(format_status(state))


@router.message(Command("tools"))
async def cmd_tools(message: types.Message) -> None:
    """Handle /tools command — list available tools."""
    if not message.from_user:
        return
    logger.info(f"User {message.from_user.id} issued /tools")

    registry = ToolRegistry(Path("src/tools"))
    tool_names = registry.list_tools()
    if not tool_names:
        await message.answer(
            "<b>🛠 Инструменты</b>\n\n"
            "<i>Нет зарегистрированных инструментов. "
            "Создайте задачу — и бот сгенерирует нужный код.</i>"
        )
        return
    tools_list = "\n".join(f"  🔧 {name}" for name in sorted(tool_names))
    await message.answer(
        f"<b>🛠 Доступные инструменты ({len(tool_names)}):</b>\n{tools_list}"
    )


@router.message(Command("task"))
async def cmd_task(message: types.Message) -> None:
    """Handle /task command — create and execute a task through the graph."""
    if not message.from_user:
        logger.warning("Received /task without from_user")
        return

    task_text = _extract_task_text(message.text or "")
    if not task_text:
        await message.answer(
            "⚠️ Укажите описание задачи после команды.\n"
            "Пример: <code>/task напиши калькулятор на Python</code>"
        )
        return

    from src.entrypoints.telegram.bot import run_user_task

    await run_user_task(message, task_text)


# --- Message handler ---


@router.message()
async def handle_message(message: types.Message) -> None:
    """Handle all non-command messages."""
    if not message.from_user:
        return
    if not message.text:
        logger.debug(f"Non-text message from {message.from_user.id}")
        await message.answer("⚠️ Неизвестный формат. Используйте /help для справки.")
        return
    if message.text.startswith("/"):
        logger.debug(f"Unknown command from {message.from_user.id}: {message.text}")
        await message.answer(
            "⚠️ Неизвестная команда. Используйте /help для списка доступных команд."
        )
        return
    logger.info(f"User {message.from_user.id} sent text, creating task")

    from src.entrypoints.telegram.bot import run_user_task

    await run_user_task(message, message.text)


# --- Helpers ---


def _extract_task_text(raw_text: str) -> str:
    """Extract task description from /task command text."""
    if raw_text.startswith("/task"):
        return raw_text[5:].strip()
    return raw_text.strip()
