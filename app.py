# app.py
import os
import sys
from datetime import date

from store import (
    init_db,
    insert_session,
    get_latest_am,
    get_last_n_summaries,
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

    print("\n--- AM SUMMARY ---")
    print(data["summary"])


def pm_session():
    today = date.today().isoformat()
    am = get_latest_am(today)

    if not am:
        print("No AM session found for today. Run `python app.py am` first.")
        sys.exit(1)

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

    answers = ask_questions(pm_questions)

    data = run_pm(DEFAULT_MODEL, am, answers)

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

    print("\n--- PM SUMMARY ---")
    print(data["summary"])


def show_last():
    rows = get_last_n_summaries(10)
    print("\nRECENT ENTRIES")
    for r in rows:
        first_line = r["summary"].splitlines()[0]
        print(f"{r['date']} [{r['type'].upper()}] {first_line}")

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set in the environment.")
        sys.exit(1)

    init_db()

    if len(sys.argv) < 2 or sys.argv[1] in ("help", "-h", "--help"):
        print("""
dailyjournal — AM/PM journaling with accountability

Usage:
  dailyjournal am      Run morning session
  dailyjournal pm      Run evening session
  dailyjournal last    Show recent summaries
  dailyjournal help    Show this help

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
    else:
        print("Unknown command. Run `dailyjournal help`.")
        sys.exit(2)

if __name__ == "__main__":
    main()

