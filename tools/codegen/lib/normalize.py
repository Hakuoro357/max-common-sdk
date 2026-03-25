from __future__ import annotations

from typing import Any


HTTP_METHODS = ("get", "post", "put", "patch", "delete", "options", "head")


def normalize_openapi(spec: dict[str, Any]) -> dict[str, Any]:
    info = spec.get("info") or {}
    servers = spec.get("servers") or []
    tags = spec.get("tags") or []
    paths = spec.get("paths") or {}
    components = spec.get("components") or {}
    schemas = components.get("schemas") or {}

    normalized_servers = [
        {
            "url": server.get("url"),
            "description": server.get("description"),
        }
        for server in servers
        if isinstance(server, dict) and server.get("url")
    ]

    normalized_tags = sorted(
        [
            {
                "name": tag.get("name"),
                "description": tag.get("description"),
            }
            for tag in tags
            if isinstance(tag, dict) and tag.get("name")
        ],
        key=lambda item: item["name"],
    )

    normalized_operations = []
    for path_name, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue

        for method in HTTP_METHODS:
            operation = path_item.get(method)
            if operation:
                normalized_operations.append(normalize_operation(path_name, method, operation))

    normalized_schemas = [normalize_schema(name, schema) for name, schema in sorted(schemas.items())]

    return {
        "info": {
            "title": info.get("title"),
            "version": info.get("version"),
            "description": info.get("description"),
        },
        "servers": normalized_servers,
        "tags": normalized_tags,
        "operations": normalized_operations,
        "schemas": normalized_schemas,
    }


def normalize_operation(path_name: str, method: str, operation: dict[str, Any]) -> dict[str, Any]:
    tags = sorted(operation.get("tags") or [])
    operation_id = operation.get("operationId") or derive_operation_id(path_name, method)
    parameters = operation.get("parameters") or []
    request_body = normalize_request_body(operation.get("requestBody"))

    responses = []
    for status_code, response in sorted((operation.get("responses") or {}).items(), key=lambda item: str(item[0])):
        response_payload = response or {}
        content = response_payload.get("content") or {}

        media_types = []
        for content_type, content_spec in sorted(content.items()):
            schema = (content_spec or {}).get("schema") or {}
            media_types.append(
                {
                    "content_type": content_type,
                    "schema_ref": schema.get("$ref"),
                    "schema_type": schema.get("type"),
                }
            )

        responses.append(
            {
                "status_code": str(status_code),
                "description": response_payload.get("description"),
                "media_types": media_types,
            }
        )

    return {
        "operation_id": operation_id,
        "method": method.lower(),
        "path": path_name,
        "wire_path": operation.get("x-max-wire-path", path_name),
        "summary": operation.get("summary"),
        "description": operation.get("description"),
        "tags": tags,
        "service": derive_service_name(tags, path_name),
        "parameters": normalize_parameters(parameters),
        "request_body": request_body,
        "responses": responses,
    }


def normalize_schema(name: str, schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties") or {}
    required = sorted(schema.get("required") or [])

    normalized_properties = []
    for prop_name, prop_schema in sorted(properties.items()):
        prop = prop_schema or {}
        normalized_properties.append(
            {
                "name": prop_name,
                "type": prop.get("type"),
                "format": prop.get("format"),
                "ref": prop.get("$ref"),
                "enum": prop.get("enum"),
                "items_type": ((prop.get("items") or {}).get("type")),
                "items_ref": ((prop.get("items") or {}).get("$ref")),
                "nullable": bool(prop.get("nullable", False)),
                "required": prop_name in required,
            }
        )

    return {
        "name": name,
        "type": schema.get("type"),
        "enum": schema.get("enum"),
        "required": required,
        "properties": normalized_properties,
    }


def derive_service_name(tags: list[str], path_name: str) -> str:
    if tags:
        return tags[0]

    segments = [segment for segment in path_name.split("/") if segment and not segment.startswith("{")]
    if segments:
        return segments[0].replace("-", "_")

    return "default"


def derive_operation_id(path_name: str, method: str) -> str:
    parts = [segment for segment in path_name.split("/") if segment]
    normalized_parts = []
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            normalized_parts.append(f"by_{part[1:-1]}")
        else:
            normalized_parts.append(part.replace("-", "_"))

    joined = "_".join(normalized_parts) if normalized_parts else "root"
    return f"{method.lower()}_{joined}"


def normalize_parameters(parameters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []

    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue

        schema = parameter.get("schema") or {}
        normalized.append(
            {
                "name": parameter.get("name"),
                "in": parameter.get("in"),
                "required": bool(parameter.get("required", False)),
                "type": schema.get("type"),
                "format": schema.get("format"),
                "ref": schema.get("$ref"),
                "enum": schema.get("enum"),
                "items_type": ((schema.get("items") or {}).get("type")),
                "items_ref": ((schema.get("items") or {}).get("$ref")),
            }
        )

    return sorted(normalized, key=lambda item: (item["in"] or "", item["name"] or ""))


def normalize_request_body(request_body: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(request_body, dict):
        return None

    content = request_body.get("content") or {}
    if not isinstance(content, dict):
        return None

    media_types = []
    for content_type, content_spec in sorted(content.items()):
        schema = ((content_spec or {}).get("schema")) or {}
        media_types.append(
            {
                "content_type": content_type,
                "schema_ref": schema.get("$ref"),
                "schema_type": schema.get("type"),
            }
        )

    return {
        "required": bool(request_body.get("required", False)),
        "media_types": media_types,
    }
