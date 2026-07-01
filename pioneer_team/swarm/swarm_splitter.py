"""
AGENTIC ZERO - PIONEER TEAM
Swarm Splitter v1.0

Role:
  Transform a decomposed Level 1 SIOP into a swarm-ready folder structure.

Input:
  00_enterprise_intent/siop_decomposition.json
  00_enterprise_intent/swarm_coordination_siop.json
  00_enterprise_intent/level_2_siops/*.json

Output:
  10_swarm/
    swarm_manifest.json
    organisms/
      {ORGANISM_SLUG}/
        siop_internal.json
        organism_blueprint_seed.json
    coordination/
      swarm_coordination_siop.json
      swarm_topology.json

Recommended path:
  pioneer_team/swarm/swarm_splitter.py

This module does NOT generate code.
It prepares the factory structure for swarm generation.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class OrganismEntry:
    organism_id: str
    organism_name: str
    agent_type: str
    domain: str
    folder: str
    siop_path: str
    seed_path: str
    upstream_dependencies: list[str]
    downstream_dependencies: list[str]
    systems: list[str]
    frameworks: list[str]


@dataclass
class SwarmManifest:
    swarm_id: str
    created_at: str
    package_dir: str
    parent_process: str
    route: str
    organisms_count: int
    organisms: list[OrganismEntry]
    coordination_siop_path: str
    topology_path: str
    ready_for_swarm_generator: bool
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    """Must stay byte-identical to organism_to_slug() in
    runtime_core/event_catalog.py, the_machine/observer.py,
    agentic_shield/policy_engine.py, agentic_shield/compliance_engine.py,
    swarm/swarm_topology_validator.py and swarm/swarm_coordinator.py.

    Strips a trailing " Organism" suffix BEFORE slugifying. Without this,
    using the canonical `organism` field directly (e.g. "Demand Planning
    Organism") would slug to "demand_planning_organism" instead of
    "demand_planning" - silently diverging from every module above that
    expects the suffix-stripped form. This was previously masked by
    accident: the old lookup order tried `name` (e.g. "Demand Planning",
    no suffix) before `organism`, so the suffix issue never surfaced. Now
    that `organism` is used directly (see organism_slug_for() below), the
    suffix MUST be stripped here to match.
    """
    value = (value or "organism").strip()
    value = re.sub(r"\s*Organism\s*$", "", value, flags=re.IGNORECASE)
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "organism"


def _upper_slug(value: str) -> str:
    return _slug(value).upper()


def organism_slug_for(level2: dict[str, Any]) -> str:
    """Canonical identifier is `organism` (agreed in SWARM_ARCHITECTURE_v1.md
    section 5) - no fallback to `name`, which is presentation metadata
    only. `agent_type` remains as a last-resort fallback only for
    malformed input that is missing `organism` entirely, not as a
    routine alternative.
    """
    return _upper_slug(
        level2.get("organism") or level2.get("agent_type") or "organism"
    )


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


def list_level2_siops(package_dir: Path) -> list[Path]:
    l2_dir = package_dir / "00_enterprise_intent" / "level_2_siops"
    if not l2_dir.exists():
        return []
    return sorted(l2_dir.glob("*.json"))


def normalize_level2_to_siop(level2: dict[str, Any]) -> dict[str, Any]:
    """
    Convert Level2SIOP into a standard SIOP-like artifact that downstream
    Architect Bridge / swarm generator can consume.
    """
    return {
        "siop_id": level2.get("siop_id", ""),
        "process_id": level2.get("siop_id", ""),
        "process_name": level2.get("name", ""),
        "parent_process": level2.get("parent_process", ""),
        "organism": level2.get("organism", ""),
        "agent_type": level2.get("agent_type", ""),
        "domain": level2.get("domain", ""),
        "executive_summary": {
            "process_name": level2.get("name", ""),
            "validated_description": level2.get("purpose", ""),
            "business_goal": f"Autonomously support {level2.get('name', '')} as part of a coordinated swarm.",
            "roi_baseline": "To be calculated by swarm economics engine.",
        },
        "business_context": {
            "sector": "",
            "erp": "",
            "systems": level2.get("systems", []),
            "frameworks": level2.get("frameworks", []),
            "parent_process": level2.get("parent_process", ""),
            "domain": level2.get("domain", ""),
        },
        "process_flow": [
            {
                "step_id": "STEP-01",
                "name": "Receive upstream context",
                "system": "Swarm Coordinator",
                "inputs": level2.get("inputs", []),
                "outputs": ["validated context"],
                "rule": "Only validated swarm context can trigger organism execution.",
                "confidence": 0.90,
            },
            {
                "step_id": "STEP-02",
                "name": f"Execute {level2.get('name', '')}",
                "system": ", ".join(level2.get("systems", [])),
                "inputs": level2.get("inputs", []),
                "outputs": level2.get("outputs", []),
                "rule": level2.get("purpose", ""),
                "confidence": 0.88,
            },
            {
                "step_id": "STEP-03",
                "name": "Publish organism output",
                "system": "Swarm Event Bus",
                "inputs": level2.get("outputs", []),
                "outputs": ["swarm event", "audit event", "learning event"],
                "rule": "Every organism output must be published as a traceable swarm event.",
                "confidence": 0.92,
            },
        ],
        "data_requirements": {
            "inputs": level2.get("inputs", []),
            "outputs": level2.get("outputs", []),
            "systems": level2.get("systems", []),
        },
        "business_rules": [
            "Do not act on incomplete upstream context.",
            "Escalate low-confidence or conflicting recommendations.",
            "Emit audit and learning events for every decision.",
        ],
        "compliance": {
            "frameworks": level2.get("frameworks", []),
            "scor_level_1_2": level2.get("scor_level_1_2", []),
            "scor_level_3": level2.get("scor_level_3", []),
            "bpmn_processes": level2.get("bpmn_processes", []),
        },
        "autonomy_design": level2.get("autonomy_design", {}),
        "acceptance_criteria": {
            "kpis": level2.get("acceptance_criteria", []),
            "tests": [
                "Organism receives upstream context.",
                "Organism produces traceable output.",
                "Organism emits audit and learning events.",
                "Low-confidence output escalates.",
            ],
        },
        "learning_hooks": level2.get("learning_hooks", {}),
        "dependencies": {
            "upstream": level2.get("upstream_dependencies", []),
            "downstream": level2.get("downstream_dependencies", []),
        },
        "ready_for_swarm_blueprint": True,
    }


def build_organism_seed(level2: dict[str, Any]) -> dict[str, Any]:
    return {
        "organism_id": level2.get("siop_id", ""),
        "organism_name": level2.get("organism", ""),
        "agent_type": level2.get("agent_type", ""),
        "domain": level2.get("domain", ""),
        "purpose": level2.get("purpose", ""),
        "systems": level2.get("systems", []),
        "frameworks": level2.get("frameworks", []),
        "inputs": level2.get("inputs", []),
        "outputs": level2.get("outputs", []),
        "dependencies": {
            "upstream": level2.get("upstream_dependencies", []),
            "downstream": level2.get("downstream_dependencies", []),
        },
        "autonomy_design": level2.get("autonomy_design", {}),
        "learning_hooks": level2.get("learning_hooks", {}),
        "blueprint_requirements": {
            "must_emit_swarm_events": True,
            "must_emit_audit_events": True,
            "must_emit_learning_events": True,
            "must_support_dry_run": True,
            "must_support_escalation": True,
            "must_support_shield_arbitration": True,
        },
        "ready_for_blueprint_generation": True,
    }


def build_topology(
    level2_items: list[dict[str, Any]], coordination: dict[str, Any]
) -> dict[str, Any]:
    nodes = []
    edges = []

    by_id = {item.get("siop_id", ""): item for item in level2_items}

    for item in level2_items:
        nodes.append(
            {
                "id": item.get("siop_id", ""),
                "label": item.get("organism", ""),
                "agent_type": item.get("agent_type", ""),
                "domain": item.get("domain", ""),
                "systems": item.get("systems", []),
            }
        )

        for dst in item.get("downstream_dependencies", []):
            target = by_id.get(dst)
            edges.append(
                {
                    "from": item.get("siop_id", ""),
                    "to": dst,
                    "from_label": item.get("organism", ""),
                    "to_label": target.get("organism", "") if target else dst,
                    "event": f"{_slug(item.get('name', 'organism'))}_updated",
                }
            )

    return {
        "topology_id": f"TOPOLOGY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "created_at": _now(),
        "type": "event_driven_swarm",
        "nodes": nodes,
        "edges": edges,
        "coordination_rules": coordination.get("coordination_rules", []),
        "shield_arbitration": coordination.get("shield_arbitration", {}),
        "shared_context": coordination.get("shared_context", []),
        "learning_hooks": coordination.get("learning_hooks", {}),
        "ready_for_swarm_coordinator": True,
    }


def split_swarm(package_dir: str | Path) -> SwarmManifest:
    package_dir = Path(package_dir)

    decomposition_path = (
        package_dir / "00_enterprise_intent" / "siop_decomposition.json"
    )
    coordination_path = (
        package_dir / "00_enterprise_intent" / "swarm_coordination_siop.json"
    )

    decomposition = read_json(decomposition_path)
    coordination = read_json(coordination_path)

    level2_paths = list_level2_siops(package_dir)
    if not level2_paths:
        raise FileNotFoundError(
            f"No Level 2 SIOPs found under {package_dir / '00_enterprise_intent' / 'level_2_siops'}"
        )

    swarm_dir = package_dir / "10_swarm"
    organisms_dir = swarm_dir / "organisms"
    coordination_dir = swarm_dir / "coordination"

    organisms_dir.mkdir(parents=True, exist_ok=True)
    coordination_dir.mkdir(parents=True, exist_ok=True)

    level2_items = [read_json(p) for p in level2_paths]
    organism_entries: list[OrganismEntry] = []

    for level2 in level2_items:
        organism_slug = organism_slug_for(level2)
        organism_dir = organisms_dir / organism_slug
        organism_dir.mkdir(parents=True, exist_ok=True)

        siop_internal = normalize_level2_to_siop(level2)
        seed = build_organism_seed(level2)

        siop_path = write_json(organism_dir / "siop_internal.json", siop_internal)
        seed_path = write_json(organism_dir / "organism_blueprint_seed.json", seed)

        organism_entries.append(
            OrganismEntry(
                organism_id=level2.get("siop_id", ""),
                organism_name=level2.get("organism", ""),
                agent_type=level2.get("agent_type", ""),
                domain=level2.get("domain", ""),
                folder=str(organism_dir),
                siop_path=str(siop_path),
                seed_path=str(seed_path),
                upstream_dependencies=level2.get("upstream_dependencies", []),
                downstream_dependencies=level2.get("downstream_dependencies", []),
                systems=level2.get("systems", []),
                frameworks=level2.get("frameworks", []),
            )
        )

    copied_coordination = write_json(
        coordination_dir / "swarm_coordination_siop.json", coordination
    )
    topology = build_topology(level2_items, coordination)
    topology_path = write_json(coordination_dir / "swarm_topology.json", topology)

    parent_process = (
        decomposition.get("parent_process")
        or decomposition.get("level_1_process")
        or "Swarm Process"
    )

    manifest_path = swarm_dir / "swarm_manifest.json"

    manifest = SwarmManifest(
        swarm_id=f"SWARM-{_upper_slug(parent_process)}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        package_dir=str(package_dir),
        parent_process=parent_process,
        route="SWARM",
        organisms_count=len(organism_entries),
        organisms=organism_entries,
        coordination_siop_path=str(copied_coordination),
        topology_path=str(topology_path),
        ready_for_swarm_generator=True,
        next_step="Run swarm_generator.py",
    )

    write_json(manifest_path, asdict(manifest))
    return manifest


def run_cli(package_dir: str):
    manifest = split_swarm(package_dir)

    print("\nSwarm Splitter complete")
    print(f"Swarm ID:    {manifest.swarm_id}")
    print(f"Process:     {manifest.parent_process}")
    print(f"Organisms:   {manifest.organisms_count}")
    print(f"Ready:       {manifest.ready_for_swarm_generator}")

    print("\nOrganisms:")
    for org in manifest.organisms:
        print(f"  - {org.organism_name} -> {org.folder}")

    print("\nOutput:")
    print(
        f"  swarm_manifest: {Path(manifest.package_dir) / '10_swarm' / 'swarm_manifest.json'}"
    )
    print(f"  topology:       {manifest.topology_path}")

    print(f"\nNext: {manifest.next_step}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Swarm Splitter")
    parser.add_argument(
        "--package-dir", required=True, help="Customer package directory"
    )
    args = parser.parse_args()

    run_cli(args.package_dir)
