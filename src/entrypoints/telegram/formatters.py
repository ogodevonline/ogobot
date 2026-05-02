"""Message formatters for Telegram bot responses."""

from src.domain.entities import ExecutionState


def format_welcome() -> str:
    """Format welcome message with HTML."""
    return (
        "<b>🚀 S.E.A.C. — Self-Evolving AI Core</b>\n\n"
        "Я — саморазвивающееся AI-ядро. Помогаю создавать, "
        "планировать и выполнять задачи с помощью LLM.\n\n"
        "<b>📋 Команды:</b>\n"
        "/task <описание> — создать задачу\n"
        "/status — статус текущей задачи\n"
        "/tools — список инструментов\n"
        "/help — справка\n\n"
        "<i>Отправьте описание задачи, и я запущу граф выполнения.</i>"
    )


def format_help() -> str:
    """Format help message."""
    return (
        "<b>📖 Справка по S.E.A.C.</b>\n\n"
        "<b>Команды:</b>\n"
        "/start — приветствие\n"
        "/task <описание> — создать и запустить задачу\n"
        "/status — показать статус текущей задачи\n"
        "/tools — список доступных инструментов\n"
        "/help — эта справка\n\n"
        "<b>Как это работает:</b>\n"
        "1. Вы отправляете описание задачи\n"
        "2. PlannerAgent разбивает её на шаги\n"
        "3. CoderAgent генерирует код\n"
        "4. Код проходит валидацию и исполнение\n"
        "5. Результат возвращается вам\n\n"
        "<b>Граф узлов:</b> Input → Planner → Coder → "
        "Validation → Approval → Executor → Completion"
    )


def format_task_result(state: ExecutionState) -> str:
    """Format task execution result with HTML."""
    lines = [
        "<b>✅ Задача выполнена</b>\n",
        f"<b>ID:</b> <code>{state.task_id}</code>",
        f"<b>Узел:</b> {state.current_node}",
    ]
    if state.plan:
        plan_text = "\n".join(f"  • {s}" for s in state.plan[:10])
        lines.append(f"<b>План ({len(state.plan)} шагов):</b>\n{plan_text}")
    if state.generated_code:
        code_preview = state.generated_code[:300]
        lines.append(
            f"<b>Код ({len(state.generated_code)} симв.):</b>\n"
            f"<pre>{code_preview}</pre>"
        )
    if state.execution_result:
        result_str = str(state.execution_result)[:500]
        lines.append(f"<b>Результат:</b>\n<pre>{result_str}</pre>")
    if state.validation_errors:
        errs = "\n".join(f"  ❌ {e}" for e in state.validation_errors)
        lines.append(f"<b>Ошибки валидации:</b>\n{errs}")
    return "\n".join(lines)


def format_status(state: ExecutionState) -> str:
    """Format current task status."""
    lines = [
        f"<b>📊 Статус задачи</b> <code>{state.task_id}</code>\n",
        f"<b>Текущий узел:</b> {state.current_node}",
        f"<b>Попыток:</b> {state.attempt_count}/{state.max_attempts}",
    ]
    if state.plan:
        lines.append(f"<b>Шагов в плане:</b> {len(state.plan)}")
    if state.requires_approval:
        lines.append("⚠️ <b>Требуется подтверждение</b>")
    return "\n".join(lines)
