import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config.config import CATALOG_DB_PATH


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(CATALOG_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None

    item = dict(row)
    if "is_private" in item:
        item["is_private"] = bool(item["is_private"])
    return item


def init_catalog() -> None:
    db_dir = os.path.dirname(CATALOG_DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge_bases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS kb_sources (
                id TEXT PRIMARY KEY,
                knowledge_base_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                repo_url TEXT,
                branch TEXT,
                path_prefix TEXT,
                is_private INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                last_indexed_at TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS kb_ingestions (
                id TEXT PRIMARY KEY,
                knowledge_base_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                files_seen INTEGER NOT NULL DEFAULT 0,
                files_indexed INTEGER NOT NULL DEFAULT 0,
                chunks_indexed INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
                FOREIGN KEY (source_id) REFERENCES kb_sources(id) ON DELETE CASCADE
            );
            """
        )


def create_knowledge_base(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    knowledge_base_id = str(uuid.uuid4())
    now = _utcnow()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO knowledge_bases (id, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (knowledge_base_id, name, description, now, now),
        )

    return get_knowledge_base(knowledge_base_id)


def list_knowledge_bases() -> List[Dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, name, description, created_at, updated_at
            FROM knowledge_bases
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_knowledge_base(knowledge_base_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, name, description, created_at, updated_at
            FROM knowledge_bases
            WHERE id = ?
            """,
            (knowledge_base_id,),
        ).fetchone()

    return _row_to_dict(row)


def get_github_source(
    knowledge_base_id: str,
    repo_url: str,
    branch: Optional[str],
) -> Optional[Dict[str, Any]]:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, knowledge_base_id, source_type, repo_url, branch, path_prefix,
                   is_private, status, last_indexed_at, error_message, created_at, updated_at
            FROM kb_sources
            WHERE knowledge_base_id = ?
              AND source_type = 'github'
              AND repo_url = ?
              AND branch IS ?
            """,
            (knowledge_base_id, repo_url, branch),
        ).fetchone()

    return _row_to_dict(row)


def create_github_source(
    knowledge_base_id: str,
    repo_url: str,
    branch: Optional[str],
    is_private: bool,
) -> Dict[str, Any]:
    existing = get_github_source(knowledge_base_id, repo_url, branch)
    if existing is not None:
        return existing

    source_id = str(uuid.uuid4())
    now = _utcnow()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO kb_sources (
                id, knowledge_base_id, source_type, repo_url, branch, path_prefix,
                is_private, status, last_indexed_at, error_message, created_at, updated_at
            )
            VALUES (?, ?, 'github', ?, ?, NULL, ?, 'pending', NULL, NULL, ?, ?)
            """,
            (source_id, knowledge_base_id, repo_url, branch, int(is_private), now, now),
        )

    return get_source(source_id)


def list_sources(knowledge_base_id: str) -> List[Dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, knowledge_base_id, source_type, repo_url, branch, path_prefix,
                   is_private, status, last_indexed_at, error_message, created_at, updated_at
            FROM kb_sources
            WHERE knowledge_base_id = ?
            ORDER BY created_at DESC
            """,
            (knowledge_base_id,),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_source(source_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, knowledge_base_id, source_type, repo_url, branch, path_prefix,
                   is_private, status, last_indexed_at, error_message, created_at, updated_at
            FROM kb_sources
            WHERE id = ?
            """,
            (source_id,),
        ).fetchone()

    return _row_to_dict(row)


def create_ingestion(knowledge_base_id: str, source_id: str) -> Dict[str, Any]:
    ingestion_id = str(uuid.uuid4())
    started_at = _utcnow()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO kb_ingestions (
                id, knowledge_base_id, source_id, status, files_seen, files_indexed,
                chunks_indexed, error_message, started_at, finished_at
            )
            VALUES (?, ?, ?, 'running', 0, 0, 0, NULL, ?, NULL)
            """,
            (ingestion_id, knowledge_base_id, source_id, started_at),
        )

    return get_ingestion(ingestion_id)


def get_ingestion(ingestion_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, knowledge_base_id, source_id, status, files_seen, files_indexed,
                   chunks_indexed, error_message, started_at, finished_at
            FROM kb_ingestions
            WHERE id = ?
            """,
            (ingestion_id,),
        ).fetchone()

    return _row_to_dict(row)


def complete_ingestion(
    ingestion_id: str,
    source_id: str,
    files_seen: int,
    files_indexed: int,
    chunks_indexed: int,
) -> Dict[str, Any]:
    now = _utcnow()

    with _connect() as connection:
        connection.execute(
            """
            UPDATE kb_ingestions
            SET status = 'completed',
                files_seen = ?,
                files_indexed = ?,
                chunks_indexed = ?,
                error_message = NULL,
                finished_at = ?
            WHERE id = ?
            """,
            (files_seen, files_indexed, chunks_indexed, now, ingestion_id),
        )
        connection.execute(
            """
            UPDATE kb_sources
            SET status = 'ready',
                last_indexed_at = ?,
                error_message = NULL,
                updated_at = ?
            WHERE id = ?
            """,
            (now, now, source_id),
        )

    return get_ingestion(ingestion_id)


def fail_ingestion(ingestion_id: str, source_id: str, error_message: str) -> Dict[str, Any]:
    now = _utcnow()

    with _connect() as connection:
        connection.execute(
            """
            UPDATE kb_ingestions
            SET status = 'failed',
                error_message = ?,
                finished_at = ?
            WHERE id = ?
            """,
            (error_message, now, ingestion_id),
        )
        connection.execute(
            """
            UPDATE kb_sources
            SET status = 'failed',
                error_message = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (error_message, now, source_id),
        )

    return get_ingestion(ingestion_id)
