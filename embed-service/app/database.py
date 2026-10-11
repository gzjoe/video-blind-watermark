"""Embed Service - Database"""
import aiosqlite
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "tasks.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                original_filename TEXT,
                watermark_text TEXT,
                password_img INTEGER,
                password_wm INTEGER,
                wm_bit_len INTEGER,
                output_path TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def create_task(task_id: str, original_filename: str, watermark_text: str,
                      password_img: int, password_wm: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO tasks (id, original_filename, watermark_text, password_img, password_wm)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, original_filename, watermark_text, password_img, password_wm))
        await db.commit()


async def update_task(task_id: str, status: str, output_path: Optional[str] = None,
                      wm_bit_len: Optional[int] = None, error_message: Optional[str] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE tasks
            SET status = ?, output_path = COALESCE(?, output_path),
                wm_bit_len = COALESCE(?, wm_bit_len),
                error_message = COALESCE(?, error_message)
            WHERE id = ?
        """, (status, output_path, wm_bit_len, error_message, task_id))
        await db.commit()


async def get_task(task_id: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
