# TELEGRAM_ALERT_USAGE.md

## Telegram Alert System - Usage Guide

### Features
- Styled messages with emojis and consistent layout
- Multiple levels: `info`, `success`, `warning`, `error`, `critical`
- HTML formatting (`<b>`, `<code>`, `<i>`)
- Automatic UTC timestamp in each alert
- Key-value detail fields for context
- Silent mode behavior by severity (`info/success` quiet by default)

## Environment Setup

Add to `.env`:

```env
TELEGRAM_ALERTS_ENABLED=true
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_CHAT_IDS=6461561884,-1001234567890
```

## Basic Usage

```python
from utils.alert_templates import build_alert
from utils.telegram import send_telegram_alert

message = build_alert(
    title="Invoice Status Updated",
    level="warning",
    fields=[
        ("Invoice ID", 12),
        ("Business ID", 2),
        ("From", "pending"),
        ("To", "failed"),
    ],
)

send_telegram_alert(message, level="warning")
```

## Severity Behavior

- `info`, `success`: sent in silent mode by default
- `warning`, `error`, `critical`: sent with notification sound by default

You can override:

```python
send_telegram_alert(message, level="info", silent=False)
```

## Notes

- Alerts are non-blocking: API continues even if Telegram fails.
- Failure reasons are logged in backend logs.
