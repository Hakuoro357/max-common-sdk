from __future__ import annotations

import json
from typing import Any, TypedDict
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from .api_error import MaxApiError, parse_error_payload


class ClientConfig(TypedDict, total=False):
    base_url: str
    access_token: str
    authorization_scheme: str
    default_headers: dict[str, str]


class RequestOptions(TypedDict, total=False):
    headers: dict[str, str]


class BaseApiClient:
    def __init__(self, config: ClientConfig | None = None) -> None:
        config = config or {}
        self.base_url = config.get("base_url", "https://api.max.ru")
        self.access_token = config.get("access_token")
        self.authorization_scheme = config.get("authorization_scheme", "Bearer")
        self.default_headers = config.get("default_headers", {})

    def request(
        self,
        *,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: Any | None = None,
        options: RequestOptions | None = None,
    ) -> Any:
        url = urljoin(self.base_url, path)
        query_string = build_query_string(query)
        if query_string:
            url = f"{url}?{query_string}"

        headers = dict(self.default_headers)
        if self.access_token:
            headers["Authorization"] = f"{self.authorization_scheme} {self.access_token}"

        if options and options.get("headers"):
            headers.update(options["headers"])

        data: bytes | None = None
        if body is not None:
            headers.setdefault("Content-Type", "application/json")
            data = json.dumps(body).encode("utf-8")

        request = Request(url=url, method=method, data=data, headers=headers)

        try:
            with urlopen(request) as response:
                payload = response.read().decode("utf-8")
                if not payload:
                    return None
                return json.loads(payload)
        except Exception as exc:
            status = getattr(exc, "code", 0)
            body_text = ""
            if hasattr(exc, "read"):
                body_text = exc.read().decode("utf-8")
            payload = parse_error_payload(body_text)
            raise MaxApiError(method=method, path=path, status=status, body_text=body_text, payload=payload) from exc


def build_query_string(query: dict[str, Any] | None) -> str:
    if not query:
        return ""

    items: list[tuple[str, str]] = []
    for key, value in query.items():
        if value is None:
            continue

        if isinstance(value, list):
            for item in value:
                items.append((key, serialize_query_value(item)))
            continue

        items.append((key, serialize_query_value(value)))

    return urlencode(items)


def serialize_query_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
