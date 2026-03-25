from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IR_PATH = ROOT / "tools" / "codegen" / "out" / "max-bot-api.ir.json"
TS_CLIENT_PATH = ROOT / "sdks" / "typescript" / "client" / "generated" / "index.ts"
PY_CLIENT_PATH = ROOT / "sdks" / "python" / "client" / "src" / "max_client" / "generated" / "client.py"


class MultiLanguageContractTests(unittest.TestCase):
    def test_generated_clients_cover_all_ir_operations(self) -> None:
        with IR_PATH.open("r", encoding="utf-8") as fh:
            ir = json.load(fh)

        expected_operations = {operation["operation_id"] for operation in ir["operations"]}

        ts_content = TS_CLIENT_PATH.read_text(encoding="utf-8")
        py_content = PY_CLIENT_PATH.read_text(encoding="utf-8")

        ts_operations = set(re.findall(r"async\s+([A-Za-z_][A-Za-z0-9_]*)\(", ts_content))
        py_operations = set(re.findall(r"^\s+def\s+([A-Za-z_][A-Za-z0-9_]*)\(", py_content, flags=re.MULTILINE))

        self.assertEqual(expected_operations, ts_operations)
        self.assertTrue(expected_operations.issubset(py_operations))


if __name__ == "__main__":
    unittest.main()
