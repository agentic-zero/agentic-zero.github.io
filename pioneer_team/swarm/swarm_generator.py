"""
AGENTIC ZERO - PIONEER TEAM
Swarm Generator v1.0

Role:
  Generate the first runnable multi-organism swarm runtime structure.

Input:
  10_swarm/swarm_manifest.json
  10_swarm/organisms/*/siop_internal.json
  10_swarm/organisms/*/organism_blueprint_seed.json
  10_swarm/runtime/*
  12_coordinator/*

Output:
  13_swarm_runtime/
    swarm_runtime_manifest.json
    coordinator/
      swarm_coordinator_runtime.py
      coordinator_config.json
    organisms/
      {ORGANISM}/
        architect_blueprint.json
        agent_runtime.py
        organism_config.json

Recommended path:
  pioneer_team/swarm/swarm_generator.py
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class GeneratedOrganism:
    organism_id: str
    organism_name: str
    agent_type: str
    folder: str
    blueprint_path: str
    runtime_path: str
    config_path: str
    ready: bool


@dataclass
class SwarmRuntimeManifest:
    swarm_runtime_id: str
    created_at: str
    package_dir: str
    swarm_id: str
    parent_process: str
    organisms_generated: int
    coordinator_generated: bool
    ready: bool
    organisms: list[GeneratedOrganism]
    outputs: dict[str, str]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "item").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "item"


def organism_slug(value: str) -> str:
    """Use this specifically for organism identifiers (organism_name /
    organism), never for system names. Must stay byte-identical to
    organism_to_slug() in runtime_core/event_catalog.py,
    the_machine/observer.py, agentic_shield/policy_engine.py,
    agentic_shield/compliance_engine.py, swarm/swarm_topology_validator.py,
    swarm/swarm_coordinator.py, and pioneer_team/swarm/swarm_splitter.py.

    Strips the trailing " Organism" suffix before slugifying - generic
    _slug() above does NOT do this and must not be changed, since it is
    also used for system names (e.g. "SAP IBP" -> "SAP_IBP_HOST" for env
    var naming at lines 191-192), which have no such suffix to strip.
    """
    value = (value or "organism").strip()
    value = re.sub(r"\s*Organism\s*$", "", value, flags=re.IGNORECASE)
    return _slug(value)


def _pascal(value: str) -> str:
    words = re.sub(r"[^a-zA-Z0-9]+", " ", value or "Agent").split()
    return "".join(w.capitalize() for w in words) or "Agent"


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


def write_text(path: str | Path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def load_context(package_dir: str | Path) -> dict[str, Any]:
    package_dir = Path(package_dir)

    paths = {
        "swarm_manifest": package_dir / "10_swarm" / "swarm_manifest.json",
        "topology_runtime": package_dir
        / "10_swarm"
        / "runtime"
        / "swarm_topology_runtime.json",
        "event_catalog": package_dir / "10_swarm" / "runtime" / "event_catalog.json",
        "escalation_routes": package_dir
        / "10_swarm"
        / "runtime"
        / "escalation_routes.json",
        "shared_context": package_dir
        / "10_swarm"
        / "runtime"
        / "shared_context_schema.json",
        "coordinator_seed": package_dir
        / "12_coordinator"
        / "swarm_coordinator_seed.json",
        "coordinator_runtime_contract": package_dir
        / "12_coordinator"
        / "coordinator_runtime_contract.json",
        "coordinator_shield_contract": package_dir
        / "12_coordinator"
        / "coordinator_shield_contract.json",
        "coordinator_learning_contract": package_dir
        / "12_coordinator"
        / "coordinator_learning_contract.json",
        "coordinator_readiness": package_dir
        / "12_coordinator"
        / "coordinator_readiness.json",
    }

    missing = [k for k, p in paths.items() if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required swarm generator inputs: {missing}")

    return {
        "package_dir": package_dir,
        "paths": paths,
        "swarm_manifest": read_json(paths["swarm_manifest"]),
        "topology_runtime": read_json(paths["topology_runtime"]),
        "event_catalog": read_json(paths["event_catalog"]),
        "escalation_routes": read_json(paths["escalation_routes"]),
        "shared_context": read_json(paths["shared_context"]),
        "coordinator_seed": read_json(paths["coordinator_seed"]),
        "coordinator_runtime_contract": read_json(
            paths["coordinator_runtime_contract"]
        ),
        "coordinator_shield_contract": read_json(paths["coordinator_shield_contract"]),
        "coordinator_learning_contract": read_json(
            paths["coordinator_learning_contract"]
        ),
        "coordinator_readiness": read_json(paths["coordinator_readiness"]),
    }


def build_organism_blueprint(
    organism: dict[str, Any], siop: dict[str, Any], seed: dict[str, Any]
) -> dict[str, Any]:
    agent_type = organism.get("agent_type", "")
    class_name = _pascal(agent_type)

    return {
        "blueprint_id": f"BP-{organism.get('organism_id', '')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "created_at": _now(),
        "process_id": organism.get("organism_id", ""),
        "agent_class_name": class_name,
        "agent_description": seed.get("purpose", ""),
        "organism_name": organism.get("organism_name", ""),
        "agent_type": agent_type,
        "domain": organism.get("domain", ""),
        "systems": organism.get("systems", []),
        "frameworks": organism.get("frameworks", []),
        "steps": siop.get("process_flow", []),
        "connectors": [
            {
                "name": f"{_pascal(system)}Connector",
                "type": "mock_connector",
                "system": system,
                "env_var_host": f"{_slug(system).upper()}_HOST",
                "env_var_key": f"{_slug(system).upper()}_KEY",
                "operations": ["read", "validate", "write_event"],
                "dry_run_mock": True,
            }
            for system in organism.get("systems", [])
        ],
        "escalations": [
            {
                "trigger": "low_confidence",
                "condition": "confidence < threshold",
                "recipient_env_var": "ESCALATION_PROCESS_OWNER",
                "action": "pause_and_escalate",
                "auto_resolvable": False,
                "resolution_hint": "Review organism output and shared swarm context.",
            }
        ],
        "shield_requirements": [
            "identity_and_access",
            "action_thresholds",
            "real_time_audit_trails",
            "escalation_pathways",
            "fail_safes",
            "human_accountability",
            "machine_learning_hooks",
            "swarm_coordination_boundary",
        ],
        "autonomous_actions": siop.get("autonomy_design", {}).get(
            "autonomous_actions", []
        ),
        "approval_required": siop.get("autonomy_design", {}).get(
            "approval_required", []
        ),
        "always_human": siop.get("autonomy_design", {}).get("always_human", []),
        "kpis": siop.get("acceptance_criteria", {}).get("kpis", []),
        "learning_hooks": siop.get("learning_hooks", {}),
        "dependencies": seed.get("dependencies", {}),
        "ready_for_runtime": True,
    }


def generate_organism_runtime(class_name: str, blueprint: dict[str, Any]) -> str:
    process_id = blueprint.get("process_id", "")
    organism_name = blueprint.get("organism_name", "")
    agent_type = blueprint.get("agent_type", "")
    domain = blueprint.get("domain", "")
    systems = blueprint.get("systems", [])
    learning_hooks = blueprint.get("learning_hooks", {})
    dependencies = blueprint.get("dependencies", {})

    return f'''"""
Generated Swarm Organism Runtime
Organism: {organism_name}
Process: {process_id}
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class {class_name}:
    def __init__(self, mode: str = "dry-run", event_stream: str = "swarm_events.jsonl"):
        self.mode = mode
        self.process_id = {process_id!r}
        self.organism_name = {organism_name!r}
        self.agent_type = {agent_type!r}
        self.domain = {domain!r}
        self.systems = {systems!r}
        self.learning_hooks = {json.dumps(learning_hooks, indent=8, ensure_ascii=False)}
        self.dependencies = {json.dumps(dependencies, indent=8, ensure_ascii=False)}
        self.event_stream = Path(event_stream)
        self.confidence_threshold = 0.85

    def emit_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {{
            "timestamp": _now(),
            "source": self.organism_name,
            "agent_type": self.agent_type,
            "process_id": self.process_id,
            "event_type": event_type,
            "payload": payload,
            "mode": self.mode,
        }}
        self.event_stream.parent.mkdir(parents=True, exist_ok=True)
        with open(self.event_stream, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\\n")
        return event

    async def execute(self, shared_context: dict[str, Any]) -> dict[str, Any]:
        self.emit_event("organism_started", {{"shared_context_keys": list(shared_context.keys())}})

        confidence = float(shared_context.get("confidence_score", 0.88))
        requires_escalation = confidence < self.confidence_threshold

        result = {{
            "status": "completed" if not requires_escalation else "escalation_required",
            "organism": self.organism_name,
            "agent_type": self.agent_type,
            "process_id": self.process_id,
            "confidence": confidence,
            "requires_escalation": requires_escalation,
            "outputs": {{
                "recommendation": f"Draft recommendation generated by {{self.organism_name}}",
                "risk_score": float(shared_context.get("risk_score", 0.20)),
            }},
            "timestamp": _now(),
        }}

        self.emit_event("organism_completed", result)
        self.emit_event("learning_event", {{
            "pattern": "organism_execution",
            "confidence": confidence,
            "requires_escalation": requires_escalation,
        }})
        return result


async def _run_cli():
    parser = argparse.ArgumentParser(description="Generated Swarm Organism Runtime")
    parser.add_argument("--mode", default="dry-run", choices=["dry-run", "qa", "live"])
    parser.add_argument("--context", default="", help="JSON shared context")
    args = parser.parse_args()

    context = json.loads(args.context) if args.context else {{
        "scenario_id": "DRY-SCENARIO-001",
        "confidence_score": 0.88,
        "risk_score": 0.20,
    }}

    agent = {class_name}(mode=args.mode)
    result = await agent.execute(context)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(_run_cli())
'''


def generate_coordinator_runtime(config: dict[str, Any]) -> str:
    return '''"""
Generated Swarm Coordinator Runtime
Coordinates organism events, conflicts, Shield escalation and learning events.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SwarmCoordinator:
    def __init__(self, config_path: str = "coordinator_config.json", mode: str = "dry-run"):
        self.mode = mode
        self.config_path = Path(config_path)
        self.config = json.loads(self.config_path.read_text(encoding="utf-8")) if self.config_path.exists() else {}
        self.event_stream = Path("swarm_events.jsonl")
        self.audit_stream = Path("swarm_audit_trail.jsonl")
        self.learning_stream = Path("swarm_learning_events.jsonl")
        self.state = "WAITING"

    def emit(self, stream: Path, event: dict[str, Any]) -> dict[str, Any]:
        event["timestamp"] = event.get("timestamp") or _now()
        event["mode"] = self.mode
        stream.parent.mkdir(parents=True, exist_ok=True)
        with open(stream, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\\n")
        return event

    def emit_swarm_event(self, event_type: str, payload: dict[str, Any]):
        return self.emit(self.event_stream, {{
            "event_type": event_type,
            "source": "SwarmCoordinator",
            "payload": payload,
        }})

    def emit_audit_event(self, event_type: str, payload: dict[str, Any]):
        return self.emit(self.audit_stream, {{
            "event_type": event_type,
            "source": "SwarmCoordinator",
            "payload": payload,
        }})

    def emit_learning_event(self, event_type: str, payload: dict[str, Any]):
        return self.emit(self.learning_stream, {{
            "event_type": event_type,
            "source": "SwarmCoordinator",
            "payload": payload,
        }})

    def validate_shared_context(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        required = self.config.get("shared_context_schema", {}).get("required_keys", [])
        missing = [k for k in required if k not in context]
        return len(missing) == 0, missing

    def detect_conflict(self, organism_results: list[dict[str, Any]]) -> dict[str, Any]:
        escalations = [r for r in organism_results if r.get("requires_escalation")]
        if escalations:
            return {{
                "conflict": True,
                "type": "escalation_required",
                "involved": [r.get("organism") for r in escalations],
                "recommended_route": "Constraint Resolution Organism",
            }}
        return {{"conflict": False}}

    async def run(self, shared_context: dict[str, Any]) -> dict[str, Any]:
        self.state = "RUNNING"
        self.emit_swarm_event("swarm_started", {{"shared_context": shared_context}})

        valid, missing = self.validate_shared_context(shared_context)
        if not valid:
            self.state = "BLOCKED"
            event = {{"missing_context": missing, "status": "blocked"}}
            self.emit_audit_event("missing_context", event)
            self.emit_learning_event("missing_context_detected", event)
            return event

        # Dry-run coordinator does not call organism runtimes yet.
        # It validates topology and simulates a coordinated execution.
        organisms = self.config.get("organisms", [])
        results = []
        for org in organisms:
            result = {{
                "organism": org.get("organism_name"),
                "agent_type": org.get("agent_type"),
                "status": "simulated_completed",
                "confidence": shared_context.get("confidence_score", 0.88),
                "requires_escalation": False,
            }}
            results.append(result)
            self.emit_swarm_event("organism_simulated_completed", result)

        conflict = self.detect_conflict(results)
        if conflict.get("conflict"):
            self.state = "ESCALATED"
            self.emit_swarm_event("conflict_detected", conflict)
            self.emit_learning_event("organism_conflict_detected", conflict)
        else:
            self.state = "COMPLETED"

        final = {{
            "status": self.state,
            "organisms_executed": len(results),
            "conflict": conflict,
            "timestamp": _now(),
        }}
        self.emit_swarm_event("swarm_completed", final)
        self.emit_learning_event("swarm_completed", final)
        return final


async def _run_cli():
    parser = argparse.ArgumentParser(description="Generated Swarm Coordinator Runtime")
    parser.add_argument("--mode", default="dry-run", choices=["dry-run", "qa", "live"])
    parser.add_argument("--config", default="coordinator_config.json")
    parser.add_argument("--context", default="")
    args = parser.parse_args()

    context = json.loads(args.context) if args.context else {
        "scenario_id": "DRY-SCENARIO-001",
        "planning_horizon": "monthly",
        "forecast_version": "v1",
        "confidence_score": 0.88,
        "risk_score": 0.20,
        "decision_owner": "process_owner"
    }

    coordinator = SwarmCoordinator(config_path=args.config, mode=args.mode)
    result = await coordinator.run(context)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(_run_cli())
'''


def generate_swarm(package_dir: str | Path) -> SwarmRuntimeManifest:
    ctx = load_context(package_dir)
    package_dir = ctx["package_dir"]

    out_root = package_dir / "13_swarm_runtime"
    organisms_out = out_root / "organisms"
    coordinator_out = out_root / "coordinator"

    organisms_out.mkdir(parents=True, exist_ok=True)
    coordinator_out.mkdir(parents=True, exist_ok=True)

    manifest = ctx["swarm_manifest"]
    organisms = manifest.get("organisms", [])

    generated: list[GeneratedOrganism] = []

    for org in organisms:
        org_folder = Path(org.get("folder", ""))
        siop = read_json(org_folder / "siop_internal.json")
        seed = read_json(org_folder / "organism_blueprint_seed.json")

        folder_name = organism_slug(org.get("organism_name") or org.get("agent_type")).upper()
        runtime_folder = organisms_out / folder_name
        runtime_folder.mkdir(parents=True, exist_ok=True)

        blueprint = build_organism_blueprint(org, siop, seed)
        class_name = blueprint.get(
            "agent_class_name", _pascal(org.get("agent_type", ""))
        )

        blueprint_path = write_json(
            runtime_folder / "architect_blueprint.json", blueprint
        )
        config_path = write_json(
            runtime_folder / "organism_config.json",
            {
                "organism": org,
                "blueprint": blueprint,
                "mode": "dry-run",
                "ready": True,
            },
        )
        runtime_path = write_text(
            runtime_folder / "agent_runtime.py",
            generate_organism_runtime(class_name, blueprint),
        )

        generated.append(
            GeneratedOrganism(
                organism_id=org.get("organism_id", ""),
                organism_name=org.get("organism_name", ""),
                agent_type=org.get("agent_type", ""),
                folder=str(runtime_folder),
                blueprint_path=str(blueprint_path),
                runtime_path=str(runtime_path),
                config_path=str(config_path),
                ready=True,
            )
        )

    coordinator_config = {
        "swarm_id": manifest.get("swarm_id", ""),
        "parent_process": manifest.get("parent_process", ""),
        "organisms": organisms,
        "topology_runtime": ctx["topology_runtime"],
        "event_catalog": ctx["event_catalog"].get("events", []),
        "escalation_routes": ctx["escalation_routes"].get("routes", []),
        "shared_context_schema": ctx["shared_context"],
        "coordinator_seed": ctx["coordinator_seed"],
        "runtime_contract": ctx["coordinator_runtime_contract"],
        "shield_contract": ctx["coordinator_shield_contract"],
        "learning_contract": ctx["coordinator_learning_contract"],
    }

    coordinator_config_path = write_json(
        coordinator_out / "coordinator_config.json", coordinator_config
    )
    coordinator_runtime_path = write_text(
        coordinator_out / "swarm_coordinator_runtime.py",
        generate_coordinator_runtime(coordinator_config),
    )

    runtime_manifest_path = out_root / "swarm_runtime_manifest.json"

    result = SwarmRuntimeManifest(
        swarm_runtime_id=f"SWARM-RUNTIME-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        package_dir=str(package_dir),
        swarm_id=manifest.get("swarm_id", ""),
        parent_process=manifest.get("parent_process", ""),
        organisms_generated=len(generated),
        coordinator_generated=coordinator_runtime_path.exists(),
        ready=bool(generated) and coordinator_runtime_path.exists(),
        organisms=generated,
        outputs={
            "swarm_runtime_manifest": str(runtime_manifest_path),
            "coordinator_runtime": str(coordinator_runtime_path),
            "coordinator_config": str(coordinator_config_path),
            "organisms_runtime_dir": str(organisms_out),
        },
        next_step="Run swarm dry-run coordinator, then integrate agent_developer_multi.",
    )

    write_json(runtime_manifest_path, asdict(result))
    return result


def run_cli(package_dir: str):
    result = generate_swarm(package_dir)

    print("\nSwarm Generator complete")
    print(f"Swarm ID:             {result.swarm_id}")
    print(f"Process:              {result.parent_process}")
    print(f"Organisms generated:  {result.organisms_generated}")
    print(f"Coordinator:          {result.coordinator_generated}")
    print(f"Ready:                {result.ready}")

    print("\nOrganisms:")
    for org in result.organisms:
        print(f"  - {org.organism_name}: {org.folder}")

    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")

    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Swarm Generator")
    parser.add_argument(
        "--package-dir", required=True, help="Customer package directory"
    )
    args = parser.parse_args()
    run_cli(args.package_dir)
