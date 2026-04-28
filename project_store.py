"""
Project storage layer: SQLite for metadata + filesystem for code.

Schema:
  projects(id, name, created_at, updated_at, status,
           requirement, spec, architecture,
           test_report, deployment_plan,
           agents, code_path)
"""

import sqlite3, json, os, re, uuid, datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
WORKSPACE_DIR = BASE_DIR / "workspace"
DB_PATH = WORKSPACE_DIR / "projects.db"

# ── init ─────────────────────────────────────────────────────────────────────

def init():
    """Create workspace dir and DB schema if they don't exist."""
    WORKSPACE_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'draft',
            requirement TEXT NOT NULL DEFAULT '',
            spec        TEXT NOT NULL DEFAULT '',
            architecture TEXT NOT NULL DEFAULT '',
            test_report TEXT NOT NULL DEFAULT '',
            deployment_plan TEXT NOT NULL DEFAULT '',
            agents      TEXT NOT NULL DEFAULT '[]',
            code_path   TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at)")
    conn.commit()
    conn.close()

# ── slug helper ──────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Turn a requirement string into a safe directory name."""
    # Remove markdown/emoji, collapse whitespace, take first 30 meaningful chars
    text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)   # keep Chinese + word chars
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    slug = text[:40]
    return slug or "project"

def _unique_name(base: str, conn) -> str:
    """Return a name that doesn't collide with existing rows."""
    name = base
    counter = 1
    while True:
        cur = conn.execute(
            "SELECT COUNT(*) FROM projects WHERE name = ?", (name,)
        ).fetchone()[0]
        if cur == 0:
            return name
        name = f"{base}-{counter}"
        counter += 1

# ── CRUD ─────────────────────────────────────────────────────────────────────

def create_project(requirement: str, agents: list[str] = None) -> dict:
    """
    Create a new project record. Returns the project dict (includes id, name).
    Does NOT write code — use save_code() for that.
    """
    conn = sqlite3.connect(str(DB_PATH))
    pid   = str(uuid.uuid4())[:8]
    slug  = _slugify(requirement)
    name  = _unique_name(slug, conn)
    now   = datetime.datetime.now().isoformat(timespec="seconds")

    conn.execute("""
        INSERT INTO projects (id, name, created_at, updated_at, status, requirement, agents)
        VALUES (?, ?, ?, ?, 'draft', ?, ?)
    """, (pid, name, now, now, requirement, json.dumps(agents or [], ensure_ascii=False)))
    conn.commit()
    row = _row_to_dict(conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone(), conn)
    conn.close()
    return row


def update_project(pid: str, **fields) -> dict:
    """Update one or more columns on a project. Returns updated row."""
    conn = sqlite3.connect(str(DB_PATH))
    now  = datetime.datetime.now().isoformat(timespec="seconds")
    allowed = ("spec", "architecture", "test_report", "deployment_plan",
               "status", "agents", "code_path")
    update_cols = {k: v for k, v in fields.items() if k in allowed}
    if not update_cols:
        conn.close()
        raise ValueError("No valid fields to update")
    update_cols["updated_at"] = now
    set_clause = ", ".join(f"{k} = ?" for k in update_cols)
    vals = list(update_cols.values()) + [pid]
    conn.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", vals)
    conn.commit()
    row = _row_to_dict(conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone(), conn)
    conn.close()
    return row


def get_project(pid: str) -> Optional[dict]:
    conn = sqlite3.connect(str(DB_PATH))
    row  = conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_dict(row, conn if False else None)


def list_projects(limit: int = 50, offset: int = 0) -> list[dict]:
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r, None) for r in rows]


def _row_to_dict(row, conn) -> dict:
    """Convert a DB row (from fetchone or fetchall) to a dict."""
    cols = ("id", "name", "created_at", "updated_at", "status",
            "requirement", "spec", "architecture",
            "test_report", "deployment_plan", "agents", "code_path")
    d = dict(zip(cols, row))
    d["agents"] = json.loads(d["agents"])
    return d


# ── code storage ─────────────────────────────────────────────────────────────

def save_code(pid: str, code: str) -> str:
    """
    Write code string to workspace/{name}/main.py (and __init__.py).
    Returns the absolute code_path.
    """
    conn = sqlite3.connect(str(DB_PATH))
    proj = conn.execute("SELECT name FROM projects WHERE id = ?", (pid,)).fetchone()
    conn.close()
    if not proj:
        raise ValueError(f"Project {pid} not found")

    proj_dir = WORKSPACE_DIR / proj[0]
    code_dir  = proj_dir / "code"
    code_dir.mkdir(parents=True, exist_ok=True)

    dest = code_dir / "main.py"
    dest.write_text(code, encoding="utf-8")
    (code_dir / "__init__.py").write_text("", encoding="utf-8")

    # update code_path in DB
    conn2 = sqlite3.connect(str(DB_PATH))
    conn2.execute("UPDATE projects SET code_path = ?, updated_at = ? WHERE id = ?",
                  (str(dest), datetime.datetime.now().isoformat(timespec="seconds"), pid))
    conn2.commit()
    conn2.close()

    return str(dest)


def get_code_path(pid: str) -> Optional[str]:
    """Return the absolute path to the project's main.py, or None."""
    conn = sqlite3.connect(str(DB_PATH))
    row  = conn.execute("SELECT code_path FROM projects WHERE id = ?", (pid,)).fetchone()
    conn.close()
    return row[0] if row else None


# ── index ────────────────────────────────────────────────────────────────────

def search_projects(keyword: str, limit: int = 20) -> list[dict]:
    """Full-text search across requirement + spec."""
    conn = sqlite3.connect(str(DB_PATH))
    pattern = f"%{keyword}%"
    rows = conn.execute("""
        SELECT * FROM projects
        WHERE requirement LIKE ? OR spec LIKE ? OR name LIKE ?
        ORDER BY created_at DESC LIMIT ?
    """, (pattern, pattern, pattern, limit)).fetchall()
    conn.close()
    return [_row_to_dict(r, None) for r in rows]
