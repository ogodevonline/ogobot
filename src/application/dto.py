"""Data Transfer Objects - API contracts"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TaskDTO(BaseModel):
    """Task data transfer object"""

    id: str
    user_id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime


class ToolDTO(BaseModel):
    """Tool data transfer object"""

    id: str
    name: str
    description: str
    version: int
    created_at: datetime


class ExecutionDTO(BaseModel):
    """Execution data transfer object"""

    id: str
    task_id: str
    tool_id: str
    status: str
    result: Any | None
    error: str | None
    duration_ms: int
    created_at: datetime


class PlanResult(BaseModel):
    """Result of planning phase"""

    steps: list[str]
    reasoning: str
    estimated_complexity: str


class CodeResult(BaseModel):
    """Result of code generation phase"""

    code: str
    explanation: str
    dependencies: list[str]


class ApprovalDTO(BaseModel):
    """Approval data transfer object for human-in-the-loop"""

    id: str
    task_id: str
    action_type: str
    action_data: str
    status: str
    user_id: int
    created_at: datetime
    approved_at: datetime | None = None
