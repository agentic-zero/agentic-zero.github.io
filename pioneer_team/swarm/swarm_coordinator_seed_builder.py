"""
AGENTIC ZERO - PIONEER TEAM
Swarm Coordinator Seed Builder v1.0

Role:
  Build the seed contract for the Swarm Coordinator.

The Swarm Coordinator is not a normal organism.
It does not perform a business sub-process.
It coordinates organisms, validates event flow, routes conflicts,
calls the Shield, and emits learning events to The Machine.

Input:
  10_swarm/swarm_manifest.json
  10_swarm/runtime/swarm_topology_runtime.json
  10_swarm/runtime/event_catalog.json
  10_swarm/runtime/escalation_routes.json
  10_swarm/runtime/shared_context_schema.json
  11_memory/memory_manifest.json

Output:
  12_coordinator/
    swarm_coordinator_seed.json
    coordinator_runtime_contract.json
    coordinator_shield_contract.json
    coordinator_learning_contract.json
    coordinator_readiness.json

Recommended path:
  pioneer_team/swarm/swarm_coordinator_seed_builder.py
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class CoordinatorSeedResult:
    coordinator_seed_id: str
    created_at: str
    package_dir: str
    swarm_id: str
    parent_process: str
    organisms_count: int
    ready_for_swarm_generator: bool
    outputs: dict[str, str]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def load_context(package_dir: str | Path) -> dict[str, Any]:
    package_dir = Path(package_dir)

    paths = {
        "manifest": package_dir / "10_swarm" / "swarm_manifest.json",
        "topology": package_dir
        / "10_swarm"
        / "runtime"
        / "swarm_topology_runtime.json",
        "events": package_dir / "10_swarm" / "runtime" / "event_catalog.json",
        "escalations": package_dir / "10_swarm" / "runtime" / "escalation_routes.json",
        "shared_context": package_dir
        / "10_swarm"
        / "runtime"
        / "shared_context_schema.json",
        "memory_manifest": package_dir / "11_memory" / "memory_manifest.json",
    }

    manifest = read_json(paths["manifest"])
    topology = read_json(paths["topology"])
    events = read_json(paths["events"])
    escalations = read_json(paths["escalations"])
    shared_context = read_json(paths["shared_context"])
    memory_manifest = read_json(paths["memory_manifest"])

    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing required inputs for coordinator seed: {missing}"
        )

    return {
        "package_dir": package_dir,
        "paths": paths,
        "manifest": manifest,
        "topology": topology,
        "events": events,
        "escalations": escalations,
        "shared_context": shared_context,
        "memory_manifest": memory_manifest,
    }


def build_swarm_coordinator_seed(ctx: dict[str, Any]) -> dict[str, Any]:
    manifest = ctx["manifest"]
    topology = ctx["topology"]
    events = ctx["events"]
    escalations = ctx["escalations"]
    shared_context = ctx["shared_context"]
    memory_manifest = ctx["memory_manifest"]

    return {
        "seed_type": "swarm_coordinator_seed",
        "created_at": _now(),
        "swarm_id": manifest.get("swarm_id", ""),
        "parent_process": manifest.get("parent_process", ""),
        "coordinator_name": f"{manifest.get('parent_process', 'Swarm')} Coordinator",
        "coordinator_class_name": "SwarmCoordinator",
        "role": "Coordinate organisms, validate event flow, arbitrate conflicts, route escalations and emit learning events.",
        "organisms": manifest.get("organisms", []),
        "runtime_topology": {
            "nodes_count": topology.get("nodes_count", 0),
            "edges_count": topology.get("edges_count", 0),
            "event_count": topology.get("event_count", 0),
            "nodes": topology.get("nodes", []),
            "edges": topology.get("edges", []),
        },
        "event_catalog": events.get("events", []),
        "shared_context_schema": shared_context,
        "memory_manifest": {
            "memory_manifest_id": memory_manifest.get("memory_manifest_id", ""),
            "ready_for_the_machine": memory_manifest.get(
                "ready_for_the_machine", False
            ),
            "entries": memory_manifest.get("entries", []),
        },
        "coordination_capabilities": [
            "receive_swarm_event",
            "validate_shared_context",
            "route_event_to_target_organisms",
            "detect_missing_context",
            "detect_conflicting_recommendations",
            "trigger_constraint_resolution",
            "trigger_agentic_shield",
            "request_human_approval",
            "emit_audit_event",
            "emit_learning_event",
            "emit_swarm_health_event",
        ],
        "non_responsibilities": [
            "Does not execute business sub-process logic.",
            "Does not override Shield decisions.",
            "Does not approve irreversible decisions.",
            "Does not share private client memory across clients.",
            "Does not modify organism runtime code.",
        ],
        "ready_for_generation": True,
    }


def build_runtime_contract(ctx: dict[str, Any]) -> dict[str, Any]:
    manifest = ctx["manifest"]
    events = ctx["events"]
    shared_context = ctx["shared_context"]

    return {
        "contract_type": "coordinator_runtime_contract",
        "created_at": _now(),
        "swarm_id": manifest.get("swarm_id", ""),
        "runtime_modes": ["dry-run", "qa", "live"],
        "required_methods": [
            "receive_event",
            "validate_event",
            "validate_shared_context",
            "route_event",
            "detect_conflict",
            "handle_conflict",
            "handle_escalation",
            "emit_audit_event",
            "emit_learning_event",
            "get_swarm_health",
        ],
        "event_catalog": events.get("events", []),
        "shared_context_schema": shared_context,
        "state_machine": {
            "states": [
                "WAITING",
                "RUNNING",
                "DEGRADED",
                "ESCALATED",
                "BLOCKED",
                "COMPLETED",
            ],
            "initial": "WAITING",
            "terminal": ["COMPLETED", "BLOCKED"],
        },
        "minimum_runtime_outputs": [
            "swarm_events.jsonl",
            "swarm_audit_trail.jsonl",
            "swarm_learning_events.jsonl",
            "swarm_health.json",
        ],
        "dry_run_requirements": [
            "Can simulate event flow without live systems.",
            "Can simulate organism conflict.",
            "Can simulate Shield escalation.",
            "Can generate audit and learning events.",
        ],
    }


def build_shield_contract(ctx: dict[str, Any]) -> dict[str, Any]:
    manifest = ctx["manifest"]
    escalations = ctx["escalations"]

    return {
        "contract_type": "coordinator_shield_contract",
        "created_at": _now(),
        "swarm_id": manifest.get("swarm_id", ""),
        "shield_required": True,
        "escalation_routes": escalations.get("routes", []),
        "shield_controls": {
            "identity_and_access": True,
            "action_thresholds": True,
            "real_time_audit_trails": True,
            "escalation_pathways": True,
            "fail_safes": True,
            "regulatory_compliance": True,
            "human_accountability": True,
            "machine_learning_hooks": True,
        },
        "autonomous_allowed": [
            "route validated events",
            "classify low-risk conflicts",
            "trigger draft recommendations",
            "request organism re-run in dry-run mode",
            "emit health and learning events",
        ],
        "approval_required": [
            "final plan approval",
            "financial impact acceptance",
            "policy threshold change",
            "supplier/customer commitment change",
            "runtime topology change",
        ],
        "always_human": [
            "strategic trade-off",
            "regulated compliance decision",
            "irreversible operational change",
            "cross-client knowledge sharing",
        ],
        "blocking_conditions": [
            "missing required shared context",
            "invalid event schema",
            "conflicting high-impact recommendations",
            "financial impact above threshold",
            "compliance impact detected",
            "Shield decision unavailable",
        ],
    }


def build_learning_contract(ctx: dict[str, Any]) -> dict[str, Any]:
    manifest = ctx["manifest"]
    topology = ctx["topology"]

    return {
        "contract_type": "coordinator_learning_contract",
        "created_at": _now(),
        "swarm_id": manifest.get("swarm_id", ""),
        "parent_process": manifest.get("parent_process", ""),
        "the_machine_observation_required": True,
        "learning_event_streams": [
            "swarm_learning_events.jsonl",
            "swarm_audit_trail.jsonl",
            "swarm_health.json",
        ],
        "observation_points": [
            "swarm_started",
            "organism_event_received",
            "organism_event_routed",
            "missing_context_detected",
            "organism_conflict_detected",
            "constraint_resolution_triggered",
            "shield_escalation_triggered",
            "human_override",
            "swarm_completed",
        ],
        "failure_patterns": [
            "missing_context",
            "broken_dependency",
            "conflicting_recommendation",
            "late_organism_response",
            "low_confidence_recommendation",
            "shield_blocked_action",
            "human_override_repeated",
        ],
        "kpi_deviation_signals": [
            "swarm_cycle_time_increase",
            "coordination_delay",
            "conflict_rate_increase",
            "human_override_rate_increase",
            "delivery_score_drop",
        ],
        "feedback_targets": [
            "swarm_coordinator",
            "swarm_topology_builder",
            "organism_memory_seed_builder",
            "enterprise_architect",
            "agentic_shield",
        ],
        "improvement_loop": [
            "observe coordination event",
            "store episode",
            "detect repeated pattern",
            "recommend topology or Shield rule improvement",
            "require human validation before permanent change",
        ],
        "topology_reference": {
            "nodes_count": topology.get("nodes_count", 0),
            "edges_count": topology.get("edges_count", 0),
            "event_count": topology.get("event_count", 0),
        },
        "memory_governance": {
            "private_client_memory": True,
            "platform_meta_memory_allowed": False,
            "anonymization_required_for_meta_learning": True,
            "human_validation_required_for_permanent_rules": True,
        },
    }


def build_readiness(ctx: dict[str, Any]) -> dict[str, Any]:
    manifest = ctx["manifest"]
    topology = ctx["topology"]
    events = ctx["events"]
    escalations = ctx["escalations"]
    memory = ctx["memory_manifest"]

    issues = []

    if manifest.get("organisms_count", 0) < 2:
        issues.append("Swarm requires at least two organisms.")
    if topology.get("edges_count", 0) < 1:
        issues.append("Swarm requires at least one dependency edge.")
    if not events.get("events"):
        issues.append("Event catalog is empty.")
    if not escalations.get("routes"):
        issues.append("Escalation routes are empty.")
    if not memory.get("ready_for_the_machine", False):
        issues.append("Memory seeds are not ready for The Machine.")

    return {
        "ready_for_swarm_generator": len(issues) == 0,
        "issues": issues,
        "organisms_count": manifest.get("organisms_count", 0),
        "edges_count": topology.get("edges_count", 0),
        "events_count": len(events.get("events", [])),
        "escalation_routes_count": len(escalations.get("routes", [])),
        "memory_ready": memory.get("ready_for_the_machine", False),
        "requires_coordinator_runtime": True,
        "requires_event_bus": True,
        "requires_shield": True,
        "requires_the_machine": True,
    }


def build_coordinator_seed(package_dir: str | Path) -> CoordinatorSeedResult:
    ctx = load_context(package_dir)
    package_dir = ctx["package_dir"]

    out_dir = package_dir / "12_coordinator"
    out_dir.mkdir(parents=True, exist_ok=True)

    seed = build_swarm_coordinator_seed(ctx)
    runtime_contract = build_runtime_contract(ctx)
    shield_contract = build_shield_contract(ctx)
    learning_contract = build_learning_contract(ctx)
    readiness = build_readiness(ctx)

    paths = {
        "swarm_coordinator_seed": out_dir / "swarm_coordinator_seed.json",
        "coordinator_runtime_contract": out_dir / "coordinator_runtime_contract.json",
        "coordinator_shield_contract": out_dir / "coordinator_shield_contract.json",
        "coordinator_learning_contract": out_dir / "coordinator_learning_contract.json",
        "coordinator_readiness": out_dir / "coordinator_readiness.json",
    }

    write_json(paths["swarm_coordinator_seed"], seed)
    write_json(paths["coordinator_runtime_contract"], runtime_contract)
    write_json(paths["coordinator_shield_contract"], shield_contract)
    write_json(paths["coordinator_learning_contract"], learning_contract)
    write_json(paths["coordinator_readiness"], readiness)

    result = CoordinatorSeedResult(
        coordinator_seed_id=f"COORD-SEED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        package_dir=str(package_dir),
        swarm_id=ctx["manifest"].get("swarm_id", ""),
        parent_process=ctx["manifest"].get("parent_process", ""),
        organisms_count=ctx["manifest"].get("organisms_count", 0),
        ready_for_swarm_generator=readiness["ready_for_swarm_generator"],
        outputs={k: str(v) for k, v in paths.items()},
        next_step="Run swarm_generator.py",
    )

    write_json(out_dir / "coordinator_seed_manifest.json", asdict(result))
    result.outputs["coordinator_seed_manifest"] = str(
        out_dir / "coordinator_seed_manifest.json"
    )
    write_json(out_dir / "coordinator_seed_manifest.json", asdict(result))

    return result


def run_cli(package_dir: str):
    result = build_coordinator_seed(package_dir)

    print("\nSwarm Coordinator Seed Builder complete")
    print(f"Swarm ID:  {result.swarm_id}")
    print(f"Process:   {result.parent_process}")
    print(f"Organisms: {result.organisms_count}")
    print(f"Ready:     {result.ready_for_swarm_generator}")

    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")

    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agentic Zero - Swarm Coordinator Seed Builder"
    )
    parser.add_argument(
        "--package-dir", required=True, help="Customer package directory"
    )
    args = parser.parse_args()

    run_cli(args.package_dir)
