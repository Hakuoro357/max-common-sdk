from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.codegen.lib.renderers.typescript_client import render_typescript_client


def load_ir(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError("IR must be a JSON object.")

    return data


def write_output(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a TypeScript client from IR.")
    parser.add_argument("--input", required=True, help="Path to IR JSON file.")
    parser.add_argument("--output", required=True, help="Path to output TypeScript file.")
    args = parser.parse_args()

    ir = load_ir(Path(args.input))
    output = render_typescript_client(ir)
    write_output(output, Path(args.output))

    print(f"Wrote TypeScript client to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
