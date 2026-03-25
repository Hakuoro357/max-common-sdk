from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IR_PATH = ROOT / "tools" / "codegen" / "out" / "max-bot-api.ir.json"
MANIFEST_PATH = ROOT / "tools" / "codegen" / "out" / "generator-manifest.json"


class GeneratorManifestTests(unittest.TestCase):
    def test_manifest_matches_ir_and_existing_files(self) -> None:
        with IR_PATH.open("r", encoding="utf-8") as fh:
            ir = json.load(fh)

        with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
            manifest = json.load(fh)

        expected_operations = sorted(operation["operation_id"] for operation in ir["operations"])

        self.assertEqual(manifest["ir_version"], ir["ir_version"])
        self.assertEqual(manifest["api_version"], ir["api"]["version"])
        self.assertEqual(len(manifest["languages"]), 3)

        for language in manifest["languages"]:
            self.assertEqual(language["supported_operations"], expected_operations)
            self.assertTrue(language["coverage_complete"])

            entrypoint = ROOT / language["entrypoint"]
            self.assertTrue(entrypoint.exists(), f"Missing entrypoint: {entrypoint}")

            for file_path in language["generated_files"]:
                self.assertTrue((ROOT / file_path).exists(), f"Missing generated file: {file_path}")

            for file_path in language["runtime_files"]:
                self.assertTrue((ROOT / file_path).exists(), f"Missing runtime file: {file_path}")


if __name__ == "__main__":
    unittest.main()
