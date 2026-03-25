from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "codegen" / "run_pipeline.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_pipeline", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load run_pipeline module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PipelineTests(unittest.TestCase):
    def test_run_generation_writes_expected_artifacts(self) -> None:
        module = load_module()
        outputs = module.run_generation(ROOT)

        self.assertEqual(
            outputs,
            {
                "ir": "tools/codegen/out/max-bot-api.ir.json",
                "typescript": "sdks/typescript/client/generated/index.ts",
                "python": "sdks/python/client/src/max_client/generated/client.py",
                "manifest": "tools/codegen/out/generator-manifest.json",
            },
        )

        for relative_path in outputs.values():
            self.assertTrue((ROOT / relative_path).exists(), f"Missing generated artifact: {relative_path}")


if __name__ == "__main__":
    unittest.main()
