class ToolError(Exception):
    """Base class for tool-layer failures."""

    def __init__(self, tool: str, error_code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.tool = tool
        self.error_code = error_code
        self.message = message
        self.retryable = retryable


class ToolNotFoundError(ToolError):
    """Raised when a requested entity cannot be found."""

    def __init__(self, tool: str, message: str):
        super().__init__(tool=tool, error_code="not_found", message=message, retryable=False)


class ToolValidationError(ToolError):
    """Raised when a tool request is structurally valid but operationally unsupported."""

    def __init__(self, tool: str, message: str):
        super().__init__(tool=tool, error_code="validation_error", message=message, retryable=False)
