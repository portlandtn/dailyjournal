# dj_secrets.py
from __future__ import annotations

import os
from typing import Optional

import keyring

SERVICE_NAME = "dailyjournal"
KEY_NAME = "openai_api_key"


def get_openai_api_key() -> Optional[str]:
    # Env var override always wins
    env = os.getenv("OPENAI_API_KEY")
    if env:
        return env.strip()

    try:
        val = keyring.get_password(SERVICE_NAME, KEY_NAME)
        return val.strip() if val else None
    except Exception:
        return None


def set_openai_api_key(value: str) -> None:
    keyring.set_password(SERVICE_NAME, KEY_NAME, value.strip())


def delete_openai_api_key() -> None:
    try:
        keyring.delete_password(SERVICE_NAME, KEY_NAME)
    except Exception:
        pass

