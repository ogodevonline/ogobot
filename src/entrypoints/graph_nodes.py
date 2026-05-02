"""Lazy-initialized registry of graph nodes."""

from src.entrypoints.graph import (
    ApprovalNode,
    CoderNode,
    CompletionNode,
    ErrorNode,
    ExecutorNode,
    InputNode,
    PlannerNode,
    ValidationNode,
)

_GRAPH_NODES: dict | None = None


def get_graph_nodes() -> dict:
    """Get graph nodes (lazy initialization)."""
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
