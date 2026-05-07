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

    return dict(row)


def init_catalog() -> None:
    db_dir = os.path.dirname(CATALOG_DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge_bases (
                id TEXT PRIMARY KEY,
                giturl TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )


def create_knowledge_base(giturl: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
    knowledge_base_id = str(uuid.uuid4())
    now = _utcnow()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO knowledge_bases (id, giturl, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (knowledge_base_id, giturl, name, description, now, now),
        )

    return get_knowledge_base(knowledge_base_id)


def list_knowledge_bases() -> List[Dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, giturl, name, description, created_at, updated_at
            FROM knowledge_bases
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_knowledge_base(knowledge_base_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, giturl, name, description, created_at, updated_at
            FROM knowledge_bases
            WHERE id = ?
            """,
            (knowledge_base_id,),
        ).fetchone()

    return _row_to_dict(row)


def update_knowledge_base(
    knowledge_base_id: str,
    giturl: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    current = get_knowledge_base(knowledge_base_id)
    if current is None:
        return None

    now = _utcnow()
    with _connect() as connection:
        connection.execute(
            """
            UPDATE knowledge_bases
            SET giturl = ?,
                name = ?,
                description = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                current["giturl"] if giturl is None else giturl,
                current["name"] if name is None else name,
                current["description"] if description is None else description,
                now,
                knowledge_base_id,
            ),
        )

    return get_knowledge_base(knowledge_base_id)


def delete_knowledge_base(knowledge_base_id: str) -> bool:
    with _connect() as connection:
        result = connection.execute(
            """
            DELETE FROM knowledge_bases
            WHERE id = ?
            """,
            (knowledge_base_id,),
        )

    return result.rowcount > 0
