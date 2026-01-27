# app.py
import os
import sys
from datetime import date
from entries import (
    export_entry, 
    wipe_sync_dir_entries,
    read_entry_file,
    iter_entry_files,
    export_note,
)

from store import (
    init_db,
    insert_session,
    get_latest_am,
    get_latest_am_full,
    get_last_n_summaries,
    get_latest_pm_with_tomorrow_focus,
    delete_db_file,
    # sync tracking for cloud imports
    is_file_imported,
    mark_file_imported,
    insert_session_from_icloud,
    import_note_from_icloud,
    # notes
    get_notes,
    add_note,
)

from prompts import AM_QUESTIONS, PM_QUESTIONS
from coach import run_am, run_pm

APP_VERSION = "0.1.0"

DEFAULT_MODEL = os.getenv("COACHSCRIBE_MODEL", "gpt-4.1-mini")


def ask_questions(questions):
    answers = []
    for q in questions:
        print()
        print(q)
        ans = input("> ").strip()
        answers.append(ans)
    return answers

def ask_multiline(prompt: str) -> str:
    print()
    print(prompt)
    print("End with a single line containing only: .done")
    lines = []
    while True:
        line = input()
        if line.strip() == ".done":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def am_session():
    last_pm = get_latest_pm_with_tomorrow_focus()
    if last_pm and last_pm.get("tomorrow_focus"):
        print("\nLast night you said tomorrow’s focus was:")
        print(f"→ {last_pm['tomorrow_focus']}") 

    today = date.today().isoformat() 
    answers = ask_questions(AM_QUESTIONS)

    additional = ask_multiline("Any additional notes for this morning? (optional)")

    data = run_am(DEFAULT_MODEL, answers)

    payload = {
        "session_date": today,
        "session_type": "am",
        "raw_transcript": data["raw_transcript"],
        "summary": data["summary"],
        "work_one_thing": data.get("work_one_thing"),
        "family_one_thing": data.get("family_one_thing"),
        "if_then_plan": data.get("if_then_plan"),
        "free_text": additional or None,
    }

    insert_session(payload)
    exported = export_entry(payload)
    if exported:
        print(f"\n(cloud) wrote entry file: {exported.name}")

    print("\n--- AM SUMMARY ---")
    print(data["summary"])


def pm_session():
    today = date.today().isoformat()

    am_full = get_latest_am_full(today)
    am = am_full  # reuse for existing logic

    if am_full and am_full.get("free_text"):
        print("\nAM NOTES YOU ADDED:")
        print(am_full["free_text"])
    if am:
        print("\nAM COMMITMENTS")
        print(f"- Work One Thing: {am['work_one_thing']}")
        print(f"- Family One Thing: {am['family_one_thing']}")
        print(f"- If-Then Plan: {am['if_then_plan']}")

        pm_questions = [
            f"You said your Work One Thing was:\n  \"{am['work_one_thing']}\"\nDid you complete it? What’s the proof?",
            f"You said your Family One Thing was:\n  \"{am['family_one_thing']}\"\nDid you do it? What did you do, specifically?",
            "What was the biggest trigger for distraction today (one sentence)?",
            "What’s one adjustment you’ll make tomorrow (one sentence)?",
        ]
    else:
        print("\nNo AM entry found for today — doing a general evening review.\n")

        pm_questions = [
            "What was the ONE thing you most wanted to accomplish today?",
            "Did you accomplish it? What’s the proof or current status?",
            "What’s one adjustment you’ll make tomorrow (one sentence)?",
            "What should tomorrow’s focus be (one sentence)?",
        ]

    answers = ask_questions(pm_questions)
    additional = ask_multiline("Any additional notes for tonight? (optional)")

    append_notes = get_notes(today, "am")
    am_for_llm = dict(am or {})
    if append_notes:
        am_for_llm["append_notes"] = append_notes

    data = run_pm(DEFAULT_MODEL, am_for_llm, answers)

    payload = {
        "session_date": today,
        "session_type": "pm",
        "raw_transcript": data["raw_transcript"],
        "summary": data["summary"],
        "work_done": int(data.get("work_done", 0)),
        "family_done": int(data.get("family_done", 0)),
        "distraction_cause": data.get("distraction_cause"),
        "improvement": data.get("improvement"),
        "tomorrow_focus": data.get("tomorrow_focus"),
        "free_text": additional or None,
    }

    insert_session(payload)
    exported = export_entry(payload)
    if exported:
        print(f"\n(cloud) wrote entry file {exported.name}")

    print("\n--- PM SUMMARY ---")
    print(data["summary"])


def show_last():
    rows = get_last_n_summaries(10)
    print("\nRECENT ENTRIES")
    for r in rows:
        first_line = r["summary"].splitlines()[0]
        print(f"{r['date']} [{r['type'].upper()}] {first_line}")

def sync_from_icloud_on_startup() -> None:
    files = iter_entry_files()
    if not files:
        return

    imported = 0
    skipped = 0

    for path in files:
        name = path.name

        if is_file_imported(name):
            skipped += 1
            continue

        try:
            entry = read_entry_file(path)

            if entry.get("entry_kind") == "note":
                import_note_from_icloud(entry)
            else:
                insert_session_from_icloud(entry)

            mark_file_imported(name)
            imported += 1
        except Exception as e:
            # Don't crash the whole app because one file is bad
            print(f"(sync) WARNING: failed to import {name}: {e}")

    if imported:
        print(f"(sync) Imported {imported} new cloud entr{'y' if imported == 1 else 'ies'}.")

def _extract_am_derail_risk(raw_transcript: str) -> str | None:
    # raw_transcript lines look like: "AM Q3: <text>"
    for line in (raw_transcript or "").splitlines():
        if line.startswith("AM Q3:"):
            return line.replace("AM Q3:", "", 1).strip()
    return None

def append_note(note_text_arg: str | None = None) -> None:
    today = date.today().isoformat()

    am_full = get_latest_am_full(today)

    print("\nYou mentioned you would like to:")
    if am_full:
        if am_full.get("family_one_thing"):
            print(f"- {am_full['family_one_thing']}")
        if am_full.get("work_one_thing"):
            print(f"- {am_full['work_one_thing']}")
        if am_full.get("if_then_plan"):
            print(f"- {am_full['if_then_plan']}")

        risk = _extract_am_derail_risk(am_full.get("raw_transcript", ""))
        if risk:
            print(f"- Derail risk: {risk}")
    else:
        print("- (No AM entry found for today yet.)")
        print("- (Run: dailyjournal am)")

    existing_notes = get_notes(today, "am")
    if existing_notes:
        print("\nExisting notes so far today:")
        for n in existing_notes:
            first = n.splitlines()[0]
            print(f"- {first}")

    # --- one-liner mode ---
    if note_text_arg and note_text_arg.strip():
        note_text = note_text_arg.strip()
    else:
        print("\nAdd a note about what's happening right now.")
        print("End with a single line containing only: .done\n")

        lines = []
        while True:
            line = input()
            if line.strip() == ".done":
                break
            lines.append(line)

        note_text = "\n".join(lines).strip()

    if not note_text:
        print("No note entered.")
        return

    add_note(today, "am", note_text)

    exported = export_note(today, "am", note_text)
    if exported:
        print(f"\n(cloud) wrote note file: {exported.name}")

    print("\n--- NOTE APPENDED ---")

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set in the environment.")
        sys.exit(1)

    init_db()
    sync_from_icloud_on_startup()

    if "--version" in sys.argv or "-V" in sys.argv:
        print(APP_VERSION)
        sys.exit(0)

    if len(sys.argv) < 2 or sys.argv[1] in ("help", "-h", "--help"):
        print("""
dailyjournal — AM/PM journaling with accountability

Usage:
  dailyjournal am               Run morning session
  dailyjournal pm               Run evening session
  dailyjournal last             Show recent summaries
  dailyjournal help             Show this help
  dailyjournal free_entry       Enter free text, not used with a template
  dailyjournal free             Enter free text, not used with a template
  dailyjournal free_text        Enter free text, not used with a template
  dailyjournal wipe [--icloud]  Erases the local journal, (also wipes the icloud sync if icloud argument is passed)
  dailyjournal append [text]    Append a note to today's AM (one-liner or multiline)

Examples:
  dailyjournal am
  dailyjournal pm
  dailyjournal append "Got 3178 done; follow up tomorrow"
""")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "am":
        am_session()
    elif cmd == "pm":
        pm_session()
    elif cmd == "last":
        show_last()
    elif cmd in ("free_entry", "free", "free_text"):
        free_entry()
    elif cmd == "wipe":
        wipe(also_wipe_icloud=("--icloud" in sys.argv))
    elif cmd == "append":
        # One-liner mode: dailyjournal append "text..."
        note_text_arg = " ".join(sys.argv[2:]).strip() if len(sys.argv) > 2 else None
        append_note(note_text_arg)
    else: 
        print("Unknown command. Run `dailyjournal help`.")
        sys.exit(2)

def free_entry():
    today = date.today().isoformat()
    print("Enter your free entry. End with a single line containing only: .done")
    lines = []
    while True:
        line = input()
        if line.strip() == ".done":
            break
        lines.append(line)

    text = "\n".join(lines).strip()

    payload = {
        "session_date": today,
        "session_type": "free",
        "raw_transcript": text,
        "summary": text[:200] + ("..." if len(text) > 200 else ""),
        "free_text": text,
    }

    insert_session(payload)

    exported = export_entry(payload)
    if exported:
        print(f"\n(cloud) wrote entry file: {exported.name}")

    print("\n--- FREE ENTRY SAVED ---")

def wipe(also_wipe_icloud: bool = False):
    phrase = "EraseTheJournal"

    print("==== DESTRUCTIVE OPERATION ====")
    if also_wipe_icloud:
        print("THIS WILL DELETE:")
        print("- Your LOCAL journal database")
        print("- ALL cloud entry files in DAILYJOURNAL_SYNC_DIR")
    else:
        print("THIS WILL DELETE YOUR LOCAL JOURNAL DATABASE ONLY.")
        print("(Tip: add --icloud to also wipe cloud entry files.)")

    print("\nTo confirm, type exactly:", phrase)
    typed = input("> ").strip()

    if typed != phrase:
        print("Cancelled.")
        return

    if delete_db_file():
        print("Local database deleted.")
    else:
        print("No database file found.")

    if also_wipe_icloud:
        deleted = wipe_sync_dir_entries()
        print(f"cloud sync dir wiped ({deleted} file(s) deleted).")

if __name__ == "__main__":
    main()

