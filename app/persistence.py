from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app.config import settings
from app.schemas import ApprovalDecision, ApprovalReviewRecord, ToolTrace


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteStore:
    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path or settings.sqlite_db_path)
        self._initialized = False

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            self.init_db(conn)
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self, conn: sqlite3.Connection | None = None) -> None:
        if self._initialized and conn is None:
            return

        def _create(target: sqlite3.Connection) -> None:
            target.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tool_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    tool_args_json TEXT NOT NULL,
                    result_summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approval_requests (
                    approval_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    route TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approval_review_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    approval_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    reason TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

        if conn is not None:
            _create(conn)
            self._initialized = True
            return

        with sqlite3.connect(self.db_path) as local_conn:
            _create(local_conn)
            local_conn.commit()
        self._initialized = True

    def reset(self) -> None:
        if self.db_path.exists():
            self.db_path.unlink()
        self._initialized = False

    def ensure_session(self, session_id: str) -> None:
        now = _utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (session_id, created_at, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET updated_at = excluded.updated_at
                """,
                (session_id, now, now),
            )

    def record_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.ensure_session(session_id)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (session_id, role, content, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, json.dumps(metadata or {}), _utc_now()),
            )

    def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        self.ensure_session(session_id)
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT role, content, metadata_json, created_at FROM messages WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
        return [
            {
                "role": row["role"],
                "content": row["content"],
                "metadata": json.loads(row["metadata_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def record_tool_trace(self, session_id: str, trace: ToolTrace) -> None:
        self.ensure_session(session_id)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO tool_traces (session_id, tool_name, tool_args_json, result_summary, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, trace.tool_name, json.dumps(trace.tool_args), trace.result_summary, _utc_now()),
            )

    def get_tool_traces(self, session_id: str) -> list[ToolTrace]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT tool_name, tool_args_json, result_summary FROM tool_traces WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
        return [
            ToolTrace(
                tool_name=row["tool_name"],
                tool_args=json.loads(row["tool_args_json"]),
                result_summary=row["result_summary"],
            )
            for row in rows
        ]

    def record_approval_request(
        self,
        session_id: str,
        route: str,
        approval_id: str,
        action_type: str,
        status: str,
        payload: dict[str, Any],
    ) -> None:
        self.ensure_session(session_id)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO approval_requests
                    (approval_id, session_id, route, action_type, status, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (approval_id, session_id, route, action_type, status, json.dumps(payload), _utc_now()),
            )

    def get_approval_request(self, approval_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT approval_id, session_id, route, action_type, status, payload_json, created_at
                FROM approval_requests WHERE approval_id = ?
                """,
                (approval_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "approval_id": row["approval_id"],
            "session_id": row["session_id"],
            "route": row["route"],
            "action_type": row["action_type"],
            "status": row["status"],
            "payload": json.loads(row["payload_json"]),
            "created_at": row["created_at"],
        }

    def record_approval_review(self, decision: ApprovalDecision, session_id: str) -> ApprovalReviewRecord:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO approval_review_events
                    (approval_id, session_id, decision, reviewer, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.approval_id,
                    session_id,
                    decision.decision,
                    decision.reviewer,
                    decision.reason,
                    _utc_now(),
                ),
            )
        return ApprovalReviewRecord(
            approval_id=decision.approval_id,
            session_id=session_id,
            decision=decision.decision,
            reviewer=decision.reviewer,
            reason=decision.reason,
        )

    def get_approval_reviews(self, approval_id: str) -> list[ApprovalReviewRecord]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT approval_id, session_id, decision, reviewer, reason
                FROM approval_review_events WHERE approval_id = ? ORDER BY id
                """,
                (approval_id,),
            ).fetchall()
        return [
            ApprovalReviewRecord(
                approval_id=row["approval_id"],
                session_id=row["session_id"],
                decision=row["decision"],
                reviewer=row["reviewer"],
                reason=row["reason"],
            )
            for row in rows
        ]

    def record_ticket(self, session_id: str, ticket: dict[str, Any]) -> None:
        self.ensure_session(session_id)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tickets
                    (ticket_id, session_id, status, priority, summary, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket["ticket_id"],
                    session_id,
                    ticket["status"],
                    ticket["priority"],
                    ticket["summary"],
                    ticket["reason"],
                    _utc_now(),
                ),
            )

    def get_ticket(self, ticket_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT ticket_id, session_id, status, priority, summary, reason, created_at
                FROM tickets WHERE ticket_id = ?
                """,
                (ticket_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)
