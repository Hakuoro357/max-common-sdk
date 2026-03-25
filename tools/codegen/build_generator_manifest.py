from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.codegen.lib.manifest import build_generator_manifest, load_ir


def write_manifest(manifest: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build generator manifest from IR and generated SDK outputs.")
    parser.add_argument("--input", required=True, help="Path to IR JSON file.")
    parser.add_argument("--output", required=True, help="Path to output manifest JSON file.")
    args = parser.parse_args()

    ir = load_ir(Path(args.input))
    manifest = build_generator_manifest(ROOT, ir)
    write_manifest(manifest, Path(args.output))

    print(f"Wrote generator manifest to {args.output}")
    print(json.dumps({"languages": len(manifest["languages"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
