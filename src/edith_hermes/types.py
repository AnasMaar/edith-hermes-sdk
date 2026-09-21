"""Small stable types shared by generated and handwritten SDK code."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OwnerReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(alias="tenantId")
    subject_id: str = Field(alias="subjectId")


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperationResult(BaseModel):
    """Forward-compatible response wrapper for dynamic/native operations."""

    model_config = ConfigDict(extra="allow")

    value: Any = None
