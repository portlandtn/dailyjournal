# app.py
import os
import sys
from datetime import date
from entries import export_entry, wipe_sync_dir_entries, read_entry_file, iter_entry_files
from store import get_latest_pm_with_tomorrow_focus
from store import delete_db_file

from store import (
    init_db,
    insert_session,
    get_latest_am,
    get_last_n_summaries,
    is_file_imported,
    mark_file_imported,
    insert_session_from_icloud,
)
from prompts import AM_QUESTIONS, PM_QUESTIONS
from coach import run_am, run_pm

DEFAULT_MODEL = os.getenv("COACHSCRIBE_MODEL", "gpt-4.1-mini")


def ask_questions(questions):
    answers = []
    for q in questions:
        print()
        print(q)
        ans = input("> ").strip()
        answers.append(ans)
    return answers


def am_session():
    last_pm = get_latest_pm_with_tomorrow_focus()
    if last_pm and last_pm.get("tomorrow_focus"):
        print("\nLast night you said tomorrow’s focus was:")
        print(f"→ {last_pm['tomorrow_focus']}") 

    today = date.today().isoformat() 
    answers = ask_questions(AM_QUESTIONS)

    data = run_am(DEFAULT_MODEL, answers)

    payload = {
        "session_date": today,
        "session_type": "am",
        "raw_transcript": data["raw_transcript"],
        "summary": data["summary"],
        "work_one_thing": data.get("work_one_thing"),
        "family_one_thing": data.get("family_one_thing"),
        "focus_guardrail": data.get("focus_guardrail"),
        "if_then_plan": data.get("if_then_plan"),
    }

    insert_session(payload)
    exported = export_entry(payload)
    if exported:
        print(f"\n(iCloud) wrote entry file: {exported.name}")

    print("\n--- AM SUMMARY ---")
    print(data["summary"])


def pm_session():
    today = date.today().isoformat()
    am = get_latest_am(today)

    if not am:
        am = get_latest_am(today)

    if am:
        print("\nAM COMMITMENTS")
        print(f"- Work One Thing: {am['work_one_thing']}")
        print(f"- Family One Thing: {am['family_one_thing']}")
        print(f"- Focus Guardrail: {am['focus_guardrail']}")
        print(f"- If-Then Plan: {am['if_then_plan']}")

        pm_questions = [
            f"You said your Work One Thing was:\n  \"{am['work_one_thing']}\"\nDid you complete it? What’s the proof?",
            f"You said your Family One Thing was:\n  \"{am['family_one_thing']}\"\nDid you do it? What did you do, specifically?",
            f"You said your Focus Guardrail was:\n  \"{am['focus_guardrail']}\"\nDid you follow it? If not, what broke it?",
            "What was the biggest trigger for distraction today (one sentence)?",
            "What’s one adjustment you’ll make tomorrow (one sentence)?",
        ]
    else:
        print("\nNo AM entry found for today — doing a general evening review.\n")

        pm_questions = [
            "What was the ONE thing you most wanted to accomplish today?",
            "Did you accomplish it? What’s the proof or current status?",
            "What was your biggest distraction today (phone, stress, meetings, fatigue)?",
            "What’s one adjustment you’ll make tomorrow (one sentence)?",
            "What should tomorrow’s focus be (one sentence)?",
        ]

    answers = ask_questions(pm_questions)

    data = run_pm(DEFAULT_MODEL, am or {}, answers)

    payload = {
        "session_date": today,
        "session_type": "pm",
        "raw_transcript": data["raw_transcript"],
        "summary": data["summary"],
        "work_done": int(data.get("work_done", 0)),
        "family_done": int(data.get("family_done", 0)),
        "focus_done": int(data.get("focus_done", 0)),
        "distraction_cause": data.get("distraction_cause"),
        "improvement": data.get("improvement"),
        "tomorrow_focus": data.get("tomorrow_focus"),
    }

    insert_session(payload)
    exported = export_entry(payload)
    if exported:
        print(f"\n(iCloud) wrote entry file {exported.name}")

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
            insert_session_from_icloud(entry)
            mark_file_imported(name)
            imported += 1
        except Exception as e:
            # Don't crash the whole app because one file is bad
            print(f"(sync) WARNING: failed to import {name}: {e}")

    if imported:
        print(f"(sync) Imported {imported} new iCloud entr{'y' if imported == 1 else 'ies'}.")


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set in the environment.")
        sys.exit(1)

    init_db()
    sync_from_icloud_on_startup()

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
  dailyjournal wipe [--iCloud]  Erases the local journal, (also wipes the icloud sync if icloud argument is passed)

Examples:
  dailyjournal am
  dailyjournal pm
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
        print(f"\n(iCloud) wrote entry file: {exported.name}")

    print("\n--- FREE ENTRY SAVED ---")

def wipe(also_wipe_icloud: bool = False):
    phrase = "EraseTheJournal"

    print("==== DESTRUCTIVE OPERATION ====")
    if also_wipe_icloud:
        print("THIS WILL DELETE:")
        print("- Your LOCAL journal database")
        print("- ALL iCloud entry files in DAILYJOURNAL_SYNC_DIR")
    else:
        print("THIS WILL DELETE YOUR LOCAL JOURNAL DATABASE ONLY.")
        print("(Tip: add --icloud to also wipe iCloud entry files.)")

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
        print(f"iCloud sync dir wiped ({deleted} file(s) deleted).")

if __name__ == "__main__":
    main()

