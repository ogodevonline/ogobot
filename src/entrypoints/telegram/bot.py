"""Telegram bot setup and task execution orchestration."""

import asyncio
from uuid import uuid4

from aiogram import Bot, Dispatcher, types
from loguru import logger

from src.domain.entities import ExecutionState
from src.domain.value_objects import TaskId, UserId
from src.entrypoints.graph import execute_graph
from src.entrypoints.telegram.formatters import format_task_result
from src.entrypoints.telegram.handlers import GRAPH_TIMEOUT, router
from src.entrypoints.telegram.middleware import LoggingMiddleware

# Per-user state tracking for /status command
_user_states: dict[UserId, ExecutionState] = {}


def get_user_state(user_id: UserId) -> ExecutionState | None:
    """Get current execution state for a user."""
    return _user_states.get(user_id)


async def run_user_task(message: types.Message, task_text: str) -> None:
    """Create ExecutionState, run graph, send result back to user."""
    if not message.from_user:
        return

    user_id = UserId(message.from_user.id)
    task_id = TaskId(uuid4().hex[:12])

    state = ExecutionState(task_id=task_id, user_id=user_id, user_input=task_text)
    _user_states[user_id] = state

    status_msg = await message.answer(
        f"<i>⏳ Задача <code>{task_id}</code> запущена...\n"
        f"Текущий узел: {state.current_node}</i>"
    )

    logger.info(f"User {user_id} created task {task_id}: {task_text[:80]}")

    try:
        state = await asyncio.wait_for(execute_graph(state), timeout=GRAPH_TIMEOUT)
    except asyncio.TimeoutError:
        logger.error(f"Task {task_id} timed out after {GRAPH_TIMEOUT}s")
        _user_states[user_id] = state
        await status_msg.edit_text(
            f"⚠️ <b>Таймаут выполнения</b>\n"
            f"Задача <code>{task_id}</code> заняла более "
            f"{int(GRAPH_TIMEOUT)} секунд и была прервана.\n"
            f"Последний узел: {state.current_node}"
        )
        return
    except Exception as exc:
        logger.exception(f"Task {task_id} failed with exception")
        _user_states[user_id] = state
        await status_msg.edit_text(
            f"❌ <b>Ошибка выполнения</b>\n"
            f"Задача <code>{task_id}</code> завершилась с ошибкой:\n"
            f"<pre>{exc!s}</pre>"
        )
        return

    _user_states[user_id] = state
    result_text = format_task_result(state)
    await status_msg.edit_text(result_text)


async def start_bot(token: str) -> None:
    """Start Telegram bot with all routers and middleware."""
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.update.outer_middleware(LoggingMiddleware())
    dp.include_router(router)

    logger.info("Starting Telegram bot")
    await dp.start_polling(bot)
