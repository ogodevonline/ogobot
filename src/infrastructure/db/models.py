"""SQLAlchemy ORM models"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""

    pass


class Task(Base):
    """Task model"""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int]
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    checkpoints: Mapped[list["Checkpoint"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )
    executions: Mapped[list["Execution"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_tasks_user_id", "user_id"),)


class Checkpoint(Base):
    """Checkpoint model for graph state"""

    __tablename__ = "checkpoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    node_name: Mapped[str]
    state_data: Mapped[str]
    created_at: Mapped[datetime]

    task: Mapped["Task"] = relationship(back_populates="checkpoints")

    __table_args__ = (Index("ix_checkpoints_task_id", task_id),)


class Tool(Base):
    """Tool model"""

    __tablename__ = "tools"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    code: Mapped[str]
    version: Mapped[int]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    executions: Mapped[list["Execution"]] = relationship(
        back_populates="tool", cascade="all, delete-orphan"
    )


class Execution(Base):
    """Execution model"""

    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id"))
    status: Mapped[str]
    result: Mapped[str | None]
    error: Mapped[str | None]
    duration_ms: Mapped[int]
    created_at: Mapped[datetime]

    task: Mapped["Task"] = relationship(back_populates="executions")
    tool: Mapped["Tool"] = relationship(back_populates="executions")

    __table_args__ = (Index("ix_executions_task_id", task_id),)


class Approval(Base):
    """Approval model for human-in-the-loop"""

    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    action_type: Mapped[str]
    action_data: Mapped[str]
    status: Mapped[str]
    user_id: Mapped[int]
    created_at: Mapped[datetime]
    approved_at: Mapped[datetime | None]

    __table_args__ = (Index("ix_approvals_status", "status"),)
