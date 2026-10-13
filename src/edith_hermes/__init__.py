"""Public EDITH Hermes SDK API."""

from .administration import DesktopAdministration
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
from .deployment import AsyncDeployment
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
from .git_mutations import AsyncGitMutations
from .integration_mutations import AsyncIntegrationMutations
from .provider_auth import ProviderLoginError
from .schedule_mutations import AsyncScheduleMutations
from .skill_administration import AsyncSkillAdministration
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
    "DesktopAdministration",
    "AsyncDeployment",
    "AsyncGitMutations",
    "AsyncIntegrationMutations",
    "AsyncScheduleMutations",
    "AsyncSkillAdministration",
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

__version__ = "0.16.0"
