"""
AGENTIC ZERO - PIONEER TEAM
System Detector v1.0

Role:
  Detect interconnected enterprise systems from a SIOP / Functional Analysis / free-text intent
  using the semantic ontology stored in:

    pioneer_team/architect/knowledge/interconnected_systems_ontology.json

Output:
  00_enterprise_intent/system_detection.json

This module does not build anything.
It only detects what kind of enterprise organism may be required.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class DetectedSystem:
    system_id: str
    name: str
    route: str
    confidence: float
    matched_keywords: list[str]
    default_level2_processes: list[str]
    scor_level_1_2: list[str]
    scor_level_3: list[str]
    bpmn_processes: list[str]
    frameworks: list[str]


@dataclass
class SystemDetectionResult:
    detection_id: str
    created_at: str
    source_path: str
    package_dir: str
    systems_detected: list[DetectedSystem]
    route_recommendation: str
    swarm_required: bool
    agentic_one_possible: bool
    confidence: float
    notes: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root() -> Path:
    """
    Find the repo root by looking for the actual marker that matters:
    pioneer_team/architect/knowledge/interconnected_systems_ontology.json.
    This avoids hardcoding the repo folder name ("agentic-zero"), which
    breaks in any environment where the folder has a different name
    (sandbox testing, a fork, a different machine, a symlinked checkout).
    Falls back to cwd if the marker is never found, same as the old
    behaviour's worst case.
    """
    marker = Path("pioneer_team") / "architect" / "knowledge" / "interconnected_systems_ontology.json"
    root = Path.cwd()
    while True:
        if (root / marker).exists():
            return root
        if root.parent == root:
            return Path.cwd()
        root = root.parent


def read_json(
    path: str | Path, default: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return default or {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def flatten_text(obj: Any) -> str:
    if obj is None:
        return ""
    if isinstance(obj, dict):
        return " ".join(flatten_text(v) for v in obj.values())
    if isinstance(obj, list):
        return " ".join(flatten_text(v) for v in obj)
    return str(obj)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9áéíóúñü\s\-/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_ontology(path: Optional[str | Path] = None) -> dict[str, Any]:
    if path:
        ontology_path = Path(path)
    else:
        ontology_path = (
            repo_root()
            / "pioneer_team"
            / "architect"
            / "knowledge"
            / "interconnected_systems_ontology.json"
        )

    if not ontology_path.exists():
        raise FileNotFoundError(f"Ontology not found: {ontology_path}")

    return read_json(ontology_path)


def keyword_match_score(text: str, keywords: list[str]) -> tuple[float, list[str]]:
    matched = []
    for kw in keywords:
        kw_norm = normalize_text(kw)
        if not kw_norm:
            continue
        # Word-boundary match instead of raw substring match.
        # Raw substring matching caused false positives on short keywords:
        # "eam" matched inside "empresa", "mes" matched inside "meses"/"comestibles",
        # "sop" matched inside filenames like "...siop_internal.json".
        # \b works correctly for both single-word keywords ("eam") and
        # multi-word keywords ("sales and operations planning") since it
        # anchors on the keyword's own start/end, not on individual words inside it.
        pattern = r"\b" + re.escape(kw_norm) + r"\b"
        if re.search(pattern, text):
            matched.append(kw)

    if not keywords:
        return 0.0, []

    # Confidence curve:
    # 1 match -> 0.70, 2 -> 0.82, 3 -> 0.90, 4+ -> 0.96
    count = len(matched)
    if count == 0:
        return 0.0, []
    if count == 1:
        return 0.70, matched
    if count == 2:
        return 0.82, matched
    if count == 3:
        return 0.90, matched
    return 0.96, matched


def detect_systems_from_payload(
    payload: dict[str, Any],
    source_path: str | Path,
    package_dir: str | Path,
    ontology_path: Optional[str | Path] = None,
) -> SystemDetectionResult:
    ontology = load_ontology(ontology_path)
    text = normalize_text(flatten_text(payload))

    detected: list[DetectedSystem] = []

    for system in ontology.get("systems", []):
        score, matched = keyword_match_score(text, system.get("keywords", []))
        if score <= 0:
            continue

        detected.append(
            DetectedSystem(
                system_id=system.get("id", ""),
                name=system.get("name", ""),
                route=system.get("route", "SWARM"),
                confidence=score,
                matched_keywords=matched,
                default_level2_processes=system.get("default_level2_processes", []),
                scor_level_1_2=system.get("scor_level_1_2", []),
                scor_level_3=system.get("scor_level_3", []),
                bpmn_processes=system.get("bpmn_processes", []),
                frameworks=system.get("frameworks", []),
            )
        )

    detected.sort(key=lambda x: x.confidence, reverse=True)

    if detected:
        route = "SWARM"
        swarm_required = True
        confidence = round(
            sum(d.confidence for d in detected[:3]) / min(3, len(detected)), 2
        )
        notes = "Interconnected enterprise system detected. Swarm decomposition is recommended."
    else:
        route = "UNKNOWN"
        swarm_required = False
        confidence = 0.0
        notes = "No interconnected system detected from ontology."

    return SystemDetectionResult(
        detection_id=f"SYSDET-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        source_path=str(source_path),
        package_dir=str(package_dir),
        systems_detected=detected,
        route_recommendation=route,
        swarm_required=swarm_required,
        agentic_one_possible=False,
        confidence=confidence,
        notes=notes,
    )


def detect_systems(
    source_path: str | Path,
    package_dir: str | Path,
    ontology_path: Optional[str | Path] = None,
) -> SystemDetectionResult:
    payload = read_json(source_path)
    return detect_systems_from_payload(payload, source_path, package_dir, ontology_path)


def save_detection(result: SystemDetectionResult) -> Path:
    out_dir = Path(result.package_dir) / "00_enterprise_intent"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "system_detection.json"
    write_json(out, asdict(result))
    return out


def run_cli(source_path: str, package_dir: str, ontology_path: Optional[str] = None):
    result = detect_systems(source_path, package_dir, ontology_path)
    out = save_detection(result)

    print("\nSystem Detector complete")
    print(f"Route recommendation: {result.route_recommendation}")
    print(f"Swarm required:       {result.swarm_required}")
    print(f"Confidence:           {int(result.confidence * 100)}%")
    print(f"Systems detected:     {len(result.systems_detected)}")

    for system in result.systems_detected:
        print(
            f"  - {system.name}: {int(system.confidence * 100)}% | {', '.join(system.matched_keywords[:5])}"
        )

    print(f"\nOutput: {out}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - System Detector")
    parser.add_argument(
        "--source", required=True, help="Path to SIOP / Functional Analysis JSON"
    )
    parser.add_argument(
        "--package-dir", required=True, help="Customer package directory"
    )
    parser.add_argument("--ontology", default=None, help="Optional ontology path")
    args = parser.parse_args()

    run_cli(args.source, args.package_dir, args.ontology)
