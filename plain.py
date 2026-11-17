# plain.py
"""Sessions without AI.

Builds the same fields the OpenAI coach returns, straight from what you typed.
Nothing here touches the network.
"""
from typing import Any, Dict, List, Optional


def _line(label: str, value: Optional[str]) -> str:
    return f"{label} {value.strip() if value and value.strip() else '(blank)'}"


def _answer(answers: List[str], index: int) -> str:
    return answers[index].strip() if index < len(answers) else ""


def run_am(answers: List[str]) -> Dict[str, Any]:
    """Morning session: your answers become the commitments as written."""
    work, family, trigger, plan = (_answer(answers, i) for i in range(4))
    transcript = [f"AM Q{i}: {a}" for i, a in enumerate(answers, start=1)]
    return {
        "work_one_thing": work,
        "family_one_thing": family,
        "if_then_plan": plan,
        "summary": "\n".join(
            [
                _line("Work One Thing:", work),
                _line("Family One Thing:", family),
                _line("Stress Trigger:", trigger),
                _line("If-Then Plan:", plan),
            ]
        ),
        "raw_transcript": "\n".join(transcript),
    }


def run_pm(
    am_commitments: Dict[str, Any],
    answers: List[str],
    work_done: bool,
    family_done: bool,
    had_am: bool,
) -> Dict[str, Any]:
    """Evening session: you mark what got done; the summary records it plainly."""
    transcript = [
        "AM Commitments:",
        f"- Work One Thing: {am_commitments.get('work_one_thing')}",
        f"- Family One Thing: {am_commitments.get('family_one_thing')}",
        f"- If-Then Plan: {am_commitments.get('if_then_plan')}",
        "",
    ]

    am_notes = am_commitments.get("free_text")
    if am_notes:
        transcript += ["AM Additional Notes:", am_notes, ""]

    notes = am_commitments.get("append_notes") or []
    if notes:
        transcript.append("Append Notes from today:")
        transcript += [f"- {n}" for n in notes]
        transcript.append("")

    transcript += [f"PM Q{i}: {a}" for i, a in enumerate(answers, start=1)]

    if had_am:
        # Questions: work proof, family proof, distraction, adjustment, tomorrow focus
        work_note, family_note = _answer(answers, 0), _answer(answers, 1)
        distraction, improvement, tomorrow = (_answer(answers, i) for i in (2, 3, 4))
    else:
        # Questions: the one thing, status, adjustment, tomorrow focus
        work_note = " / ".join(a for a in (_answer(answers, 0), _answer(answers, 1)) if a)
        family_note, distraction = "", ""
        improvement, tomorrow = _answer(answers, 2), _answer(answers, 3)

    def result(done: bool, note: str) -> str:
        status = "Done" if done else "Not done"
        return f"{status}. {note}" if note else status

    summary = [_line("Work Result:", result(work_done, work_note))]
    if had_am:
        summary.append(_line("Family Result:", result(family_done, family_note)))
        summary.append(_line("Distraction Cause:", distraction))
    summary.append(_line("Improvement:", improvement))
    summary.append(_line("Tomorrow Focus:", tomorrow))

    return {
        "work_done": int(work_done),
        "family_done": int(family_done),
        "distraction_cause": distraction or None,
        "improvement": improvement or None,
        "tomorrow_focus": tomorrow or None,
        "summary": "\n".join(summary),
        "raw_transcript": "\n".join(transcript),
    }
