"""Telegram bot integration with aiogram"""

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from loguru import logger

from src.domain.entities import ExecutionState
from src.domain.value_objects import TaskId, UserId
from src.entrypoints.graph import execute_graph

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Handle /start command"""
    if not message.from_user:
        logger.warning("Received message without from_user")
        return
    logger.info(f"User {message.from_user.id} started bot")
    await message.answer("Welcome to S.E.A.C. - Self-Evolving AI Core!")


@router.message(Command("task"))
async def cmd_task(message: types.Message) -> None:
    """Handle /task command"""
    if not message.from_user:
        logger.warning("Received message without from_user")
        return
    user_id = UserId(message.from_user.id)
    task_id = TaskId("task_001")

    logger.info(f"User {user_id} created task {task_id}")

    state = ExecutionState(
        task_id=task_id,
        user_id=user_id,
        user_input=message.text or "",
    )

    state = await execute_graph(state)

    await message.answer(f"Task completed: {state.execution_result}")


@router.message()
async def handle_message(message: types.Message) -> None:
    """Handle regular messages"""
    if not message.from_user:
        logger.warning("Received message without from_user")
        return
    logger.info(f"Message from {message.from_user.id}: {message.text}")
    await message.answer("I received your message!")


async def start_bot(token: str) -> None:
    """Start Telegram bot"""
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting Telegram bot")
    await dp.start_polling(bot)
