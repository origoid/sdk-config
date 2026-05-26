#!/usr/bin/env python3
"""Sync mintlify-poc/openapi.json → sdk-config/fern/openapi/openapi.json

Strips x-codeSamples extensions which break fern-typescript-node-sdk.
Docs site (Mintlify) keeps them — only the SDK generator copy is stripped.

Usage:
  python3 scripts/sync-openapi.py
  # or from sdk-config root:
  ./scripts/sync-openapi.py
"""
import json
from pathlib import Path

SRC = Path("/Users/macbook/Dessarrollos/mintlify-poc/openapi.json")
DST = Path(__file__).resolve().parent.parent / "fern" / "openapi" / "openapi.json"


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: source not found: {SRC}")
        return 1

    with SRC.open() as f:
        spec = json.load(f)

    stripped = 0
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if isinstance(op, dict) and "x-codeSamples" in op:
                op.pop("x-codeSamples")
                stripped += 1

    DST.parent.mkdir(parents=True, exist_ok=True)
    with DST.open("w") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Synced {SRC} → {DST}")
    print(f"Stripped x-codeSamples from {stripped} operations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
