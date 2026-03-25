from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON_CLIENT_SRC = ROOT / "sdks" / "python" / "client" / "src"

if str(PYTHON_CLIENT_SRC) not in sys.path:
    sys.path.insert(0, str(PYTHON_CLIENT_SRC))

from max_client.runtime.api_error import MaxApiError, parse_error_payload


class PythonApiErrorTests(unittest.TestCase):
    def test_parse_error_payload_returns_typed_fields(self) -> None:
        payload = parse_error_payload('{"code":"bot.not_found","message":"Bot not found","details":"check token"}')

        self.assertEqual(
            payload,
            {
                "code": "bot.not_found",
                "message": "Bot not found",
                "details": "check token",
            },
        )

    def test_parse_error_payload_returns_none_for_invalid_json(self) -> None:
        self.assertIsNone(parse_error_payload("not-json"))

    def test_max_api_error_uses_payload_fields(self) -> None:
        payload = {"code": "forbidden", "message": "Forbidden", "details": "missing rights"}
        error = MaxApiError(method="GET", path="/me", status=403, body_text='{"code":"forbidden"}', payload=payload)

        self.assertEqual(str(error), "Forbidden")
        self.assertEqual(error.error_code, "forbidden")
        self.assertEqual(error.error_message, "Forbidden")
        self.assertEqual(error.error_details, "missing rights")


if __name__ == "__main__":
    unittest.main()
