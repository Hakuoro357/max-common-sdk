from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RENDER_MODULE_PATH = ROOT / "tools" / "codegen" / "render_typescript_client.py"
IR_PATH = ROOT / "tools" / "codegen" / "out" / "max-bot-api.ir.json"


def load_module():
    spec = importlib.util.spec_from_file_location("render_typescript_client", RENDER_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load render_typescript_client module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TypeScriptRendererTests(unittest.TestCase):
    def test_render_typescript_client_contains_expected_symbols(self) -> None:
        module = load_module()
        with IR_PATH.open("r", encoding="utf-8") as fh:
            ir = json.load(fh)

        output = module.render_typescript_client(ir)

        self.assertIn("export interface HealthResponse", output)
        self.assertIn("export type UploadType =", output)
        self.assertIn("export class MaxBotApiClient", output)
        self.assertIn("async getHealth", output)
        self.assertIn("const url = new URL(`/health`, this.baseUrl);", output)
        self.assertIn("export interface SendMessageParams", output)
        self.assertIn("url.searchParams.set('chat_id'", output)
        self.assertIn("request.path.message_id", output)


if __name__ == "__main__":
    unittest.main()
