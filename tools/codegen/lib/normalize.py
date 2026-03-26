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
    normalized = normalize_schema_node(schema)
    normalized["name"] = name
    return normalized


def normalize_schema_node(
    schema: dict[str, Any] | None,
    *,
    prop_name: str | None = None,
    required_names: set[str] | None = None,
) -> dict[str, Any]:
    node = schema or {}
    required_names = required_names or set()

    normalized: dict[str, Any] = {
        "type": node.get("type"),
        "format": node.get("format"),
        "ref": node.get("$ref"),
        "enum": node.get("enum"),
        "nullable": bool(node.get("nullable", False)),
        "kind": derive_node_kind(node),
        "required": prop_name in required_names if prop_name is not None else False,
        "required_fields": [],
        "items_type": None,
        "items_ref": None,
        "items": None,
        "variants": [],
        "discriminator": None,
        "additional_properties": None,
        "raw_object": False,
        "properties": [],
    }

    if prop_name is not None:
        normalized["name"] = prop_name

    if normalized["kind"] == "array":
        items_node = normalize_schema_node(node.get("items") or {})
        normalized["items"] = items_node
        normalized["items_type"] = items_node.get("type")
        normalized["items_ref"] = items_node.get("ref")
        return normalized

    if normalized["kind"] == "union":
        normalized["variants"] = [normalize_schema_node(variant) for variant in node.get("oneOf") or []]
        discriminator = node.get("discriminator") or {}
        normalized["discriminator"] = {
            "property_name": discriminator.get("propertyName"),
            "mapping": discriminator.get("mapping") or {},
        }
        return normalized

    if normalized["kind"] == "map":
        additional_properties = node.get("additionalProperties")
        if additional_properties is True:
            normalized["additional_properties"] = {
                "kind": "raw",
                "type": "object",
                "format": None,
                "ref": None,
                "enum": None,
                "nullable": False,
                "required": False,
                "required_fields": [],
                "items_type": None,
                "items_ref": None,
                "items": None,
                "variants": [],
                "discriminator": None,
                "additional_properties": None,
                "raw_object": True,
                "properties": [],
                "required": [],
            }
        else:
            normalized["additional_properties"] = normalize_schema_node(additional_properties or {})
        return normalized

    if normalized["kind"] == "object":
        properties = node.get("properties") or {}
        required = sorted(node.get("required") or [])
        normalized["required_fields"] = required
        normalized["properties"] = [
            normalize_schema_node(prop_schema, prop_name=prop_name, required_names=set(required))
            for prop_name, prop_schema in sorted(properties.items())
        ]
        return normalized

    if normalized["kind"] == "raw":
        normalized["raw_object"] = True

    return normalized


def derive_node_kind(node: dict[str, Any]) -> str:
    if node.get("$ref"):
        return "ref"

    if node.get("oneOf"):
        return "union"

    if node.get("enum"):
        return "enum"

    node_type = node.get("type")
    if node_type == "array":
        return "array"

    if node_type == "object":
        if node.get("properties"):
            return "object"
        if "additionalProperties" in node:
            return "map"
        return "raw"

    return "scalar"


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

        normalized_parameter = normalize_schema_node(parameter.get("schema") or {})
        normalized_parameter["name"] = parameter.get("name")
        normalized_parameter["in"] = parameter.get("in")
        normalized_parameter["required"] = bool(parameter.get("required", False))
        normalized.append(normalized_parameter)

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
