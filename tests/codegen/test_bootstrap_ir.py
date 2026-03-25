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
        normalized = module.normalize_openapi(spec)
        ir = module.build_ir(normalized)

        self.assertEqual(ir["api"]["title"], "MAX Bot API")
        self.assertEqual(ir["stats"]["service_count"], 1)
        self.assertEqual(ir["stats"]["operation_count"], 1)
        self.assertEqual(ir["stats"]["schema_count"], 1)
        self.assertEqual(ir["operations"][0]["operation_id"], "getHealth")
        self.assertEqual(ir["operations"][0]["service"], "health")
        self.assertEqual(ir["schemas"][0]["name"], "HealthResponse")
        self.assertEqual(ir["services"][0]["name"], "health")

    def test_normalize_openapi_sorts_and_derives_defaults(self) -> None:
        module = load_module()
        raw_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users/{userId}": {
                    "get": {
                        "summary": "Get user",
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["id"],
                        "properties": {
                            "name": {"type": "string"},
                            "id": {"type": "string", "nullable": False},
                        },
                    }
                }
            },
        }

        normalized = module.normalize_openapi(raw_spec)

        self.assertEqual(normalized["operations"][0]["operation_id"], "get_users_by_userId")
        self.assertEqual(normalized["operations"][0]["service"], "users")
        self.assertEqual(normalized["schemas"][0]["properties"][0]["name"], "id")
        self.assertTrue(normalized["schemas"][0]["properties"][0]["required"])
        self.assertEqual(normalized["schemas"][0]["properties"][1]["name"], "name")


if __name__ == "__main__":
    unittest.main()
