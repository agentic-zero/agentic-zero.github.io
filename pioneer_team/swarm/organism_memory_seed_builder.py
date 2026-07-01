"""
AGENTIC ZERO - PIONEER TEAM
Organism Memory Seed Builder v1.0

Role:
  Build semantic memory seeds for each swarm organism.

Input:
  10_swarm/swarm_manifest.json
  10_swarm/runtime/swarm_topology_runtime.json
  10_swarm/runtime/event_catalog.json
  10_swarm/runtime/escalation_routes.json
  10_swarm/organisms/*/siop_internal.json
  10_swarm/organisms/*/organism_blueprint_seed.json

Output:
  11_memory/
    memory_manifest.json
    {ORGANISM_SLUG}/
      semantic_memory_seed.json
      episodic_seed.json
      risk_seed.json
      kpi_seed.json
      learning_contract.json

Recommended path:
  pioneer_team/swarm/organism_memory_seed_builder.py

This module does NOT run The Machine.
It prepares memory seeds so The Machine starts with enterprise-grade semantic context.
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
class MemorySeedEntry:
    organism_id: str
    organism_name: str
    agent_type: str
    domain: str
    memory_folder: str
    semantic_memory_seed: str
    episodic_seed: str
    risk_seed: str
    kpi_seed: str
    learning_contract: str
    ready_for_the_machine: bool


@dataclass
class MemoryManifest:
    memory_manifest_id: str
    created_at: str
    package_dir: str
    swarm_id: str
    parent_process: str
    organisms_count: int
    entries: list[MemorySeedEntry]
    ready_for_the_machine: bool
    outputs: dict[str, str]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    """Must stay byte-identical to organism_to_slug() in
    runtime_core/event_catalog.py, the_machine/observer.py,
    agentic_shield/policy_engine.py, agentic_shield/compliance_engine.py,
    swarm/swarm_topology_validator.py, swarm/swarm_coordinator.py, and
    pioneer_team/swarm/swarm_splitter.py (organism_slug_for()).

    Without stripping the trailing " Organism" suffix first, this would
    slug "Demand Planning Organism" to "DEMAND_PLANNING_ORGANISM" instead
    of "DEMAND_PLANNING" - silently diverging from the
    10_swarm/organisms/<SLUG>/ folder that swarm_splitter.py already
    created for the same organism, breaking any downstream lookup that
    expects the 11_memory/ and 10_swarm/organisms/ folder names to match.
    """
    value = (value or "organism").strip()
    value = re.sub(r"\s*Organism\s*$", "", value, flags=re.IGNORECASE)
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "organism"


def _upper_slug(value: str) -> str:
    return _slug(value).upper()


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


def load_swarm_context(package_dir: str | Path) -> dict[str, Any]:
    package_dir = Path(package_dir)

    manifest_path = package_dir / "10_swarm" / "swarm_manifest.json"
    topology_path = package_dir / "10_swarm" / "runtime" / "swarm_topology_runtime.json"
    event_catalog_path = package_dir / "10_swarm" / "runtime" / "event_catalog.json"
    escalation_routes_path = (
        package_dir / "10_swarm" / "runtime" / "escalation_routes.json"
    )
    shared_context_path = (
        package_dir / "10_swarm" / "runtime" / "shared_context_schema.json"
    )

    manifest = read_json(manifest_path)
    topology = read_json(topology_path)
    event_catalog = read_json(event_catalog_path)
    escalation_routes = read_json(escalation_routes_path)
    shared_context = read_json(shared_context_path)

    if not manifest:
        raise FileNotFoundError(f"Missing swarm manifest: {manifest_path}")

    if not topology:
        raise FileNotFoundError(f"Missing swarm runtime topology: {topology_path}")

    return {
        "package_dir": package_dir,
        "manifest": manifest,
        "topology": topology,
        "event_catalog": event_catalog,
        "escalation_routes": escalation_routes,
        "shared_context": shared_context,
    }


def load_organism_files(organism_folder: str | Path) -> dict[str, Any]:
    organism_folder = Path(organism_folder)

    siop_path = organism_folder / "siop_internal.json"
    seed_path = organism_folder / "organism_blueprint_seed.json"

    siop = read_json(siop_path)
    seed = read_json(seed_path)

    return {
        "folder": organism_folder,
        "siop_path": siop_path,
        "seed_path": seed_path,
        "siop": siop,
        "seed": seed,
    }


def related_events_for_organism(
    organism_id: str, event_catalog: dict[str, Any]
) -> list[dict[str, Any]]:
    events = event_catalog.get("events", [])
    related = []

    for event in events:
        if event.get("source") == organism_id or organism_id in event.get(
            "targets", []
        ):
            related.append(event)

    return related


def related_escalations_for_organism(
    organism_name: str, escalation_routes: dict[str, Any]
) -> list[dict[str, Any]]:
    routes = escalation_routes.get("routes", [])
    related = []

    for route in routes:
        if organism_name.lower() in str(route).lower():
            related.append(route)

    return related


def build_semantic_memory_seed(
    organism: dict[str, Any],
    organism_files: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    siop = organism_files["siop"]
    seed = organism_files["seed"]

    organism_id = organism.get("organism_id", "")
    organism_name = organism.get("organism_name", "")
    event_catalog = context["event_catalog"]
    escalation_routes = context["escalation_routes"]

    return {
        "memory_type": "semantic_memory_seed",
        "created_at": _now(),
        "scope": "private_client_memory",
        "source": "swarm_generation",
        "swarm_id": context["manifest"].get("swarm_id", ""),
        "parent_process": context["manifest"].get("parent_process", ""),
        "organism_id": organism_id,
        "organism_name": organism_name,
        "agent_type": organism.get("agent_type", ""),
        "domain": organism.get("domain", ""),
        "purpose": seed.get("purpose")
        or siop.get("executive_summary", {}).get("validated_description", ""),
        "systems": organism.get("systems", []),
        "frameworks": organism.get("frameworks", []),
        "scor": {
            "level_1_2": siop.get("compliance", {}).get("scor_level_1_2", []),
            "level_3": siop.get("compliance", {}).get("scor_level_3", []),
        },
        "bpmn_processes": siop.get("compliance", {}).get("bpmn_processes", []),
        "data_contract": siop.get("data_requirements", {}),
        "business_rules": siop.get("business_rules", []),
        "autonomy_design": siop.get("autonomy_design", {}),
        "acceptance_criteria": siop.get("acceptance_criteria", {}),
        "dependencies": seed.get("dependencies", {}),
        "event_vocabulary": related_events_for_organism(organism_id, event_catalog),
        "escalation_vocabulary": related_escalations_for_organism(
            organism_name, escalation_routes
        ),
        "shared_context_schema": context["shared_context"],
        "knowledge_boundaries": {
            "private_to_client": True,
            "share_with_platform_meta_memory": False,
            "requires_anonymization_for_meta_learning": True,
            "human_validated": False,
        },
        "memory_governance": {
            "retention": "client_policy",
            "can_be_forgotten": True,
            "can_be_overridden_by_human_expert": True,
            "source_confidence": 0.88,
            "truth_status": "seeded_semantic_context",
        },
    }


def build_episodic_seed(
    organism: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    organism_id = organism.get("organism_id", "")
    organism_name = organism.get("organism_name", "")

    return {
        "memory_type": "episodic_seed",
        "created_at": _now(),
        "organism_id": organism_id,
        "organism_name": organism_name,
        "initial_episode_templates": [
            {
                "episode_type": "organism_started",
                "description": f"{organism_name} received valid swarm context and started execution.",
                "expected_payload": [
                    "scenario_id",
                    "source_organism",
                    "timestamp",
                    "confidence_score",
                ],
            },
            {
                "episode_type": "organism_completed",
                "description": f"{organism_name} completed execution and published output.",
                "expected_payload": [
                    "scenario_id",
                    "output",
                    "confidence_score",
                    "decision_id",
                ],
            },
            {
                "episode_type": "organism_exception",
                "description": f"{organism_name} detected an exception or missing context.",
                "expected_payload": [
                    "scenario_id",
                    "exception_type",
                    "required_action",
                ],
            },
            {
                "episode_type": "organism_conflict",
                "description": f"{organism_name} generated a recommendation conflicting with another organism.",
                "expected_payload": [
                    "scenario_id",
                    "conflict_type",
                    "counterparty_organism",
                    "confidence_delta",
                ],
            },
        ],
        "first_observation_status": "waiting_for_runtime_events",
        "episodic_memory_target": "the_machine/memory/episodic_memory.jsonl",
    }


def build_risk_seed(
    organism: dict[str, Any], organism_files: dict[str, Any]
) -> dict[str, Any]:
    siop = organism_files["siop"]
    hooks = siop.get("learning_hooks", {})

    return {
        "memory_type": "risk_seed",
        "created_at": _now(),
        "organism_id": organism.get("organism_id", ""),
        "organism_name": organism.get("organism_name", ""),
        "risk_categories": [
            "missing_input",
            "low_confidence",
            "conflicting_recommendation",
            "late_signal",
            "policy_boundary",
            "human_override",
            "system_unavailable",
            "data_quality_issue",
        ],
        "failure_patterns": hooks.get("failure_patterns", []),
        "kpi_deviation_signals": hooks.get("kpi_deviation_signals", []),
        "risk_scoring": {
            "low": "confidence >= 0.85 and no policy boundary",
            "medium": "0.70 <= confidence < 0.85 or minor dependency conflict",
            "high": "confidence < 0.70, financial impact, compliance impact or repeated conflict",
            "critical": "irreversible action, regulatory breach, financial commitment or blocked Shield control",
        },
        "shield_escalation_required_for": [
            "high",
            "critical",
            "policy_boundary",
            "regulated_decision",
            "financial_impact_above_threshold",
        ],
    }


def build_kpi_seed(
    organism: dict[str, Any], organism_files: dict[str, Any]
) -> dict[str, Any]:
    siop = organism_files["siop"]
    domain = organism.get("domain", "")

    default_domain_kpis = {
        "planning": [
            "forecast_accuracy",
            "plan_stability",
            "coverage_gap",
            "planning_cycle_time",
        ],
        "supply": ["supplier_otif", "supply_constraint_rate", "lead_time_variance"],
        "operations": ["execution_health", "exception_rate", "cycle_time", "otif_risk"],
        "finance": ["margin_impact", "cash_impact", "working_capital_deviation"],
        "risk": ["risk_score", "risk_resolution_time", "risk_recurrence"],
        "simulation": [
            "simulation_accuracy",
            "scenario_adoption_rate",
            "simulation_deviation",
        ],
        "quality": ["non_conformance_rate", "capa_cycle_time", "repeat_issue_rate"],
        "procurement": [
            "supplier_response_time",
            "purchase_order_exception_rate",
            "price_deviation",
        ],
        "manufacturing": [
            "schedule_adherence",
            "production_deviation",
            "quality_yield",
        ],
        "logistics": ["otif", "carrier_exception_rate", "shipment_delay_rate"],
        "orchestration": [
            "conflict_resolution_time",
            "human_override_rate",
            "swarm_rework_rate",
        ],
    }

    return {
        "memory_type": "kpi_seed",
        "created_at": _now(),
        "organism_id": organism.get("organism_id", ""),
        "organism_name": organism.get("organism_name", ""),
        "domain": domain,
        "kpis": default_domain_kpis.get(
            domain, ["cycle_time", "confidence_score", "exception_rate"]
        ),
        "acceptance_criteria": siop.get("acceptance_criteria", {}),
        "learning_signals": siop.get("learning_hooks", {}).get(
            "kpi_deviation_signals", []
        ),
        "baseline_status": "not_initialized",
        "baseline_source": "requires_runtime_observation",
    }


def build_learning_contract(
    organism: dict[str, Any], organism_files: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    siop = organism_files["siop"]
    hooks = siop.get("learning_hooks", {})

    return {
        "memory_type": "learning_contract",
        "created_at": _now(),
        "organism_id": organism.get("organism_id", ""),
        "organism_name": organism.get("organism_name", ""),
        "agent_type": organism.get("agent_type", ""),
        "the_machine_contract": {
            "must_observe": True,
            "must_store_episodes": True,
            "must_detect_patterns": True,
            "must_not_modify_runtime_without_approval": True,
            "must_respect_private_client_memory": True,
            "can_contribute_anonymized_meta_patterns": False,
        },
        "observation_points": hooks.get("observation_points", []),
        "failure_patterns": hooks.get("failure_patterns", []),
        "feedback_targets": hooks.get("feedback_targets", []),
        "improvement_loop": hooks.get("improvement_loop", []),
        "truth_and_confidence": {
            "seed_confidence": 0.88,
            "runtime_observation_required": True,
            "human_validation_required_for_permanent_rules": True,
        },
        "boundary_governance": {
            "no_irreversible_action_without_human_approval": True,
            "no_cross_client_private_memory_sharing": True,
            "no_policy_change_without_signoff": True,
            "no_financial_commitment_without_threshold_check": True,
        },
    }


def build_memory_for_organism(
    organism: dict[str, Any],
    context: dict[str, Any],
    memory_root: Path,
) -> MemorySeedEntry:
    organism_name = organism.get("organism_name", "")
    organism_id = organism.get("organism_id", "")
    organism_folder = organism.get("folder", "")

    files = load_organism_files(organism_folder)

    folder_name = _upper_slug(organism_name or organism_id)
    memory_folder = memory_root / folder_name
    memory_folder.mkdir(parents=True, exist_ok=True)

    semantic = build_semantic_memory_seed(organism, files, context)
    episodic = build_episodic_seed(organism, context)
    risk = build_risk_seed(organism, files)
    kpi = build_kpi_seed(organism, files)
    contract = build_learning_contract(organism, files, context)

    semantic_path = write_json(memory_folder / "semantic_memory_seed.json", semantic)
    episodic_path = write_json(memory_folder / "episodic_seed.json", episodic)
    risk_path = write_json(memory_folder / "risk_seed.json", risk)
    kpi_path = write_json(memory_folder / "kpi_seed.json", kpi)
    contract_path = write_json(memory_folder / "learning_contract.json", contract)

    ready = all(
        [
            semantic_path.exists(),
            episodic_path.exists(),
            risk_path.exists(),
            kpi_path.exists(),
            contract_path.exists(),
        ]
    )

    return MemorySeedEntry(
        organism_id=organism_id,
        organism_name=organism_name,
        agent_type=organism.get("agent_type", ""),
        domain=organism.get("domain", ""),
        memory_folder=str(memory_folder),
        semantic_memory_seed=str(semantic_path),
        episodic_seed=str(episodic_path),
        risk_seed=str(risk_path),
        kpi_seed=str(kpi_path),
        learning_contract=str(contract_path),
        ready_for_the_machine=ready,
    )


def build_memory_seeds(package_dir: str | Path) -> MemoryManifest:
    context = load_swarm_context(package_dir)
    package_dir = context["package_dir"]

    memory_root = package_dir / "11_memory"
    memory_root.mkdir(parents=True, exist_ok=True)

    manifest = context["manifest"]
    organisms = manifest.get("organisms", [])

    if not organisms:
        raise ValueError("No organisms found in swarm_manifest.json")

    entries = []
    for organism in organisms:
        entries.append(build_memory_for_organism(organism, context, memory_root))

    manifest_path = memory_root / "memory_manifest.json"

    result = MemoryManifest(
        memory_manifest_id=f"MEMORY-SEED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        package_dir=str(package_dir),
        swarm_id=manifest.get("swarm_id", ""),
        parent_process=manifest.get("parent_process", ""),
        organisms_count=len(entries),
        entries=entries,
        ready_for_the_machine=all(e.ready_for_the_machine for e in entries),
        outputs={
            "memory_manifest": str(manifest_path),
            "memory_root": str(memory_root),
        },
        next_step="Run swarm_coordinator_seed_builder.py",
    )

    write_json(manifest_path, asdict(result))
    return result


def run_cli(package_dir: str):
    result = build_memory_seeds(package_dir)

    print("\nOrganism Memory Seed Builder complete")
    print(f"Swarm ID:  {result.swarm_id}")
    print(f"Process:   {result.parent_process}")
    print(f"Organisms: {result.organisms_count}")
    print(f"Ready:     {result.ready_for_the_machine}")

    print("\nMemory seeds:")
    for entry in result.entries:
        print(f"  - {entry.organism_name}: {entry.memory_folder}")

    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")

    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agentic Zero - Organism Memory Seed Builder"
    )
    parser.add_argument(
        "--package-dir", required=True, help="Customer package directory"
    )
    args = parser.parse_args()

    run_cli(args.package_dir)
