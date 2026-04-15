"""Domain exceptions - Business logic errors"""


class SEACException(Exception):
    """Base exception for S.E.A.C."""

    pass


class ValidationError(SEACException):
    """Raised when validation fails"""

    pass


class CodeExecutionError(SEACException):
    """Raised when code execution fails"""

    pass


class TimeoutError(SEACException):
    """Raised when operation times out"""

    pass


class ApprovalRequiredError(SEACException):
    """Raised when human approval is required"""

    pass


class ToolNotFoundError(SEACException):
    """Raised when tool is not found"""

    pass
