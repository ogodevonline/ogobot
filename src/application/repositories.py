"""Repository interfaces - Data access contracts"""

from abc import ABC, abstractmethod

from src.application.dto import ExecutionDTO, TaskDTO, ToolDTO
from src.domain.value_objects import TaskId


class TaskRepository(ABC):
    """Task repository interface"""

    @abstractmethod
    async def create(self, task: TaskDTO) -> TaskDTO:
        """Create task"""
        pass

    @abstractmethod
    async def get_by_id(self, task_id: TaskId) -> TaskDTO | None:
        """Get task by ID"""
        pass

    @abstractmethod
    async def update(self, task: TaskDTO) -> TaskDTO:
        """Update task"""
        pass


class ToolRepository(ABC):
    """Tool repository interface"""

    @abstractmethod
    async def create(self, tool: ToolDTO) -> ToolDTO:
        """Create tool"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> ToolDTO | None:
        """Get tool by name"""
        pass

    @abstractmethod
    async def list_all(self) -> list[ToolDTO]:
        """List all tools"""
        pass


class ExecutionRepository(ABC):
    """Execution repository interface"""

    @abstractmethod
    async def create(self, execution: ExecutionDTO) -> ExecutionDTO:
        """Create execution record"""
        pass

    @abstractmethod
    async def get_by_id(self, execution_id: str) -> ExecutionDTO | None:
        """Get execution by ID"""
        pass
