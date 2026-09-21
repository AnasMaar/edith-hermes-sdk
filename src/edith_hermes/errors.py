"""Normalized SDK exceptions."""

from __future__ import annotations

from typing import Any


class EdithHermesError(Exception):
    """Base SDK exception."""


class RemoteError(EdithHermesError):
    """A remote API returned a problem response."""

    def __init__(self, status: int, title: str, *, detail: str | None = None, body: Any = None):
        self.status = status
        self.title = title
        self.detail = detail
        self.body = body
        super().__init__(f"{status} {title}" + (f": {detail}" if detail else ""))


class AuthenticationError(RemoteError):
    """Authentication or authorization failed."""


class NotFoundError(RemoteError):
    """A requested resource does not exist or is not visible."""


class ConflictError(RemoteError):
    """The request conflicts with current resource state."""


class ValidationError(RemoteError):
    """The server rejected request input."""


def error_from_response(status: int, body: Any) -> RemoteError:
    problem = body if isinstance(body, dict) else {}
    title = str(problem.get("title") or "Request failed")
    detail = problem.get("detail")
    cls: type[RemoteError]
    if status in {401, 403}:
        cls = AuthenticationError
    elif status == 404:
        cls = NotFoundError
    elif status == 409:
        cls = ConflictError
    elif status in {400, 422}:
        cls = ValidationError
    else:
        cls = RemoteError
    return cls(status, title, detail=str(detail) if detail else None, body=body)
