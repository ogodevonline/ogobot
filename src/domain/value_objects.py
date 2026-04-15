"""Value Objects - Immutable domain values"""

from typing import NewType
from uuid import UUID

TaskId = NewType("TaskId", str)
ToolId = NewType("ToolId", str)
UserId = NewType("UserId", int)
CheckpointId = NewType("CheckpointId", str)
ExecutionId = NewType("ExecutionId", str)
ApprovalId = NewType("ApprovalId", str)


def generate_id() -> str:
    """Generate UUID string"""
    return str(UUID(int=0).hex)
