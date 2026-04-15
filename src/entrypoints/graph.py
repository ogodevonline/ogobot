"""Pydantic Graph definition and nodes"""

from loguru import logger

from src.domain.entities import ExecutionState
from src.infrastructure.llm.factory import create_llm_provider


class InputNode:
    """Parse user input"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute input parsing"""
        logger.info(f"InputNode: Processing input from user {state.user_id}")
        state.current_node = "PlannerNode"
        state.parsed_intent = {"raw_input": state.user_input}
        return state


class PlannerNode:
    """Decompose task into subtasks"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute planning"""
        logger.info(f"PlannerNode: Planning task {state.task_id}")
        state.current_node = "CoderNode"
        state.plan = ["step_1", "step_2", "step_3"]
        return state


class CoderNode:
    """Generate code for tool"""

    def __init__(self) -> None:
        """Initialize with LLM provider"""
        self.llm = create_llm_provider()

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute code generation"""
        logger.info(f"CoderNode: Generating code for task {state.task_id}")
        state.current_node = "ValidationNode"
        spec = "\n".join(state.plan)
        state.generated_code = await self.llm.generate_code(spec)
        return state


class ValidationNode:
    """Validate generated code"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute validation"""
        logger.info(f"ValidationNode: Validating code for task {state.task_id}")
        state.current_node = "ApprovalNode"
        return state


class ApprovalNode:
    """Wait for human approval"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute approval"""
        logger.info(f"ApprovalNode: Waiting approval for task {state.task_id}")
        state.requires_approval = True
        state.current_node = "ExecutorNode"
        return state


class ExecutorNode:
    """Execute generated code"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute code"""
        logger.info(f"ExecutorNode: Executing code for task {state.task_id}")
        state.current_node = "CompletionNode"
        state.execution_result = {"status": "success"}
        return state


class CompletionNode:
    """Complete task"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute completion"""
        logger.info(f"CompletionNode: Task {state.task_id} completed")
        return state


class ErrorNode:
    """Handle errors"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute error handling"""
        logger.error(f"ErrorNode: Task {state.task_id} failed")
        return state


# Graph nodes registry (lazy initialization)
_GRAPH_NODES: dict | None = None


def get_graph_nodes() -> dict:
    """Get graph nodes (lazy initialization)"""
    global _GRAPH_NODES
    if _GRAPH_NODES is None:
        _GRAPH_NODES = {
            "InputNode": InputNode(),
            "PlannerNode": PlannerNode(),
            "CoderNode": CoderNode(),
            "ValidationNode": ValidationNode(),
            "ApprovalNode": ApprovalNode(),
            "ExecutorNode": ExecutorNode(),
            "CompletionNode": CompletionNode(),
            "ErrorNode": ErrorNode(),
        }
    return _GRAPH_NODES


async def execute_graph(state: ExecutionState) -> ExecutionState:
    """Execute graph with state"""
    max_iterations = 10
    iteration = 0
    nodes = get_graph_nodes()

    while iteration < max_iterations:
        node_name = state.current_node
        logger.info(f"Executing node: {node_name}")

        if node_name not in nodes:
            logger.error(f"Unknown node: {node_name}")
            break

        node = nodes[node_name]
        state = await node.execute(state)

        if node_name in {"CompletionNode", "ErrorNode"}:
            break

        iteration += 1

    return state
