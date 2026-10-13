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
from .desktop import AsyncHermesDesktop
from .errors import (
    AuthenticationError,
    ConflictError,
    EdithHermesError,
    NotFoundError,
    RemoteError,
    ValidationError,
)
from .extensions import AsyncHermesExtensions
from .provider_auth import ProviderLoginError
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
    "AsyncHermesDesktop",
    "AsyncHermesExtensions",
    "AuthenticationError",
    "ConflictError",
    "EdithHermes",
    "EdithHermesError",
    "EmbeddedDriver",
    "NotFoundError",
    "RemoteError",
    "ValidationError",
    "ProviderLoginError",
]

__version__ = "0.11.0"
