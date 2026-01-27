from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# 路径配置
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"

def ensure_data_directory_exists() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

@contextmanager
def get_db():
    ensure_data_directory_exists()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    ensure_data_directory_exists()
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
        """)
        conn.commit()

# --- CRUD 操作 ---

def insert_note(content: str) -> int:
    with get_db() as conn:
        cursor = conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        conn.commit()
        return cursor.lastrowid

def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row) if row else None

def list_notes() -> List[Dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    with get_db() as conn:
        ids = []
        for item in items:
            cursor = conn.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item)
            )
            ids.append(cursor.lastrowid)
        conn.commit()
        return ids

def list_action_items(note_id: Optional[int] = None) -> List[Dict[str, Any]]:
    with get_db() as conn:
        if note_id is None:
            rows = conn.execute("SELECT * FROM action_items ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute("SELECT * FROM action_items WHERE note_id = ? ORDER BY id DESC", (note_id,)).fetchall()
        return [dict(r) for r in rows]

def mark_action_item_done(action_item_id: int, done: bool) -> bool:
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id)
        )
        conn.commit()
        return cursor.rowcount > 0
