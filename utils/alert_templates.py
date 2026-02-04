# utils/alert_templates.py
from datetime import datetime, timezone
from html import escape
from typing import Iterable


def _level_icon(level: str) -> str:
    level_map = {
        "info": "\U0001F4D8",      # blue book
        "success": "\u2705",      # check mark
        "warning": "\u26A0\uFE0F",  # warning
        "error": "\U0001F6A8",     # police light
        "critical": "\U0001F525",  # fire
    }
    return level_map.get(level, "\U0001F4E3")


def build_alert(
    *,
    title: str,
    fields: Iterable[tuple[str, object]] = (),
    level: str = "info",
    footer: str | None = None,
    include_timestamp: bool = True,
) -> str:
    """Build a styled Telegram HTML message for internal alerts."""
    normalized_level = (level or "info").strip().lower()
    icon = _level_icon(normalized_level)

    lines = [f"{icon} <b>{escape(title)}</b>"]

    if include_timestamp:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        lines.append(f"<b>Time:</b> <code>{now}</code>")

    lines.append(f"<b>Level:</b> <code>{escape(normalized_level.upper())}</code>")

    for label, value in fields:
        rendered = "-" if value is None or value == "" else str(value)
        lines.append(f"<b>{escape(label)}:</b> <code>{escape(rendered)}</code>")

    if footer:
        lines.append(f"<i>{escape(footer)}</i>")

    return "\n".join(lines)
