# coach.py
import json
from typing import Dict, Any, List
from openai import OpenAI

from prompts import SYSTEM_RULES

client = OpenAI()


def _ask_llm(model: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends a structured request to the OpenAI Responses API and
    expects a JSON object back.
    """
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_RULES,
            },
            {
                "role": "user",
                "content": json.dumps(payload),
            },
        ],
        text={
            "format": {
                "type": "json_object"
            }
        },
    )

    # Responses API returns text in a few possible places depending on SDK version.
    # output_text is the safest single accessor.
    return json.loads(response.output_text)


def run_am(model: str, answers: List[str]) -> Dict[str, Any]:
    """
    Morning session:
    Takes raw user answers, returns structured commitments + summary.
    """
    transcript = []
    for i, a in enumerate(answers, start=1):
        transcript.append(f"AM Q{i}: {a}")

    payload = {
        "mode": "am",
        "answers": answers,
        "instructions": (
            "Convert the answers into concrete commitments. "
            "Be strict about specificity. "
            "Return ONLY the required fields as JSON."
        ),
        "summary_rules": "Summary MUST be multi-line, one item per line, using newline characters.",
        "required_fields": [
            "work_one_thing",
            "family_one_thing",
            "if_then_plan",
            "summary",
        ],
        "summary_format": [
            "Work One Thing:",
            "Family One Thing:",
            "Stress Trigger:",
            "If-Then Plan:",
        ],
    }

    data = _ask_llm(model, payload)
    data["raw_transcript"] = "\n".join(transcript)
    return data


def run_pm(model: str, am_commitments: Dict[str, Any], answers: List[str]) -> Dict[str, Any]:
    """
    Evening session:
    Evaluates AM commitments and produces outcomes + tomorrow setup.
    """
    transcript = [
        "AM Commitments:",
        f"- Work One Thing: {am_commitments.get('work_one_thing')}",
        f"- Family One Thing: {am_commitments.get('family_one_thing')}",
        f"- If-Then Plan: {am_commitments.get('if_then_plan')}",
        "",
    ]

    am_notes = am_commitments.get("free_text")
    if am_notes:
        transcript.append("AM Additional Notes:")
        transcript.append(am_notes)
        transcript.append("")

    notes = am_commitments.get("append_notes") or []
    if notes:
        transcript.append("Append Notes from today:")
        for n in notes:
            transcript.append(f"- {n}")
        transcript.append("")

    for i, a in enumerate(answers, start=1):
        transcript.append(f"PM Q{i}: {a}")

    payload = {
        "mode": "pm",
        "am_commitments": am_commitments,
        "answers": answers,
        "instructions": (
            "Evaluate whether commitments were met. "
            "Do not soften failures. "
            "Return ONLY the required fields as JSON."
        ),
        "summary_rules": "Summary MUST be multi-line, one item per line, using newline characters.",
        "required_fields": [
            "work_done",
            "family_done",
            "distraction_cause",
            "improvement",
            "summary",
            "tomorrow_focus",
        ],
        "summary_format": [
            "Work Result:",
            "Family Result:",
            "Distraction Cause:",
            "Improvement:",
            "Tomorrow Focus:",
        ],
    }

    data = _ask_llm(model, payload)
    data["raw_transcript"] = "\n".join(transcript)
    return data

