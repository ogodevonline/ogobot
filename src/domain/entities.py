"""Domain entities - Core business objects"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.domain.value_objects import TaskId, UserId


class ExecutionState(BaseModel):
    """State of task execution in the graph"""

    task_id: TaskId
    user_id: UserId
    user_input: str
    current_node: str = "InputNode"
    parsed_intent: dict[str, Any] = Field(default_factory=dict)
    plan: list[str] = Field(default_factory=list)
    generated_code: str = ""
    validation_errors: list[str] = Field(default_factory=list)
    execution_result: Any = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    attempt_count: int = 0
    max_attempts: int = 3
    requires_approval: bool = False
    approval_data: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config"""

        frozen = False
