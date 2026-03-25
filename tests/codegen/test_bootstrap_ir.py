from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "codegen" / "bootstrap_ir.py"
SPEC_PATH = ROOT / "api" / "openapi" / "max-bot-api.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("bootstrap_ir", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load bootstrap_ir module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BootstrapIrTests(unittest.TestCase):
    def test_build_ir_from_bootstrap_openapi(self) -> None:
        module = load_module()
        spec = module.load_openapi(SPEC_PATH)
        ir = module.build_ir(spec)

        self.assertEqual(ir["api"]["title"], "MAX Bot API")
        self.assertEqual(ir["stats"]["operation_count"], 1)
        self.assertEqual(ir["stats"]["schema_count"], 1)
        self.assertEqual(ir["operations"][0]["operation_id"], "getHealth")
        self.assertEqual(ir["schemas"][0]["name"], "HealthResponse")


if __name__ == "__main__":
    unittest.main()
