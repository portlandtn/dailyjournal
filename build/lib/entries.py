# entries.py
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_sync_dir() -> Optional[Path]:
    sync_dir = os.getenv("DAILYJOURNAL_SYNC_DIR")
    if not sync_dir:
        return None
    p = Path(sync_dir).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def _make_filename(session_date: str, session_type: str, entry_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{session_date}_{session_type}_{ts}_{entry_id}.json"


@dataclass
class Entry:
    id: str
    session_date: str          # YYYY-MM-DD
    session_type: str          # am/pm
    created_at: str            # UTC ISO-ish

    # Always included
    summary: str
    raw_transcript: str

    # AM commitments (optional)
    work_one_thing: Optional[str] = None
    family_one_thing: Optional[str] = None
    focus_guardrail: Optional[str] = None
    if_then_plan: Optional[str] = None

    # PM outcomes (optional)
    work_done: Optional[int] = None
    family_done: Optional[int] = None
    focus_done: Optional[int] = None
    distraction_cause: Optional[str] = None
    improvement: Optional[str] = None
    tomorrow_focus: Optional[str] = None
    free_text: Optional[str] = None


def export_entry(payload: Dict[str, Any]) -> Optional[Path]:
    """
    Writes one immutable JSON entry file into DAILYJOURNAL_SYNC_DIR.
    Returns the file path if written, otherwise None.
    """
    sync_dir = _safe_sync_dir()
    if sync_dir is None:
        return None

    entry_id = uuid4().hex[:12]
    entry = Entry(
        id=entry_id,
        session_date=payload["session_date"],
        session_type=payload["session_type"],
        created_at=_utc_now_iso(),
        summary=payload["summary"],
        raw_transcript=payload["raw_transcript"],

        work_one_thing=payload.get("work_one_thing"),
        family_one_thing=payload.get("family_one_thing"),
        focus_guardrail=payload.get("focus_guardrail"),
        if_then_plan=payload.get("if_then_plan"),

        work_done=payload.get("work_done"),
        family_done=payload.get("family_done"),
        focus_done=payload.get("focus_done"),
        distraction_cause=payload.get("distraction_cause"),
        improvement=payload.get("improvement"),
        tomorrow_focus=payload.get("tomorrow_focus"),
        free_text=payload.get("free_text"),
    )

    file_path = sync_dir / _make_filename(entry.session_date, entry.session_type, entry.id)

    # Write atomically: write temp then rename
    tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(asdict(entry), ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(file_path)

    return file_path

def iter_entry_files() -> list[Path]:
    """
    Returns a sorted list of *.json entry files in the sync dir.
    """
    sync_dir = _safe_sync_dir()
    if sync_dir is None:
        return []
    return sorted([p for p in sync_dir.glob("*.json") if p.is_file()])


def read_entry_file(path: Path) -> dict[str, Any]:
    """
    Reads a single entry JSON file and returns its dict.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def wipe_sync_dir_entries() -> int:
    """
    Deletes all files in DAILYJOURNAL_SYNC_DIR.
    Returns how many files were deleted.
    """
    sync_dir = _safe_sync_dir()
    if sync_dir is None:
        return 0

    deleted = 0
    for p in sync_dir.iterdir():
        if p.is_file():
            p.unlink()
            deleted += 1

    return deleted

