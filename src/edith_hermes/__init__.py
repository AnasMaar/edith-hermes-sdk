"""Public EDITH Hermes SDK API."""

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

__version__ = "0.2.0"
