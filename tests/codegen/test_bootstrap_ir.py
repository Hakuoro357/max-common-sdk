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
        operation_ids = [operation["operation_id"] for operation in ir["operations"]]
        service_names = [service["name"] for service in ir["services"]]
        schema_names = [schema["name"] for schema in ir["schemas"]]

        self.assertEqual(ir["api"]["title"], "MAX Bot API")
        self.assertEqual(ir["stats"]["service_count"], 6)
        self.assertEqual(ir["stats"]["operation_count"], 25)
        self.assertGreaterEqual(ir["stats"]["schema_count"], 44)
        self.assertEqual(service_names[0], "bots")
        self.assertIn("health", service_names)
        self.assertIn("messages", service_names)
        self.assertIn("getHealth", operation_ids)
        self.assertIn("getUpdates", operation_ids)
        self.assertIn("getAllChats", operation_ids)
        self.assertIn("getChatByLink", operation_ids)
        self.assertIn("answerOnCallback", operation_ids)
        self.assertIn("getChatMembers", operation_ids)
        self.assertIn("pinMessage", operation_ids)
        self.assertIn("deleteMessage", operation_ids)
        self.assertIn("UploadType", schema_names)
        self.assertIn("Chat", schema_names)
        self.assertIn("ChatMember", schema_names)
        self.assertIn("AttachmentRequest", schema_names)
        self.assertIn("Attachment", schema_names)

        get_health = next(operation for operation in ir["operations"] if operation["operation_id"] == "getHealth")
        self.assertEqual(get_health["service"], "health")
        self.assertEqual(get_health["parameters"], [])
        self.assertIsNone(get_health["request_body"])

        get_chat_by_link = next(operation for operation in ir["operations"] if operation["operation_id"] == "getChatByLink")
        self.assertEqual(get_chat_by_link["path"], "/chats/by-link/{chat_link}")
        self.assertEqual(get_chat_by_link["wire_path"], "/chats/{chat_link}")

        attachment_request = next(schema for schema in ir["schemas"] if schema["name"] == "AttachmentRequest")
        attachment = next(schema for schema in ir["schemas"] if schema["name"] == "Attachment")
        self.assertEqual(attachment_request["kind"], "union")
        self.assertEqual(len(attachment_request["variants"]), 9)
        self.assertEqual(attachment_request["discriminator"]["property_name"], "type")
        self.assertEqual(attachment["kind"], "union")
        self.assertEqual(len(attachment["variants"]), 9)
        update = next(schema for schema in ir["schemas"] if schema["name"] == "Update")
        self.assertEqual(update["kind"], "union")
        self.assertEqual(len(update["variants"]), 13)
        self.assertEqual(update["discriminator"]["property_name"], "update_type")

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
        self.assertEqual(normalized["operations"][0]["parameters"], [])
        self.assertIsNone(normalized["operations"][0]["request_body"])
        self.assertEqual(normalized["schemas"][0]["properties"][0]["name"], "id")
        self.assertTrue(normalized["schemas"][0]["properties"][0]["required"])
        self.assertEqual(normalized["schemas"][0]["properties"][1]["name"], "name")

    def test_normalize_openapi_keeps_parameters_and_request_body(self) -> None:
        module = load_module()
        raw_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/messages/{message_id}": {
                    "post": {
                        "parameters": [
                            {
                                "name": "message_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "notify",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean"},
                            },
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EditMessageRequest"}
                                }
                            },
                        },
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        }

        normalized = module.normalize_openapi(raw_spec)
        operation = normalized["operations"][0]

        self.assertEqual(operation["parameters"][0]["in"], "path")
        self.assertEqual(operation["parameters"][0]["name"], "message_id")
        self.assertEqual(operation["parameters"][1]["in"], "query")
        self.assertEqual(operation["parameters"][1]["name"], "notify")
        self.assertTrue(operation["request_body"]["required"])
        self.assertEqual(
            operation["request_body"]["media_types"][0]["schema_ref"],
            "#/components/schemas/EditMessageRequest",
        )

    def test_normalize_openapi_keeps_wire_path_override(self) -> None:
        module = load_module()
        raw_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/chats/by-link/{chat_link}": {
                    "get": {
                        "operationId": "getChatByLink",
                        "x-max-wire-path": "/chats/{chat_link}",
                        "parameters": [
                            {
                                "name": "chat_link",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        }

        normalized = module.normalize_openapi(raw_spec)
        operation = normalized["operations"][0]

        self.assertEqual(operation["path"], "/chats/by-link/{chat_link}")
        self.assertEqual(operation["wire_path"], "/chats/{chat_link}")

    def test_normalize_openapi_keeps_union_map_and_discriminator(self) -> None:
        module = load_module()
        raw_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "StringMap": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "Attachment": {
                        "oneOf": [
                            {"$ref": "#/components/schemas/ImageAttachment"},
                            {"$ref": "#/components/schemas/FileAttachment"},
                        ],
                        "discriminator": {
                            "propertyName": "type",
                            "mapping": {
                                "image": "#/components/schemas/ImageAttachment",
                                "file": "#/components/schemas/FileAttachment",
                            },
                        },
                    },
                }
            },
        }

        normalized = module.normalize_openapi(raw_spec)
        string_map = next(schema for schema in normalized["schemas"] if schema["name"] == "StringMap")
        attachment = next(schema for schema in normalized["schemas"] if schema["name"] == "Attachment")

        self.assertEqual(string_map["kind"], "map")
        self.assertEqual(string_map["additional_properties"]["kind"], "scalar")
        self.assertEqual(string_map["additional_properties"]["type"], "string")
        self.assertEqual(attachment["kind"], "union")
        self.assertEqual(len(attachment["variants"]), 2)
        self.assertEqual(attachment["variants"][0]["kind"], "ref")
        self.assertEqual(attachment["discriminator"]["property_name"], "type")
        self.assertIn("image", attachment["discriminator"]["mapping"])


if __name__ == "__main__":
    unittest.main()
