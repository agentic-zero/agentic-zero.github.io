"""
AGENTIC ZERO -- Essential Package Path Normalizer

Problem it solves:
  siop_generator.py, siop_validator.py and architect_siop_bridge.py
  generate filenames with embedded siop_id + timestamp
  (e.g. SIOP-empresa_transportes-otc-20260619083333.json)
  for versioning and idempotency reasons -- this is correct and
  should NOT be changed in those files.

  essential_blueprint.py and the adapters (guardian_adapter.py,
  auditor_adapter.py, delivery_gate.py) expect fixed filenames:
    02_siop/siop_internal.json
    02_siop/siop_validation.json
    03_blueprint/architect_blueprint.json

This script bridges the two conventions without touching either
side. Run it once after customer_pipeline.py and before
agent_developer.py / essential_packager.py.

It always copies the MOST RECENT matching file (by modification time)
to the fixed name expected downstream. The original timestamped file
is preserved for audit/versioning purposes.

Path:
  pioneer_team/architect/normalize_package_paths.py

Usage:
  python normalize_package_paths.py --package-dir clients/inmaculada/otc/essential_package
"""

from __future__ import annotations

import shutil
from pathlib import Path


FIXED_NAMES = {
    "02_siop": [
        # (glob pattern, fixed filename, exclude pattern)
        ("SIOP-*.json", "siop_internal.json", "VAL-"),
        ("VAL-*.json", "siop_validation.json", None),
    ],
    "03_blueprint": [
        ("*_blueprint.json", "architect_blueprint.json", None),
    ],
}


def _most_recent(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)


def normalize_package(package_dir: str | Path) -> list[str]:
    """
    Normalizes filenames inside an essential_package folder.
    Returns a list of human-readable actions taken.
    """
    package_dir = Path(package_dir)
    actions: list[str] = []

    for subfolder, rules in FIXED_NAMES.items():
        folder = package_dir / subfolder
        if not folder.exists():
            actions.append(f"SKIP  {subfolder}/ does not exist yet")
            continue

        for pattern, fixed_name, exclude in rules:
            candidates = [
                p for p in folder.glob(pattern)
                if p.name != fixed_name
                and (exclude is None or not p.name.startswith(exclude))
            ]
            target = folder / fixed_name
            latest = _most_recent(candidates)

            if latest is None:
                if target.exists():
                    actions.append(f"OK    {subfolder}/{fixed_name} already present")
                else:
                    actions.append(f"WARN  {subfolder}/{fixed_name} -- no source file found matching '{pattern}'")
                continue

            shutil.copy2(latest, target)
            actions.append(f"COPY  {subfolder}/{latest.name}  ->  {subfolder}/{fixed_name}")

    return actions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Agentic Zero -- normalize SIOP/Blueprint filenames to the fixed names expected by adapters"
    )
    parser.add_argument("--package-dir", required=True, help="Path to the essential_package folder")
    args = parser.parse_args()

    print("\nEssential Package Path Normalizer")
    print(f"Package: {args.package_dir}\n")

    results = normalize_package(args.package_dir)
    for line in results:
        print(f"  {line}")

    print("\nNext: run agent_developer.py / essential_packager.py")
