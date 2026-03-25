from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_ir_schema(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError("IR schema must be a JSON object.")

    return data


def validate_openapi_shape(spec: dict[str, Any]) -> None:
    if not isinstance(spec, dict):
        raise ValueError("OpenAPI document must be a mapping at the root.")

    info = spec.get("info")
    if not isinstance(info, dict):
        raise ValueError("OpenAPI document must contain an info object.")

    if not info.get("title"):
        raise ValueError("OpenAPI info.title is required.")

    if not info.get("version"):
        raise ValueError("OpenAPI info.version is required.")


def validate_ir_shape(ir: dict[str, Any], schema: dict[str, Any]) -> None:
    required_top_level = schema.get("required") or []
    for field_name in required_top_level:
        if field_name not in ir:
            raise ValueError(f"IR missing required top-level field: {field_name}")

    stats = ir.get("stats") or {}
    api = ir.get("api") or {}
    services = ir.get("services") or []
    operations = ir.get("operations") or []
    schemas = ir.get("schemas") or []

    if not api.get("title"):
        raise ValueError("IR api.title is required.")

    if not api.get("version"):
        raise ValueError("IR api.version is required.")

    if not isinstance(services, list):
        raise ValueError("IR services must be a list.")

    if not isinstance(operations, list):
        raise ValueError("IR operations must be a list.")

    if not isinstance(schemas, list):
        raise ValueError("IR schemas must be a list.")

    if stats.get("operation_count") != len(operations):
        raise ValueError("IR stats.operation_count does not match operations length.")

    if stats.get("schema_count") != len(schemas):
        raise ValueError("IR stats.schema_count does not match schemas length.")

    if stats.get("service_count") != len(services):
        raise ValueError("IR stats.service_count does not match services length.")

    operation_ids = set()
    for operation in operations:
        operation_id = operation.get("operation_id")
        if not operation_id:
            raise ValueError("Each IR operation must have operation_id.")
        if operation_id in operation_ids:
            raise ValueError(f"Duplicate IR operation_id detected: {operation_id}")
        operation_ids.add(operation_id)

        if not operation.get("service"):
            raise ValueError(f"Operation {operation_id} must have service.")

        if not operation.get("path"):
            raise ValueError(f"Operation {operation_id} must have path.")

        if not operation.get("method"):
            raise ValueError(f"Operation {operation_id} must have method.")

    known_operation_ids = operation_ids
    for service in services:
        service_name = service.get("name")
        if not service_name:
            raise ValueError("Each IR service must have name.")

        service_operations = service.get("operation_ids")
        if not isinstance(service_operations, list):
            raise ValueError(f"Service {service_name} must have operation_ids list.")

        unknown_ids = sorted(set(service_operations) - known_operation_ids)
        if unknown_ids:
            raise ValueError(f"Service {service_name} references unknown operations: {', '.join(unknown_ids)}")
