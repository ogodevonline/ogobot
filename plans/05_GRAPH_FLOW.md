# 5. Диаграмма Потока Данных

## Основной Поток Выполнения

```mermaid
graph TD
    A[Telegram: /start task] -->|user_input| B[InputNode]
    B -->|parsed_intent| C[PlannerNode]
    C -->|plan| D[CoderNode]
    D -->|generated_code| E[ValidationNode]
    
    E -->|errors found| F[ErrorNode]
    E -->|code valid| G[ApprovalNode]
    
    G -->|requires_approval=true| H[Telegram: Inline Buttons]
    H -->|user clicks Approve| I[ExecutorNode]
    H -->|user clicks Reject| F
    
    I -->|success| J[CompletionNode]
    I -->|error/timeout| F
    
    J -->|save result| K[DB: Execution Log]
    F -->|save error| K
    
    K -->|notify user| L[Telegram: Result Message]
```

## Восстановление из Checkpoint

```mermaid
graph TD
    A[Process Crash] -->|read last checkpoint| B[DB: Checkpoints]
    B -->|load ExecutionState| C[Resume from Node]
    C -->|continue execution| D[Graph continues]
    D -->|save new checkpoint| E[DB: Checkpoints]
```

## Интеграция с Telegram

```mermaid
graph LR
    A[User Message] -->|aiogram| B[TelegramHandler]
    B -->|create task| C[ExecutionState]
    C -->|start graph| D[Pydantic Graph]
    D -->|requires_approval| E[Send Inline Buttons]
    E -->|callback_query| F[ApprovalHandler]
    F -->|update state| D
    D -->|completion| G[Send Result Message]
```

## Жизненный Цикл Инструмента

```mermaid
graph TD
    A[CoderNode generates code] -->|code string| B[ValidationNode]
    B -->|AST validation| C{Safe?}
    C -->|No| D[ErrorNode]
    C -->|Yes| E[ApprovalNode]
    E -->|User approves| F[register_tool]
    F -->|save to DB| G[Tool model]
    F -->|write to file| H[src/tools/tool_name.py]
    F -->|importlib.reload| I[ToolRegistry]
    I -->|tool available| J[ExecutorNode can use it]
```

## Состояние в БД

```
Task (user_id, status, created_at)
  ├── Checkpoints (node_name, state_data, created_at)
  │   └── state_data = JSON(ExecutionState)
  ├── Executions (tool_id, status, result, duration_ms)
  └── Approvals (action_type, action_data, status)

Tool (name, code, version, created_at)
  └── Executions (task_id, status, result)
```

## Сценарий: Самоэволюция

```
1. User: "Создай инструмент для парсинга JSON"
   ↓
2. InputNode парсит intent
   ↓
3. PlannerNode создает план
   ↓
4. CoderNode генерирует код функции parse_json()
   ↓
5. ValidationNode проверяет безопасность
   ↓
6. ApprovalNode отправляет Inline-кнопки в Telegram
   ↓
7. User нажимает "Approve"
   ↓
8. register_tool() сохраняет в БД и файловую систему
   ↓
9. ToolRegistry перезагружает модуль
   ↓
10. ExecutorNode тестирует инструмент
    ↓
11. Инструмент готов к использованию в будущих задачах
```

## Таймауты и Ограничения

| Компонент | Таймаут | Лимит |
|-----------|---------|-------|
| Pydantic AI запрос | 60s | 3 попытки |
| Код в sandbox | 30s | 1 выполнение |
| Граф выполнение | 300s | 1 попытка |
| Одобрение от пользователя | 3600s | ∞ |

---

**Архитектурный план завершен. Ожидаю вашего подтверждения.**
