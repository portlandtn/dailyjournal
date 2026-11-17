# engine.py
"""Decides whether a session uses the OpenAI coach or plain mode.

There are two downloads. The OpenAI edition includes coach.py and the openai
package. The no-AI edition is built without them, so the import below fails
and every session runs through plain.py. The OpenAI edition also falls back to
plain mode when no API key is set or the request fails, so answers are never
lost.
"""
import os

try:
    import coach  # needs the openai package; left out of the no-AI build
except ImportError:
    coach = None

AI_BUILD = coach is not None


def edition() -> str:
    return "OpenAI edition" if AI_BUILD else "no-AI edition"


def get_api_key():
    if not AI_BUILD:
        return None
    from dj_secrets import get_openai_api_key

    return get_openai_api_key()


def ai_ready() -> bool:
    """True when this build has the coach, AI is not switched off, and a key exists."""
    if not AI_BUILD or os.getenv("DAILYJOURNAL_NO_AI"):
        return False
    return bool(get_api_key())
