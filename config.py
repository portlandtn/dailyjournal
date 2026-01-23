# config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


APP_NAME = "dailyjournal"


def _default_config_path() -> Path:
    # Cross-platform-ish default:
    # macOS/Linux: ~/.config/dailyjournal/config.toml
    # Windows:     %APPDATA%\dailyjournal\config.toml (fallback to ~/.config)
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME / "config.toml"
    return Path.home() / ".config" / APP_NAME / "config.toml"


def _default_db_path() -> Path:
    # Keep your existing default but make it OS-friendly
    # macOS: ~/Library/Application Support/dailyjournal/coachscribe.db
    if sys_platform() == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME / "coachscribe.db"
    # Linux/other: ~/.local/share/dailyjournal/coachscribe.db
    return Path.home() / ".local" / "share" / APP_NAME / "coachscribe.db"


def sys_platform() -> str:
    import sys
    return sys.platform


@dataclass
class AppConfig:
    db_path: str
    export_dir: str
    model: str = "gpt-4.1-mini"

    @staticmethod
    def defaults() -> "AppConfig":
        # export_dir default: env var or empty (user should set via setup)
        # We'll pick a safe default folder in home if nothing is set
        default_export = str(Path.home() / "dailyjournal_exports")
        return AppConfig(
            db_path=str(_default_db_path()),
            export_dir=default_export,
            model=os.getenv("COACHSCRIBE_MODEL", "gpt-4.1-mini"),
        )


def load_config(path: Optional[Path] = None) -> AppConfig:
    cfg_path = path or _default_config_path()
    if not cfg_path.exists():
        return AppConfig.defaults()

    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))

    defaults = AppConfig.defaults()
    return AppConfig(
        db_path=str(data.get("db_path", defaults.db_path)),
        export_dir=str(data.get("export_dir", defaults.export_dir)),
        model=str(data.get("model", defaults.model)),
    )


def save_config(cfg: AppConfig, path: Optional[Path] = None) -> Path:
    cfg_path = path or _default_config_path()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    # TOML writing without extra deps (simple manual format)
    content = (
        f'db_path = "{cfg.db_path}"\n'
        f'export_dir = "{cfg.export_dir}"\n'
        f'model = "{cfg.model}"\n'
    )
    cfg_path.write_text(content, encoding="utf-8")
    return cfg_path


def config_path() -> Path:
    return _default_config_path()

