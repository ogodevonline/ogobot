# 3. Модель State для Pydantic Graph

## Основная State

```python
# src/domain/entities.py
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

class ExecutionState(BaseModel):
    """Состояние выполнения задачи в графе"""
    
    # Идентификаторы
    task_id: str
    user_id: int
    
    # Контекст задачи
    user_input: str  # Исходный запрос от пользователя
    current_node: str  # Текущий узел графа
    
    # Результаты промежуточных этапов
    parsed_intent: dict[str, Any] = Field(default_factory=dict)
    plan: list[str] = Field(default_factory=list)
    generated_code: str = ""
    validation_errors: list[str] = Field(default_factory=list)
    execution_result: Any = None
    
    # Метаданные
    created_at: datetime
    updated_at: datetime
    attempt_count: int = 0
    max_attempts: int = 3
    
    # Флаги
    requires_approval: bool = False
    approval_data: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = False  # Mutability для обновления в графе
```

## Узлы Графа (Nodes)

### 1. InputNode — Парсинг входных данных

```python
# src/entrypoints/graph.py
from pydantic_graph import Node

class InputNode(Node):
    """Парсирует пользовательский ввод"""
    
    async def execute(self, state: ExecutionState) -> ExecutionState:
        # Валидация и парсинг user_input
        state.parsed_intent = parse_intent(state.user_input)
        state.current_node = "PlannerNode"
        return state
```

### 2. PlannerNode — Декомпозиция задачи

```python
class PlannerNode(Node):
    """Разбивает задачу на подзадачи"""
    
    async def execute(self, state: ExecutionState) -> ExecutionState:
        # Использует Pydantic AI для планирования
        state.plan = await planner_agent.run(state.parsed_intent)
        state.current_node = "CoderNode"
        return state
```

### 3. CoderNode — Генерация кода

```python
class CoderNode(Node):
    """Генерирует Python-код для инструмента"""
    
    async def execute(self, state: ExecutionState) -> ExecutionState:
        # Генерирует код через Pydantic AI
        state.generated_code = await coder_agent.run(state.plan)
        state.current_node = "ValidationNode"
        return state
```

### 4. ValidationNode — Проверка безопасности

```python
class ValidationNode(Node):
    """Валидирует сгенерированный код"""
    
    async def execute(self, state: ExecutionState) -> ExecutionState:
        errors = validate_code_safety(state.generated_code)
        if errors:
            state.validation_errors = errors
            state.current_node = "ErrorNode"
        else:
            state.current_node = "ApprovalNode"
        return state
```

### 5. ApprovalNode — Human-in-the-Loop

```python
class ApprovalNode(Node):
    """Ждет подтверждения от пользователя"""
    
    async def execute(self, state: ExecutionState) -> ExecutionState:
        state.requires_approval = True
        state.approval_data = {
            "code": state.generated_code,
            "plan": state.plan
        }
        # Граф приостанавливается, ждет callback от Telegram
        state.current_node = "ExecutorNode"  # После одобрения
        return state
```

### 6. ExecutorNode — Запуск инструмента

```python
class ExecutorNode(Node):
    """Выполняет сгенерированный код в sandbox"""
    
    async def execute(self, state: ExecutionState) -> ExecutionState:
        try:
            result = await execute_in_sandbox(
                code=state.generated_code,
                timeout=30
            )
            state.execution_result = result
            state.current_node = "CompletionNode"
        except Exception as e:
            state.validation_errors.append(str(e))
            state.current_node = "ErrorNode"
        return state
```

## Граф Конфигурация

```python
# src/entrypoints/graph.py
from pydantic_graph import Graph

graph = Graph(
    nodes=[
        InputNode(),
        PlannerNode(),
        CoderNode(),
        ValidationNode(),
        ApprovalNode(),
        ExecutorNode(),
        CompletionNode(),
        ErrorNode(),
    ],
    edges=[
        ("InputNode", "PlannerNode"),
        ("PlannerNode", "CoderNode"),
        ("CoderNode", "ValidationNode"),
        ("ValidationNode", "ApprovalNode"),
        ("ValidationNode", "ErrorNode"),
        ("ApprovalNode", "ExecutorNode"),
        ("ExecutorNode", "CompletionNode"),
        ("ExecutorNode", "ErrorNode"),
    ]
)
```

---

**Далее:** [`04_DYNAMIC_IMPORT.md`](04_DYNAMIC_IMPORT.md)
