"""Pydantic Graph definition and nodes"""

from loguru import logger

from src.domain.entities import ExecutionState
from src.infrastructure.llm.agents import CoderAgent, PlannerAgent
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

    def __init__(self) -> None:
        self.agent = PlannerAgent(create_llm_provider())

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute planning"""
        logger.info(f"PlannerNode: Planning task {state.task_id}")
        try:
            result = await self.agent.run(state.parsed_intent)
            state.plan = result.steps
            state.current_node = "CoderNode"
            logger.info(f"PlannerNode: Plan created with {len(result.steps)} steps")
        except Exception as e:
            logger.error(f"PlannerNode: Planning failed: {e}")
            state.current_node = "ErrorNode"
        return state


class CoderNode:
    """Generate code for tool"""

    def __init__(self) -> None:
        self.agent = CoderAgent(create_llm_provider())

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute code generation"""
        logger.info(f"CoderNode: Generating code for task {state.task_id}")
        try:
            result = await self.agent.run(state.plan)
            state.generated_code = result.code
            state.current_node = "ValidationNode"
            logger.info(f"CoderNode: Code generated ({len(result.code)} chars)")
        except Exception as e:
            logger.error(f"CoderNode: Code generation failed: {e}")
            state.current_node = "ErrorNode"
        return state


class ValidationNode:
    """Validate generated code"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Execute validation"""
        logger.info(f"ValidationNode: Validating code for task {state.task_id}")
        state.current_node = "ApprovalNode"
        return state


class ApprovalNode:
    """Wait for human approval — pauses graph execution"""

    async def execute(self, state: ExecutionState) -> ExecutionState:
        """Set requires_approval flag and fill approval data"""
        logger.info(f"ApprovalNode: Requesting approval for task {state.task_id}")
        state.requires_approval = True
        state.approval_data = {
            "code": state.generated_code,
            "plan": state.plan,
        }
        # Keep current_node as ApprovalNode — signals graph to pause
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


async def execute_graph(state: ExecutionState) -> ExecutionState:
    """Execute graph with state; pauses when requires_approval is set."""
    from src.entrypoints.graph_nodes import get_graph_nodes

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

        # Pause graph when human approval is required
        if state.requires_approval:
            logger.info(f"Graph paused at ApprovalNode for task {state.task_id}")
            return state

        if node_name in {"CompletionNode", "ErrorNode"}:
            break

        iteration += 1

    return state
