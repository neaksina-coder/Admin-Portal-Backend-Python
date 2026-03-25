# utils/paypal.py
from typing import Any, Dict

import httpx

from core.config import settings


def _paypal_base_url() -> str:
    return "https://api-m.paypal.com" if settings.PAYPAL_ENV == "live" else "https://api-m.sandbox.paypal.com"


def get_access_token() -> str:
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise RuntimeError("PayPal credentials are not configured")

    url = f"{_paypal_base_url()}/v1/oauth2/token"
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}
    with httpx.Client(timeout=20) as client:
        res = client.post(url, data=data, auth=auth)
        res.raise_for_status()
        payload = res.json()
        return payload["access_token"]


def create_order(*, amount: float, currency: str, description: str, custom_id: str) -> Dict[str, Any]:
    url = f"{_paypal_base_url()}/v2/checkout/orders"
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "description": description,
                "custom_id": custom_id,
                "amount": {
                    "currency_code": currency,
                    "value": f"{amount:.2f}",
                },
            }
        ],
    }
    with httpx.Client(timeout=20) as client:
        res = client.post(url, json=body, headers=headers)
        res.raise_for_status()
        return res.json()


def capture_order(order_id: str) -> Dict[str, Any]:
    url = f"{_paypal_base_url()}/v2/checkout/orders/{order_id}/capture"
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    with httpx.Client(timeout=20) as client:
        res = client.post(url, headers=headers)
        res.raise_for_status()
        return res.json()
