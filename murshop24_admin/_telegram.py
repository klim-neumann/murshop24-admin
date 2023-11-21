from typing import Any

import httpx


def _call_method(token: str, method: str, params: Any | None = None) -> dict[str, Any]:
    res = httpx.get(f"https://api.telegram.org/bot{token}/{method}", params=params)
    return res.json()


def get_me(token: str) -> dict[str, Any]:
    return _call_method(token, "getMe")


def set_webhook(token: str, url: str, secret_token: str) -> dict[str, Any]:
    params = {"url": url, "secret_token": secret_token}
    return _call_method(token, "setWebhook", params=params)


def delete_webhook(token: str) -> dict[str, Any]:
    return _call_method(token, "deleteWebhook")
