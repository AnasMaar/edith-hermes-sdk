"""Swappable mock state stores."""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol

Owner = tuple[str, str]


class StateStore(Protocol):
    def put(self, kind: str, resource_id: str, owner: Owner, value: dict[str, Any]) -> None: ...

    def get(self, kind: str, resource_id: str, owner: Owner) -> dict[str, Any] | None: ...

    def list(self, kind: str, owner: Owner) -> list[dict[str, Any]]: ...

    def delete(self, kind: str, resource_id: str, owner: Owner) -> bool: ...


class MemoryStateStore:
    def __init__(self) -> None:
        self._values: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    @staticmethod
    def _key(kind: str, resource_id: str, owner: Owner) -> tuple[str, str, str, str]:
        return kind, resource_id, owner[0], owner[1]

    def put(self, kind: str, resource_id: str, owner: Owner, value: dict[str, Any]) -> None:
        self._values[self._key(kind, resource_id, owner)] = json.loads(json.dumps(value))

    def get(self, kind: str, resource_id: str, owner: Owner) -> dict[str, Any] | None:
        value = self._values.get(self._key(kind, resource_id, owner))
        return json.loads(json.dumps(value)) if value is not None else None

    def list(self, kind: str, owner: Owner) -> list[dict[str, Any]]:
        values = [
            value
            for (item_kind, _, tenant, subject), value in self._values.items()
            if item_kind == kind and (tenant, subject) == owner
        ]
        return json.loads(json.dumps(values))

    def delete(self, kind: str, resource_id: str, owner: Owner) -> bool:
        return self._values.pop(self._key(kind, resource_id, owner), None) is not None


class SQLiteStateStore:
    def __init__(self, path: str | Path):
        self._path = str(path)
        self._lock = threading.RLock()
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS resources (
                    kind TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    PRIMARY KEY (kind, resource_id, tenant_id, subject_id)
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=30)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def put(self, kind: str, resource_id: str, owner: Owner, value: dict[str, Any]) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO resources(kind, resource_id, tenant_id, subject_id, value_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(kind, resource_id, tenant_id, subject_id)
                DO UPDATE SET value_json=excluded.value_json
                """,
                (kind, resource_id, owner[0], owner[1], json.dumps(value, separators=(",", ":"))),
            )

    def get(self, kind: str, resource_id: str, owner: Owner) -> dict[str, Any] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """SELECT value_json FROM resources
                   WHERE kind=? AND resource_id=? AND tenant_id=? AND subject_id=?""",
                (kind, resource_id, owner[0], owner[1]),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, kind: str, owner: Owner) -> list[dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows: Iterable[tuple[str]] = connection.execute(
                """SELECT value_json FROM resources
                   WHERE kind=? AND tenant_id=? AND subject_id=? ORDER BY resource_id""",
                (kind, owner[0], owner[1]),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def delete(self, kind: str, resource_id: str, owner: Owner) -> bool:
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """DELETE FROM resources
                   WHERE kind=? AND resource_id=? AND tenant_id=? AND subject_id=?""",
                (kind, resource_id, owner[0], owner[1]),
            )
        return cursor.rowcount > 0
