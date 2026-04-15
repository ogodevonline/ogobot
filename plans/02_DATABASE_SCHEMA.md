# 2. Схема БД (SQLite + SQLAlchemy)

## Таблицы и Модели

### 1. `tasks` — История задач

```python
# src/infrastructure/db/models.py
class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[str] = mapped_column(primary_key=True)  # UUID
    user_id: Mapped[int]  # Telegram user_id
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[str]  # "pending", "in_progress", "completed", "failed"
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    
    # Relationships
    checkpoints: Mapped[list["Checkpoint"]] = relationship(back_populates="task")
    executions: Mapped[list["Execution"]] = relationship(back_populates="task")
```

### 2. `checkpoints` — Сохранение состояния графа

```python
class Checkpoint(Base):
    __tablename__ = "checkpoints"
    
    id: Mapped[str] = mapped_column(primary_key=True)  # UUID
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    node_name: Mapped[str]  # "InputNode", "PlannerNode", etc.
    state_data: Mapped[str]  # JSON-сериализованное состояние
    created_at: Mapped[datetime]
    
    task: Mapped["Task"] = relationship(back_populates="checkpoints")
```

### 3. `tools` — Реестр инструментов

```python
class Tool(Base):
    __tablename__ = "tools"
    
    id: Mapped[str] = mapped_column(primary_key=True)  # UUID
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    code: Mapped[str]  # Исходный Python-код
    version: Mapped[int]  # Версия инструмента
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    
    executions: Mapped[list["Execution"]] = relationship(back_populates="tool")
```

### 4. `executions` — Логирование выполнения

```python
class Execution(Base):
    __tablename__ = "executions"
    
    id: Mapped[str] = mapped_column(primary_key=True)  # UUID
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id"))
    status: Mapped[str]  # "success", "timeout", "error"
    result: Mapped[str | None]  # JSON результат
    error: Mapped[str | None]  # Сообщение об ошибке
    duration_ms: Mapped[int]  # Время выполнения
    created_at: Mapped[datetime]
    
    task: Mapped["Task"] = relationship(back_populates="executions")
    tool: Mapped["Tool"] = relationship(back_populates="executions")
```

### 5. `approvals` — Human-in-the-Loop

```python
class Approval(Base):
    __tablename__ = "approvals"
    
    id: Mapped[str] = mapped_column(primary_key=True)  # UUID
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    action_type: Mapped[str]  # "register_tool", "shell_command", etc.
    action_data: Mapped[str]  # JSON с деталями действия
    status: Mapped[str]  # "pending", "approved", "rejected"
    user_id: Mapped[int]  # Telegram user_id
    created_at: Mapped[datetime]
    approved_at: Mapped[datetime | None]
```

## Индексы

```python
# Для быстрого поиска
Index("ix_tasks_user_id", Task.user_id)
Index("ix_checkpoints_task_id", Checkpoint.task_id)
Index("ix_executions_task_id", Execution.task_id)
Index("ix_approvals_status", Approval.status)
```

## Миграции

Использовать **Alembic** для версионирования схемы:

```bash
uv run alembic init migrations
uv run alembic revision --autogenerate -m "Initial schema"
uv run alembic upgrade head
```

---

**Далее:** [`03_STATE_MODEL.md`](03_STATE_MODEL.md)
