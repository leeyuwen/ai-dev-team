from __future__ import annotations

"""
ProjectService — 数据访问层，封装所有项目存储操作。

用法:
    from services import ProjectService
    svc = ProjectService()
    proj = svc.create(requirement="创建一个计算器")
    svc.update(proj["id"], spec="...")
    svc.save_code(proj["id"], "print('hello')")
"""
import contextlib
import datetime
import json
import os
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Optional

BASE_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
DB_PATH = WORKSPACE_DIR / "projects.db"

ALLOWED_UPDATE_FIELDS = (
    "spec", "architecture", "test_report", "deployment_plan",
    "status", "agents", "code_path",
)


class ProjectService:
    """项目存储服务 — SQLite + 文件系统。"""

    # ── context manager ───────────────────────────────────────────────────────

    @contextlib.contextmanager
    def _conn(self):
        """线程安全的 SQLite 连接上下文管理器。"""
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ── init ─────────────────────────────────────────────────────────────────

    def init(self):
        """确保 workspace 目录和 DB schema 存在。"""
        WORKSPACE_DIR.mkdir(exist_ok=True)
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id              TEXT PRIMARY KEY,
                    name            TEXT NOT NULL,
                    created_at      TEXT NOT NULL,
                    updated_at      TEXT NOT NULL,
                    status          TEXT NOT NULL DEFAULT 'draft',
                    requirement     TEXT NOT NULL DEFAULT '',
                    spec            TEXT NOT NULL DEFAULT '',
                    architecture    TEXT NOT NULL DEFAULT '',
                    test_report     TEXT NOT NULL DEFAULT '',
                    deployment_plan TEXT NOT NULL DEFAULT '',
                    agents          TEXT NOT NULL DEFAULT '[]',
                    code_path       TEXT NOT NULL DEFAULT ''
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at)")
            conn.commit()

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _slugify(text: str) -> str:
        """需求文本 → 安全目录名。"""
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)
        text = re.sub(r"\s+", "-", text.strip())
        text = re.sub(r"-+", "-", text)
        return text[:40] or "project"

    @staticmethod
    def _unique_name(base: str, conn: sqlite3.Connection) -> str:
        """返回不冲突的项目名。"""
        name, counter = base, 1
        while conn.execute("SELECT COUNT(*) FROM projects WHERE name = ?", (name,)).fetchone()[0] > 0:
            name = f"{base}-{counter}"
            counter += 1
        return name

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict:
        cols = (
            "id", "name", "created_at", "updated_at", "status",
            "requirement", "spec", "architecture",
            "test_report", "deployment_plan", "agents", "code_path",
        )
        d = dict(zip(cols, row))
        d["agents"] = json.loads(d["agents"])
        return d

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def create(self, requirement: str, agents: list = None) -> dict:
        """创建新项目，返回项目字典（含 id, name）。"""
        pid = str(uuid.uuid4())[:8]
        slug = self._slugify(requirement)
        with self._conn() as conn:
            name = self._unique_name(slug, conn)
            now = datetime.datetime.now().isoformat(timespec="seconds")
            conn.execute("""
                INSERT INTO projects
                    (id, name, created_at, updated_at, status, requirement, agents)
                VALUES (?, ?, ?, ?, 'draft', ?, ?)
            """, (pid, name, now, now, requirement, json.dumps(agents or [], ensure_ascii=False)))
            conn.commit()
            row = conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
            return self._row_to_dict(row)

    def get(self, pid: str) -> Optional[dict]:
        """按 id 查项目，不存在返回 None。"""
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
            return self._row_to_dict(row) if row else None

    def list(self, limit: int = 50, offset: int = 0) -> list:
        """分页列出所有项目（倒序）。"""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def update(self, pid: str, **fields) -> dict:
        """
        更新指定字段。允许的字段: spec, architecture, test_report,
        deployment_plan, status, agents, code_path。
        """
        update_cols = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
        if not update_cols:
            raise ValueError(f"No valid fields to update. Allowed: {ALLOWED_UPDATE_FIELDS}")

        update_cols["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        set_clause = ", ".join(f"{k} = ?" for k in update_cols)
        vals = list(update_cols.values()) + [pid]

        with self._conn() as conn:
            conn.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", vals)
            conn.commit()
            row = conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
            return self._row_to_dict(row)

    def search(self, keyword: str, limit: int = 20) -> list:
        """在 requirement / spec / name 中全文搜索。"""
        pat = f"%{re.escape(keyword)}%"
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM projects
                WHERE requirement LIKE ? OR spec LIKE ? OR name LIKE ?
                ORDER BY created_at DESC LIMIT ?
            """, (pat, pat, pat, limit)).fetchall()
            return [self._row_to_dict(r) for r in rows]

    # ── code ─────────────────────────────────────────────────────────────────

    def save_code(self, pid: str, code: str) -> str:
        """将代码写入 workspace/{name}/code/main.py，返回绝对路径。"""
        with self._conn() as conn:
            row = conn.execute("SELECT name FROM projects WHERE id = ?", (pid,)).fetchone()
            if not row:
                raise ValueError(f"Project {pid} not found")

        code_dir = WORKSPACE_DIR / row["name"] / "code"
        code_dir.mkdir(parents=True, exist_ok=True)
        dest = code_dir / "main.py"
        dest.write_text(code, encoding="utf-8")
        (code_dir / "__init__.py").write_text("", encoding="utf-8")

        self.update(pid, code_path=str(dest))
        return str(dest)

    def get_code_path(self, pid: str) -> Optional[str]:
        """返回项目代码路径，不存在返回 None。"""
        with self._conn() as conn:
            row = conn.execute("SELECT code_path FROM projects WHERE id = ?", (pid,)).fetchone()
            return row["code_path"] if row else None

    def get_code(self, pid: str) -> Optional[str]:
        """读取项目代码内容，不存在返回 None。"""
        path = self.get_code_path(pid)
        if not path or not os.path.exists(path):
            return None
        return Path(path).read_text(encoding="utf-8")


# ── 单一全局实例 ────────────────────────────────────────────────────────────────
svc = ProjectService()
