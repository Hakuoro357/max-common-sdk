from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RENDER_MODULE_PATH = ROOT / "tools" / "codegen" / "render_python_client.py"
IR_PATH = ROOT / "tools" / "codegen" / "out" / "max-bot-api.ir.json"


def load_module():
    spec = importlib.util.spec_from_file_location("render_python_client", RENDER_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load render_python_client module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PythonRendererTests(unittest.TestCase):
    def test_render_python_client_contains_expected_symbols(self) -> None:
        module = load_module()
        with IR_PATH.open("r", encoding="utf-8") as fh:
            ir = json.load(fh)

        output = module.render_python_client(ir)

        self.assertIn("from ..runtime import BaseApiClient, ClientConfig, RequestOptions", output)
        self.assertIn("class HealthResponse(TypedDict", output)
        self.assertIn("UploadType: TypeAlias = Literal[", output)
        self.assertIn("class MaxBotApiClient(BaseApiClient):", output)
        self.assertIn("def getHealth", output)
        self.assertIn("query={ 'chat_id': request['query'].get('chat_id')", output)
        self.assertIn("quote(str(request[\"path\"][\"message_id\"])", output)
        self.assertIn("path=f'/chats/{quote(str(request[\"path\"][\"chat_link\"]), safe=\"\")}'", output)
        self.assertIn("sender: NotRequired[User | None]", output)
        self.assertIn("photos: NotRequired[PhotoTokenMap | None]", output)
        self.assertIn("PhotoTokenMap: TypeAlias = dict[str, str]", output)
        self.assertIn("AttachmentRequest: TypeAlias =", output)
        self.assertIn("ImageAttachmentRequest | VideoAttachmentRequest", output)
        self.assertIn("Update: TypeAlias =", output)
        self.assertIn("MessageCallbackUpdate | MessageCreatedUpdate", output)
        self.assertIn("InlineKeyboard: TypeAlias = list[InlineKeyboardRow]", output)
        self.assertIn("InlineKeyboardRow: TypeAlias = list[InlineKeyboardButton]", output)
        self.assertIn("InlineKeyboardButton: TypeAlias =", output)
        self.assertIn("CallbackButton | LinkButton | RequestContactButton", output)
        self.assertIn("MarkupElementType: TypeAlias = Literal[", output)
        self.assertIn("'mention'", output)
        self.assertIn("dialog_with_user: NotRequired[UserWithPhoto | None]", output)
        self.assertIn("pinned_message: NotRequired[Message | None]", output)
        self.assertIn("payload: ShareAttachmentPayload", output)

    def test_render_python_client_supports_union_and_map_types(self) -> None:
        module = load_module()
        ir = {
            "schemas": [
                {
                    "name": "AttachmentVariant",
                    "kind": "union",
                    "variants": [
                        {"kind": "ref", "ref": "#/components/schemas/ImageAttachment", "nullable": False},
                        {"kind": "ref", "ref": "#/components/schemas/FileAttachment", "nullable": False},
                    ],
                },
                {
                    "name": "StringMap",
                    "kind": "map",
                    "additional_properties": {"kind": "scalar", "type": "string", "nullable": False},
                },
            ],
            "operations": [],
        }

        output = module.render_python_client(ir)

        self.assertIn("AttachmentVariant: TypeAlias = ImageAttachment | FileAttachment", output)
        self.assertIn("StringMap: TypeAlias = dict[str, str]", output)


if __name__ == "__main__":
    unittest.main()
