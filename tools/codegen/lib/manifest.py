from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TS_OPERATION_RE = re.compile(r"async\s+([A-Za-z_][A-Za-z0-9_]*)\(")
PY_OPERATION_RE = re.compile(r"^\s+def\s+([A-Za-z_][A-Za-z0-9_]*)\(", flags=re.MULTILINE)
CS_OPERATION_RE = re.compile(r"public\s+Task<[^>]+>\s+([A-Za-z_][A-Za-z0-9_]*)Async\(")


def load_ir(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError("IR must be a JSON object.")

    return data


def build_generator_manifest(root: Path, ir: dict[str, Any]) -> dict[str, Any]:
    operations = sorted(operation["operation_id"] for operation in ir.get("operations", []))

    languages = [
        build_typescript_entry(root, operations),
        build_python_entry(root, operations),
        build_csharp_entry(root, operations),
    ]

    return {
        "manifest_version": "1.0.0",
        "ir_version": ir.get("ir_version"),
        "api_version": (ir.get("api") or {}).get("version"),
        "languages": languages,
    }


def build_typescript_entry(root: Path, expected_operations: list[str]) -> dict[str, Any]:
    package_root = root / "sdks" / "typescript" / "client"
    generated_entry = package_root / "generated" / "index.ts"
    runtime_dir = package_root / "runtime"

    generated_files = [
        rel(root, generated_entry),
    ]
    runtime_files = sorted(rel(root, path) for path in runtime_dir.glob("*.ts"))
    supported_operations = extract_operations(generated_entry, TS_OPERATION_RE)

    return {
        "language": "typescript",
        "package_name": "@max/client",
        "package_root": rel(root, package_root),
        "entrypoint": rel(root, generated_entry),
        "generated_files": generated_files,
        "runtime_files": runtime_files,
        "supported_operations": supported_operations,
        "operation_count": len(supported_operations),
        "coverage_complete": supported_operations == expected_operations,
    }


def build_python_entry(root: Path, expected_operations: list[str]) -> dict[str, Any]:
    package_root = root / "sdks" / "python" / "client"
    generated_entry = package_root / "src" / "max_client" / "generated" / "client.py"
    runtime_dir = package_root / "src" / "max_client" / "runtime"

    generated_files = [
        rel(root, generated_entry),
        rel(root, package_root / "src" / "max_client" / "generated" / "__init__.py"),
    ]
    runtime_files = sorted(rel(root, path) for path in runtime_dir.glob("*.py"))
    supported_operations = extract_operations(generated_entry, PY_OPERATION_RE)

    return {
        "language": "python",
        "package_name": "max-client",
        "package_root": rel(root, package_root),
        "entrypoint": rel(root, generated_entry),
        "generated_files": generated_files,
        "runtime_files": runtime_files,
        "supported_operations": supported_operations,
        "operation_count": len(supported_operations),
        "coverage_complete": supported_operations == expected_operations,
    }


def build_csharp_entry(root: Path, expected_operations: list[str]) -> dict[str, Any]:
    package_root = root / "sdks" / "csharp" / "client" / "Max.Client"
    generated_entry = package_root / "Generated" / "MaxBotApiClient.g.cs"
    runtime_dir = package_root / "Runtime"

    generated_files = [
        rel(root, generated_entry),
    ]
    runtime_files = sorted(rel(root, path) for path in runtime_dir.glob("*.cs"))
    supported_operations = [
        csharp_method_to_operation_id(operation[: -len("Async")] if operation.endswith("Async") else operation)
        for operation in extract_operations(generated_entry, CS_OPERATION_RE)
    ]

    return {
        "language": "csharp",
        "package_name": "Max.Client",
        "package_root": rel(root, package_root),
        "entrypoint": rel(root, generated_entry),
        "generated_files": generated_files,
        "runtime_files": runtime_files,
        "supported_operations": supported_operations,
        "operation_count": len(supported_operations),
        "coverage_complete": supported_operations == expected_operations,
    }


def extract_operations(path: Path, pattern: re.Pattern[str]) -> list[str]:
    content = path.read_text(encoding="utf-8")
    return sorted({name for name in pattern.findall(content) if not name.startswith("__")})


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def csharp_method_to_operation_id(value: str) -> str:
    return value[:1].lower() + value[1:]
