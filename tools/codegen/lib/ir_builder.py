from __future__ import annotations

from collections import defaultdict
from typing import Any


IR_VERSION = "1.0.0"


def build_ir(normalized_spec: dict[str, Any]) -> dict[str, Any]:
    info = normalized_spec["info"]
    servers = normalized_spec["servers"]
    operations = normalized_spec["operations"]
    schemas = normalized_spec["schemas"]

    service_map: dict[str, list[str]] = defaultdict(list)
    for operation in operations:
        service_map[operation["service"]].append(operation["operation_id"])

    services = [
        {
            "name": service_name,
            "operation_ids": sorted(operation_ids),
        }
        for service_name, operation_ids in sorted(service_map.items())
    ]

    return {
        "ir_version": IR_VERSION,
        "api": {
            "title": info["title"],
            "version": info["version"],
            "description": info.get("description"),
            "servers": [server["url"] for server in servers],
        },
        "services": services,
        "operations": operations,
        "schemas": schemas,
        "stats": {
            "service_count": len(services),
            "operation_count": len(operations),
            "schema_count": len(schemas),
        },
    }
