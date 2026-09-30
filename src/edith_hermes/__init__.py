"""Public EDITH Hermes SDK API."""

from .agent import (
    Agent,
    BoundAgent,
    Docker,
    External,
    Hermes,
    Instance,
    Kubernetes,
    Model,
    Process,
    RunResult,
    Runtime,
    Tool,
    ToolHost,
    tool,
)
from .client import AsyncEdithHermes, EdithHermes
from .errors import (
    AuthenticationError,
    ConflictError,
    EdithHermesError,
    NotFoundError,
    RemoteError,
    ValidationError,
)
from .transport import EmbeddedDriver

__all__ = [
    "Agent",
    "BoundAgent",
    "Docker",
    "External",
    "Hermes",
    "Instance",
    "Kubernetes",
    "Model",
    "Process",
    "RunResult",
    "Runtime",
    "Tool",
    "ToolHost",
    "tool",
    "AsyncEdithHermes",
    "AuthenticationError",
    "ConflictError",
    "EdithHermes",
    "EdithHermesError",
    "EmbeddedDriver",
    "NotFoundError",
    "RemoteError",
    "ValidationError",
]

__version__ = "0.4.0"
