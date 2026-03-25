from __future__ import annotations


class MaxApiError(Exception):
    def __init__(self, *, method: str, path: str, status: int, body_text: str) -> None:
        super().__init__(f"{method} {path} failed with status {status}")
        self.method = method
        self.path = path
        self.status = status
        self.body_text = body_text
