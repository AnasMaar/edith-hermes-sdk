"""SQLite/PostgreSQL resource, lease and durable-job storage."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any, cast

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    and_,
    or_,
    select,
    text,
    update,
)
from sqlalchemy import (
    delete as sql_delete,
)
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import AsyncAdaptedQueuePool


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Resource(Base):
    __tablename__ = "resources"
    kind: Mapped[str] = mapped_column(String(48), primary_key=True)
    resource_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    subject_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class DurableJob(Base):
    __tablename__ = "jobs"
    job_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(48), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(48), nullable=False, default="queued")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    logs: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cancel_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    worker_id: Mapped[str | None] = mapped_column(String(128))
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


Index("ix_jobs_claim", DurableJob.status, DurableJob.created_at)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    operation_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    subject_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(24), nullable=False, default="in_progress")
    status_code: Mapped[int | None] = mapped_column(Integer)
    response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Database:
    def __init__(self, url: str):
        self.engine: AsyncEngine
        if url.startswith("sqlite"):
            # SQLite has one writer. A single queued connection also prevents
            # same-process read-to-write snapshot upgrades from deadlocking.
            # WAL + busy timeout handle independently connected workers.
            self.engine = create_async_engine(
                url,
                pool_pre_ping=True,
                connect_args={"timeout": 30},
                poolclass=AsyncAdaptedQueuePool,
                pool_size=1,
                max_overflow=0,
            )
        else:
            self.engine = create_async_engine(url, pool_pre_ping=True)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            if self.engine.dialect.name == "sqlite":
                # WAL keeps concurrent readers from blocking queued writers.
                # In-memory SQLite safely retains its memory journal instead.
                await connection.exec_driver_sql("PRAGMA journal_mode=WAL")
            await connection.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()

    async def put(
        self,
        kind: str,
        resource_id: str,
        owner: tuple[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        async with self.sessions.begin() as session:
            key = (kind, resource_id, owner[0], owner[1])
            record = await session.get(Resource, key)
            if record is None:
                record = Resource(
                    kind=kind,
                    resource_id=resource_id,
                    tenant_id=owner[0],
                    subject_id=owner[1],
                    payload=payload,
                )
                session.add(record)
            else:
                record.payload = payload
                record.version += 1
                record.updated_at = utcnow()
        return payload

    async def get(
        self, kind: str, resource_id: str, owner: tuple[str, str]
    ) -> dict[str, Any] | None:
        async with self.sessions() as session:
            record = await session.get(Resource, (kind, resource_id, owner[0], owner[1]))
            return None if record is None else dict(record.payload)

    async def list(self, kind: str, owner: tuple[str, str]) -> list[dict[str, Any]]:
        async with self.sessions() as session:
            result = await session.scalars(
                select(Resource)
                .where(
                    and_(
                        Resource.kind == kind,
                        Resource.tenant_id == owner[0],
                        Resource.subject_id == owner[1],
                    )
                )
                .order_by(Resource.created_at)
            )
            return [dict(item.payload) for item in result]

    async def delete(self, kind: str, resource_id: str, owner: tuple[str, str]) -> bool:
        async with self.sessions.begin() as session:
            record = await session.get(Resource, (kind, resource_id, owner[0], owner[1]))
            if record is None:
                return False
            await session.delete(record)
            return True

    async def save_provider_login(
        self, resource_id: str, owner: tuple[str, str], payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Compare-and-set login state: a slow poll cannot resurrect a terminal flow.

        Works across control-plane workers/backends without keeping OAuth state
        in process memory. The initial row is created before its ID is exposed.
        """
        terminal = {"approved", "denied", "expired", "cancelled", "failed"}
        for _ in range(10):
            async with self.sessions.begin() as session:
                record = await session.get(Resource, ("provider_login", resource_id, *owner))
                if record is None:
                    session.add(
                        Resource(
                            kind="provider_login",
                            resource_id=resource_id,
                            tenant_id=owner[0],
                            subject_id=owner[1],
                            payload=payload,
                        )
                    )
                    return payload
                if record.payload["status"] in terminal:
                    return dict(record.payload)
                result = await session.execute(
                    update(Resource)
                    .where(
                        Resource.kind == "provider_login",
                        Resource.resource_id == resource_id,
                        Resource.tenant_id == owner[0],
                        Resource.subject_id == owner[1],
                        Resource.version == record.version,
                    )
                    .values(payload=payload, version=record.version + 1, updated_at=utcnow())
                )
                if cast(CursorResult[Any], result).rowcount == 1:
                    return payload
        raise RuntimeError("Concurrent provider login updates did not settle")

    async def delete_runtime_tree(
        self,
        owner: tuple[str, str],
        *,
        instance_id: str,
        profile_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """Remove a deleted runtime's dependent registry rows in one transaction.

        Tool bundles/MCP definitions are independent, reusable resources. Only
        their bindings belong to the runtime tree. Jobs remain as audit history.
        """
        whole_instance = profile_id is None and session_id is None
        async with self.sessions.begin() as transaction:
            records = list(
                await transaction.scalars(
                    select(Resource).where(
                        Resource.tenant_id == owner[0],
                        Resource.subject_id == owner[1],
                        Resource.kind.in_(
                            [
                                "instance",
                                "profile",
                                "session",
                                "turn",
                                "tool_binding",
                                "lease",
                                "lease_slot",
                                "provider_login",
                            ]
                        ),
                    )
                )
            )
            session_ids = {
                row.resource_id
                for row in records
                if row.kind == "session"
                and row.payload.get("instanceId") == instance_id
                and (profile_id is None or row.payload.get("profileId") == profile_id)
                and (session_id is None or row.resource_id == session_id)
            }
            for row in records:
                value = row.payload
                scope = value.get("scope") or {}
                remove = (
                    row.kind == "instance"
                    and whole_instance
                    and row.resource_id == instance_id
                    or row.kind == "profile"
                    and session_id is None
                    and value.get("instanceId") == instance_id
                    and (profile_id is None or row.resource_id == profile_id)
                    or row.kind == "session"
                    and row.resource_id in session_ids
                    or row.kind == "turn"
                    and value.get("sessionId") in session_ids
                    or row.kind == "tool_binding"
                    and session_id is None
                    and scope.get("instanceId") == instance_id
                    and (profile_id is None or scope.get("profileId") == profile_id)
                    or row.kind == "lease"
                    and whole_instance
                    and value.get("instanceId") == instance_id
                    or row.kind == "lease_slot"
                    and whole_instance
                    and row.resource_id == instance_id
                    or row.kind == "provider_login"
                    and session_id is None
                    and value.get("instanceId") == instance_id
                    and (profile_id is None or value.get("profileId") == profile_id)
                )
                if remove:
                    await transaction.delete(row)

    async def reserve_lease_slot(
        self, instance_id: str, owner: tuple[str, str], lease_id: str, expires_at: datetime
    ) -> bool:
        """Atomically reserve one instance, including across control-plane workers.

        The resource primary key arbitrates first insertion. Version-checked
        updates arbitrate expired slots; an old lease cannot release a newer one.
        This uses the existing schema so no destructive migration is required.
        """
        payload = {"leaseId": lease_id, "expiresAt": expires_at.isoformat()}
        try:
            async with self.sessions.begin() as transaction:
                if self.engine.dialect.name == "sqlite":
                    await transaction.execute(text("BEGIN IMMEDIATE"))
                record = await transaction.get(Resource, ("lease_slot", instance_id, *owner))
                if record is None:
                    transaction.add(
                        Resource(
                            kind="lease_slot",
                            resource_id=instance_id,
                            tenant_id=owner[0],
                            subject_id=owner[1],
                            payload=payload,
                        )
                    )
                    await transaction.flush()
                    return True
                if datetime.fromisoformat(record.payload["expiresAt"]) > utcnow():
                    return False
                result = await transaction.execute(
                    update(Resource)
                    .where(
                        Resource.kind == "lease_slot",
                        Resource.resource_id == instance_id,
                        Resource.tenant_id == owner[0],
                        Resource.subject_id == owner[1],
                        Resource.version == record.version,
                    )
                    .values(payload=payload, version=record.version + 1, updated_at=utcnow())
                )
                return cast(CursorResult[Any], result).rowcount == 1
        except IntegrityError:
            return False

    async def release_lease_slot(
        self, instance_id: str, owner: tuple[str, str], lease_id: str
    ) -> None:
        async with self.sessions.begin() as transaction:
            await transaction.execute(
                sql_delete(Resource).where(
                    Resource.kind == "lease_slot",
                    Resource.resource_id == instance_id,
                    Resource.tenant_id == owner[0],
                    Resource.subject_id == owner[1],
                    Resource.payload["leaseId"].as_string() == lease_id,
                )
            )

    async def find(
        self, kind: str, resource_id: str
    ) -> tuple[tuple[str, str], dict[str, Any]] | None:
        async with self.sessions() as session:
            record = await session.scalar(
                select(Resource).where(
                    and_(Resource.kind == kind, Resource.resource_id == resource_id)
                )
            )
            if record is None:
                return None
            return (record.tenant_id, record.subject_id), dict(record.payload)

    async def enqueue(
        self, job_id: str, kind: str, owner: tuple[str, str], payload: dict[str, Any]
    ) -> None:
        async with self.sessions.begin() as session:
            session.add(
                DurableJob(
                    job_id=job_id,
                    kind=kind,
                    tenant_id=owner[0],
                    subject_id=owner[1],
                    payload=payload,
                    status="queued",
                )
            )

    async def get_job(self, job_id: str, owner: tuple[str, str]) -> DurableJob | None:
        async with self.sessions() as session:
            record = await session.get(DurableJob, job_id)
            if record is None or (record.tenant_id, record.subject_id) != owner:
                return None
            session.expunge(record)
            return record

    async def list_jobs(self, kind: str, owner: tuple[str, str]) -> Sequence[DurableJob]:
        async with self.sessions() as session:
            result = await session.scalars(
                select(DurableJob)
                .where(
                    and_(
                        DurableJob.kind == kind,
                        DurableJob.tenant_id == owner[0],
                        DurableJob.subject_id == owner[1],
                    )
                )
                .order_by(DurableJob.created_at.desc())
            )
            records = list(result)
            for record in records:
                session.expunge(record)
            return records

    async def claim_job(self, worker_id: str) -> DurableJob | None:
        async with self.sessions.begin() as session:
            if self.engine.dialect.name == "sqlite":
                # SQLite ignores FOR UPDATE; reserve the write lock before selecting.
                await session.execute(text("BEGIN IMMEDIATE"))
            stale = utcnow() - timedelta(minutes=5)
            query = (
                select(DurableJob)
                .where(
                    or_(
                        DurableJob.status == "queued",
                        and_(
                            DurableJob.status == "running",
                            or_(DurableJob.heartbeat_at.is_(None), DurableJob.heartbeat_at < stale),
                        ),
                    )
                )
                .order_by(DurableJob.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            record = await session.scalar(query)
            if record is None:
                return None
            record.status = "running"
            record.worker_id = worker_id
            record.started_at = utcnow()
            record.heartbeat_at = utcnow()
            await session.flush()
            session.expunge(record)
            return record

    async def heartbeat_job(self, job_id: str, worker_id: str) -> None:
        async with self.sessions.begin() as session:
            record = await session.get(DurableJob, job_id)
            if record is not None and record.worker_id == worker_id and record.status == "running":
                record.heartbeat_at = utcnow()

    async def finish_job(
        self,
        job_id: str,
        *,
        status: str,
        result: dict[str, Any] | None = None,
        error: dict[str, Any] | None = None,
    ) -> None:
        async with self.sessions.begin() as session:
            record = await session.get(DurableJob, job_id)
            if record is None:
                return
            record.status = status
            record.result = result
            record.error = error
            record.completed_at = utcnow()

    async def append_job_log(self, job_id: str, line: str) -> None:
        async with self.sessions.begin() as session:
            record = await session.get(DurableJob, job_id)
            if record is not None:
                record.logs = (record.logs + line + "\n")[-1_000_000:]

    async def cancel_job(self, job_id: str, owner: tuple[str, str]) -> bool:
        async with self.sessions.begin() as session:
            record = await session.get(DurableJob, job_id)
            if record is None or (record.tenant_id, record.subject_id) != owner:
                return False
            record.cancel_requested = True
            if record.status == "queued":
                record.status = "cancelled"
                record.completed_at = utcnow()
            return True

    async def job_cancel_requested(self, job_id: str) -> bool:
        async with self.sessions() as session:
            record = await session.get(DurableJob, job_id)
            return record is None or record.cancel_requested

    async def reserve_idempotency(
        self,
        operation_id: str,
        key: str,
        owner: tuple[str, str],
        request_hash: str,
    ) -> tuple[str, int | None, dict[str, Any] | None]:
        identity = (operation_id, key, owner[0], owner[1])
        async with self.sessions() as session:
            session.add(
                IdempotencyRecord(
                    operation_id=operation_id,
                    idempotency_key=key,
                    tenant_id=owner[0],
                    subject_id=owner[1],
                    request_hash=request_hash,
                )
            )
            try:
                await session.commit()
                return "new", None, None
            except IntegrityError:
                await session.rollback()
            record = await session.get(IdempotencyRecord, identity)
            assert record is not None
            if record.request_hash != request_hash:
                return "conflict", None, None
            if record.state == "complete":
                return "complete", record.status_code, record.response
            return "in_progress", None, None

    async def complete_idempotency(
        self,
        operation_id: str,
        key: str,
        owner: tuple[str, str],
        status_code: int,
        response: dict[str, Any],
    ) -> None:
        async with self.sessions.begin() as session:
            record = await session.get(IdempotencyRecord, (operation_id, key, owner[0], owner[1]))
            if record is not None:
                record.state = "complete"
                record.status_code = status_code
                record.response = response
