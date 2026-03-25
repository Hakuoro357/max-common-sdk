from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


HTTP_METHODS = ("get", "post", "put", "patch", "delete", "options", "head")


def load_openapi(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if not isinstance(data, dict):
        raise ValueError("OpenAPI document must be a mapping at the root.")

    return data


def extract_operation(path_name: str, method: str, operation: dict[str, Any]) -> dict[str, Any]:
    responses = []
    for status_code, response in sorted((operation.get("responses") or {}).items()):
        content = response.get("content") or {}
        content_types = sorted(content.keys())
        schema_ref = None

        if "application/json" in content:
            schema = (content["application/json"] or {}).get("schema") or {}
            schema_ref = schema.get("$ref")

        responses.append(
            {
                "status_code": str(status_code),
                "description": response.get("description"),
                "content_types": content_types,
                "schema_ref": schema_ref,
            }
        )

    return {
        "operation_id": operation.get("operationId"),
        "method": method,
        "path": path_name,
        "summary": operation.get("summary"),
        "tags": operation.get("tags") or [],
        "responses": responses,
    }


def extract_schema(name: str, schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties") or {}
    normalized_properties = {}

    for prop_name, prop_schema in sorted(properties.items()):
        normalized_properties[prop_name] = {
            "type": prop_schema.get("type"),
            "format": prop_schema.get("format"),
            "ref": prop_schema.get("$ref"),
        }

    return {
        "name": name,
        "type": schema.get("type"),
        "required": schema.get("required") or [],
        "properties": normalized_properties,
    }


def build_ir(spec: dict[str, Any]) -> dict[str, Any]:
    info = spec.get("info") or {}
    servers = spec.get("servers") or []

    operations = []
    for path_name, path_item in sorted((spec.get("paths") or {}).items()):
        for method in HTTP_METHODS:
            operation = (path_item or {}).get(method)
            if operation:
                operations.append(extract_operation(path_name, method, operation))

    schemas = []
    raw_schemas = (((spec.get("components") or {}).get("schemas")) or {})
    for name, schema in sorted(raw_schemas.items()):
        schemas.append(extract_schema(name, schema))

    return {
        "api": {
            "title": info.get("title"),
            "version": info.get("version"),
            "servers": [server.get("url") for server in servers if isinstance(server, dict)],
        },
        "operations": operations,
        "schemas": schemas,
        "stats": {
            "operation_count": len(operations),
            "schema_count": len(schemas),
        },
    }


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

    spec = load_openapi(input_path)
    ir = build_ir(spec)
    write_ir(ir, output_path)

    print(f"Wrote IR to {output_path}")
    print(
        json.dumps(
            {
                "operations": ir["stats"]["operation_count"],
                "schemas": ir["stats"]["schema_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
