from __future__ import annotations

import json
from typing import NotRequired, TypedDict


class MaxErrorPayload(TypedDict, total=False):
    code: str
    message: str
    details: NotRequired[str | None]


class MaxApiError(Exception):
    def __init__(
        self,
        *,
        method: str,
        path: str,
        status: int,
        body_text: str,
        payload: MaxErrorPayload | None = None,
    ) -> None:
        message = payload.get("message") if payload else None
        super().__init__(message or f"{method} {path} failed with status {status}")
        self.method = method
        self.path = path
        self.status = status
        self.body_text = body_text
        self.payload = payload
        self.error_code = payload.get("code") if payload else None
        self.error_message = payload.get("message") if payload else None
        self.error_details = payload.get("details") if payload else None


def parse_error_payload(body_text: str) -> MaxErrorPayload | None:
    if not body_text.strip():
        return None

    try:
        parsed = json.loads(body_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None

    payload: MaxErrorPayload = {}
    if isinstance(parsed.get("code"), str):
        payload["code"] = parsed["code"]
    if isinstance(parsed.get("message"), str):
        payload["message"] = parsed["message"]
    if isinstance(parsed.get("details"), str) or parsed.get("details") is None:
        if "details" in parsed:
            payload["details"] = parsed["details"]

    return payload or None
