from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.codegen.bootstrap_ir import load_openapi, write_ir
from tools.codegen.lib.ir_builder import build_ir
from tools.codegen.lib.manifest import build_generator_manifest
from tools.codegen.lib.normalize import normalize_openapi
from tools.codegen.lib.renderers.python_client import render_python_client
from tools.codegen.lib.renderers.typescript_client import render_typescript_client
from tools.codegen.lib.validate import load_ir_schema, validate_ir_shape


OPENAPI_PATH = ROOT / "api" / "openapi" / "max-bot-api.yaml"
IR_SCHEMA_PATH = ROOT / "tools" / "codegen" / "ir-schema.json"
IR_OUTPUT_PATH = ROOT / "tools" / "codegen" / "out" / "max-bot-api.ir.json"
TS_OUTPUT_PATH = ROOT / "sdks" / "typescript" / "client" / "generated" / "index.ts"
PY_OUTPUT_PATH = ROOT / "sdks" / "python" / "client" / "src" / "max_client" / "generated" / "client.py"
MANIFEST_OUTPUT_PATH = ROOT / "tools" / "codegen" / "out" / "generator-manifest.json"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def run_generation(root: Path = ROOT) -> dict[str, str]:
    spec = load_openapi(OPENAPI_PATH)
    normalized = normalize_openapi(spec)
    ir = build_ir(normalized)

    ir_schema = load_ir_schema(IR_SCHEMA_PATH)
    validate_ir_shape(ir, ir_schema)
    write_ir(ir, IR_OUTPUT_PATH)

    typescript_client = render_typescript_client(ir)
    write_text(TS_OUTPUT_PATH, typescript_client)

    python_client = render_python_client(ir)
    write_text(PY_OUTPUT_PATH, python_client)

    manifest = build_generator_manifest(root, ir)
    write_json(MANIFEST_OUTPUT_PATH, manifest)

    return {
        "ir": IR_OUTPUT_PATH.relative_to(root).as_posix(),
        "typescript": TS_OUTPUT_PATH.relative_to(root).as_posix(),
        "python": PY_OUTPUT_PATH.relative_to(root).as_posix(),
        "manifest": MANIFEST_OUTPUT_PATH.relative_to(root).as_posix(),
    }


def run_verification(root: Path = ROOT) -> None:
    python_exe = sys.executable
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    commands = [
        (
            [python_exe, "-m", "unittest", "tests.codegen.test_bootstrap_ir", "tests.codegen.test_typescript_renderer", "tests.codegen.test_python_renderer", "tests.codegen.test_multilang_contract", "tests.codegen.test_generator_manifest", "tests.codegen.test_pipeline"],
            root,
        ),
        ([python_exe, "-m", "compileall", str(root / "sdks" / "python" / "client" / "src")], root),
        ([npm_cmd, "run", "check"], root / "sdks" / "typescript" / "client"),
        ([npm_cmd, "run", "build"], root / "sdks" / "typescript" / "client"),
    ]

    for command, cwd in commands:
        subprocess.run(command, cwd=str(cwd), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run MAX common SDK codegen pipeline.")
    parser.add_argument("--verify", action="store_true", help="Run verification after generation.")
    args = parser.parse_args()

    outputs = run_generation(ROOT)
    print(json.dumps(outputs, ensure_ascii=False, indent=2))

    if args.verify:
        run_verification(ROOT)
        print("Verification completed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
