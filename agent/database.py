import sqlite3
import json
import uuid
from datetime import datetime
from config import DATABASE_PATH

_connection = None


def get_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _init_tables()
    return _connection


def _init_tables():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS project (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            context TEXT DEFAULT '',
            mode TEXT DEFAULT 'pm',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS requirement (
            id TEXT PRIMARY KEY,
            project_id TEXT REFERENCES project(id),
            title TEXT NOT NULL,
            detail TEXT DEFAULT '',
            actors TEXT DEFAULT '[]',
            priority TEXT DEFAULT 'P2',
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS diagram (
            id TEXT PRIMARY KEY,
            project_id TEXT REFERENCES project(id),
            requirement_id TEXT DEFAULT '',
            type TEXT NOT NULL,
            title TEXT DEFAULT '',
            plantuml_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


def create_project(name: str, context: str = "", mode: str = "pm") -> dict:
    conn = get_connection()
    project_id = str(uuid.uuid4())[:8]
    conn.execute(
        "INSERT INTO project (id, name, context, mode) VALUES (?, ?, ?, ?)",
        (project_id, name, context, mode),
    )
    conn.commit()
    return get_project(project_id)


def get_project(project_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM project WHERE id = ?", (project_id,)).fetchone()
    if row is None:
        return None
    return dict(row)


def list_projects() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM project ORDER BY updated_at DESC").fetchall()
    return [dict(r) for r in rows]


def update_project(project_id: str, **kwargs) -> dict | None:
    conn = get_connection()
    allowed = {"name", "context", "mode"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_project(project_id)
    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [project_id]
    conn.execute(f"UPDATE project SET {set_clause} WHERE id = ?", values)
    conn.commit()
    return get_project(project_id)


def save_requirement(
    project_id: str, title: str, detail: str = "", actors: list | None = None,
    priority: str = "P2", status: str = "draft"
) -> dict:
    conn = get_connection()
    req_id = str(uuid.uuid4())[:8]
    actors_json = json.dumps(actors or [], ensure_ascii=False)
    conn.execute(
        "INSERT INTO requirement (id, project_id, title, detail, actors, priority, status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (req_id, project_id, title, detail, actors_json, priority, status),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM requirement WHERE id = ?", (req_id,)).fetchone()
    return dict(row)


def list_requirements(project_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM requirement WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def save_diagram(
    project_id: str, type_: str, plantuml_code: str,
    requirement_id: str = "", title: str = ""
) -> dict:
    conn = get_connection()
    diag_id = str(uuid.uuid4())[:8]
    conn.execute(
        "INSERT INTO diagram (id, project_id, requirement_id, type, title, plantuml_code) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (diag_id, project_id, requirement_id, type_, title, plantuml_code),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM diagram WHERE id = ?", (diag_id,)).fetchone()
    return dict(row)


def list_diagrams(project_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM diagram WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    return [dict(r) for r in rows]
