# store.py
import sqlite3
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import os
from pathlib import Path

DB_FILE = os.getenv(
    "DAILYJOURNAL_DB_PATH",
    str(Path.home() / ".local" / "share" / "dailyjournal" / "coachscribe.db"),
)

def _conn() -> sqlite3.Connection:
    db_path = Path(DB_FILE)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db() -> None:
    with _conn() as con:
        con.execute(
            """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TEXT NOT NULL,          -- YYYY-MM-DD
            session_type TEXT NOT NULL,          -- 'am' or 'pm'
            raw_transcript TEXT NOT NULL,
            summary TEXT NOT NULL,

            -- AM commitments
            work_one_thing TEXT,
            family_one_thing TEXT,
            focus_guardrail TEXT,
            if_then_plan TEXT,

            -- PM outcomes
            work_done INTEGER,                   -- 0/1
            family_done INTEGER,                 -- 0/1
            focus_done INTEGER,                  -- 0/1
            distraction_cause TEXT,
            improvement TEXT,
            tomorrow_focus TEXT,

            forree_text TEXT,
            created_at TEXT NOT NULL
        )
        """
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_date_type ON sessions(session_date, session_type)"
        )


def insert_session(payload: Dict[str, Any]) -> None:
    """Insert a session row."""
    with _conn() as con:
        con.execute(
            """
        INSERT INTO sessions (
            session_date, session_type, raw_transcript, summary,
            work_one_thing, family_one_thing, focus_guardrail, if_then_plan,
            work_done, family_done, focus_done,
            distraction_cause, improvement, tomorrow_focus, free_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                payload["session_date"],
                payload["session_type"],
                payload["raw_transcript"],
                payload["summary"],
                payload.get("work_one_thing"),
                payload.get("family_one_thing"),
                payload.get("focus_guardrail"),
                payload.get("if_then_plan"),
                payload.get("work_done"),
                payload.get("family_done"),
                payload.get("focus_done"),
                payload.get("distraction_cause"),
                payload.get("improvement"),
                payload.get("tomorrow_focus"),
                payload.get("free_text"),
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )


def get_latest_am(session_date: str) -> Optional[Dict[str, Any]]:
    with _conn() as con:
        cur = con.execute(
            """
            SELECT work_one_thing, family_one_thing, focus_guardrail, if_then_plan, summary
            FROM sessions
            WHERE session_date = ? AND session_type = 'am'
            ORDER BY id DESC
            LIMIT 1
        """,
            (session_date,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "work_one_thing": row[0],
        "family_one_thing": row[1],
        "focus_guardrail": row[2],
        "if_then_plan": row[3],
        "summary": row[4],
    }


def get_last_n_summaries(n: int = 10) -> List[Dict[str, str]]:
    with _conn() as con:
        cur = con.execut

def get_latest_pm_with_tomorrow_focus() -> Optional[Dict[str, Any]]:
    with _conn() as con:
        cur = con.execute(
            """
            SELECT session_date, tomorrow_focus
            FROM sessions
            WHERE session_type = 'pm' AND tomorrow_focus IS NOT NULL AND tomorrow_focus != ''
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()

    if not row:
        return None

    return {"session_date": row[0], "tomorrow_focus": row[1]}

def delete_db_file() -> bool:
    from pathlib import Path
    p = Path(DB_FILE).expanduser()
    if p.exists():
        p.unlink()
        return True
    return False

