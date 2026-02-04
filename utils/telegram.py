# utils/telegram.py
import json
import logging
import urllib.error
import urllib.request

from core.config import settings

logger = logging.getLogger(__name__)


def _chat_ids() -> list[str]:
    return [item.strip() for item in settings.TELEGRAM_CHAT_IDS.split(",") if item.strip()]


def _should_silent(level: str) -> bool:
    """Send quiet notifications for non-urgent events by default."""
    return (level or "info").strip().lower() in {"info", "success"}


def send_telegram_alert(
    message: str,
    *,
    level: str = "info",
    silent: bool | None = None,
) -> None:
    if not settings.TELEGRAM_ALERTS_ENABLED:
        return
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram alerts enabled but TELEGRAM_BOT_TOKEN is empty.")
        return

    chat_ids = _chat_ids()
    if not chat_ids:
        logger.warning("Telegram alerts enabled but TELEGRAM_CHAT_IDS is empty.")
        return

    disable_notification = _should_silent(level) if silent is None else silent

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "disable_notification": disable_notification,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8):
                pass
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            logger.warning(
                "Telegram alert failed (chat_id=%s, status=%s): %s",
                chat_id,
                exc.code,
                body or exc.reason,
            )
        except (urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Telegram alert failed (chat_id=%s): %s", chat_id, exc)
