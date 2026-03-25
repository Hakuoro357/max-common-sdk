from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.codegen.lib.ir_builder import build_ir
from tools.codegen.lib.normalize import normalize_openapi
from tools.codegen.lib.validate import load_ir_schema, validate_ir_shape, validate_openapi_shape


def load_openapi(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    validate_openapi_shape(data)
    return data


def write_ir(ir: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(ir, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a minimal IR from an OpenAPI file.")
    parser.add_argument("--input", required=True, help="Path to OpenAPI YAML file.")
    parser.add_argument("--output", required=True, help="Path to output IR JSON file.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    schema_path = Path(__file__).with_name("ir-schema.json")

    spec = load_openapi(input_path)
    normalized_spec = normalize_openapi(spec)
    ir = build_ir(normalized_spec)
    ir_schema = load_ir_schema(schema_path)
    validate_ir_shape(ir, ir_schema)
    write_ir(ir, output_path)

    print(f"Wrote IR to {output_path}")
    print(
        json.dumps(
            {
                "services": ir["stats"]["service_count"],
                "operations": ir["stats"]["operation_count"],
                "schemas": ir["stats"]["schema_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
