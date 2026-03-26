from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RENDER_MODULE_PATH = ROOT / "tools" / "codegen" / "render_csharp_client.py"
IR_PATH = ROOT / "tools" / "codegen" / "out" / "max-bot-api.ir.json"


def load_module():
    spec = importlib.util.spec_from_file_location("render_csharp_client", RENDER_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load render_csharp_client module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CSharpRendererTests(unittest.TestCase):
    def test_render_csharp_client_contains_expected_symbols(self) -> None:
        module = load_module()
        with IR_PATH.open("r", encoding="utf-8") as fh:
            ir = json.load(fh)

        output = module.render_csharp_client(ir)

        self.assertIn("namespace Max.Client.Generated;", output)
        self.assertIn("public sealed class MaxBotApiClient : BaseApiClient", output)
        self.assertIn("public enum UploadType", output)
        self.assertIn("GetHealthAsync", output)
        self.assertIn("request.Query.ChatId", output)
        self.assertIn("request.Path.MessageId", output)
        self.assertIn('Path = $"/chats/{Uri.EscapeDataString(request.Path.ChatLink.ToString())}"', output)
        self.assertIn('[JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]', output)
        self.assertIn('[JsonDerivedType(typeof(ImageAttachment), typeDiscriminator: "image")]', output)
        self.assertIn("public abstract class Attachment", output)
        self.assertIn("public sealed class ImageAttachment : Attachment", output)
        self.assertIn("public abstract class AttachmentRequest", output)
        self.assertIn("public sealed class ImageAttachmentRequest : AttachmentRequest", output)
        self.assertIn('[JsonPolymorphic(TypeDiscriminatorPropertyName = "update_type")]', output)
        self.assertIn("public abstract class Update", output)
        self.assertIn("public sealed class MessageCreatedUpdate : Update", output)
        self.assertIn("public sealed class InlineKeyboard : List<InlineKeyboardRow>", output)
        self.assertIn("public sealed class InlineKeyboardRow : List<InlineKeyboardButton>", output)
        self.assertIn('[JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]', output)
        self.assertIn('[JsonDerivedType(typeof(CallbackButton), typeDiscriminator: "callback")]', output)
        self.assertIn("public abstract class InlineKeyboardButton", output)
        self.assertIn("public sealed class CallbackButton : InlineKeyboardButton", output)
        self.assertIn("public enum MarkupElementType", output)
        self.assertIn("public UserWithPhoto? DialogWithUser { get; init; }", output)
        self.assertIn("public Message? PinnedMessage { get; init; }", output)
        self.assertIn("public ShareAttachmentPayload Payload { get; init; }", output)


if __name__ == "__main__":
    unittest.main()
