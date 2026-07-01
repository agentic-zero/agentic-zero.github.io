"""
AGENTIC ZERO - PIONEER TEAM
Swarm Topology Builder v1.0

Role:
  Build the runtime topology for a multi-organism swarm.

Input:
  10_swarm/swarm_manifest.json
  10_swarm/coordination/swarm_coordination_siop.json
  10_swarm/coordination/swarm_topology.json

Output:
  10_swarm/runtime/
    swarm_topology_runtime.json
    event_catalog.json
    escalation_routes.json
    shared_context_schema.json
    topology_readiness.json

Recommended path:
  pioneer_team/swarm/swarm_topology_builder.py

This module does NOT generate agents.
It defines how organisms communicate, escalate and coordinate.
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
class RuntimeNode:
    node_id: str
    organism_name: str
    agent_type: str
    domain: str
    runtime_status: str
    systems: list[str]
    frameworks: list[str]
    input_events: list[str]
    output_events: list[str]
    dependencies: dict[str, list[str]]


@dataclass
class RuntimeEdge:
    edge_id: str
    source_node: str
    target_node: str
    event_name: str
    event_type: str
    required_context: list[str]
    shield_validation_required: bool
    escalation_on_failure: bool


@dataclass
class EventDefinition:
    event_name: str
    source: str
    targets: list[str]
    payload_schema: dict[str, Any]
    required_context: list[str]
    audit_required: bool = True
    learning_required: bool = True
    shield_required: bool = True


@dataclass
class EscalationRoute:
    route_id: str
    trigger: str
    source: str
    first_level: str
    second_level: str
    final_level: str
    human_required: bool
    notes: str


@dataclass
class SwarmTopologyRuntime:
    topology_runtime_id: str
    created_at: str
    package_dir: str
    parent_process: str
    swarm_id: str
    nodes_count: int
    edges_count: int
    event_count: int
    nodes: list[RuntimeNode]
    edges: list[RuntimeEdge]
    readiness: dict[str, Any]
    outputs: dict[str, str]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "item").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "item"


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


def load_swarm(package_dir: str | Path) -> dict[str, Any]:
    package_dir = Path(package_dir)

    manifest_path = package_dir / "10_swarm" / "swarm_manifest.json"
    coordination_path = (
        package_dir / "10_swarm" / "coordination" / "swarm_coordination_siop.json"
    )
    topology_path = package_dir / "10_swarm" / "coordination" / "swarm_topology.json"

    manifest = read_json(manifest_path)
    coordination = read_json(coordination_path)
    topology = read_json(topology_path)

    if not manifest:
        raise FileNotFoundError(f"Missing swarm manifest: {manifest_path}")

    return {
        "package_dir": package_dir,
        "manifest_path": manifest_path,
        "coordination_path": coordination_path,
        "topology_path": topology_path,
        "manifest": manifest,
        "coordination": coordination,
        "topology": topology,
    }


def event_from_organism_name(name: str) -> str:
    return f"{_slug(name)}_updated"


def build_nodes(payload: dict[str, Any]) -> list[RuntimeNode]:
    manifest = payload["manifest"]
    topology = payload["topology"]

    topo_nodes = {n.get("id"): n for n in topology.get("nodes", [])}
    organisms = manifest.get("organisms", [])

    nodes: list[RuntimeNode] = []

    for org in organisms:
        node_id = org.get("organism_id", "")
        topo = topo_nodes.get(node_id, {})

        upstream = org.get("upstream_dependencies", [])
        downstream = org.get("downstream_dependencies", [])

        input_events = [f"{_slug(dep)}_updated" for dep in upstream]
        output_events = [event_from_organism_name(org.get("organism_name", ""))]

        nodes.append(
            RuntimeNode(
                node_id=node_id,
                organism_name=org.get("organism_name", ""),
                agent_type=org.get("agent_type", ""),
                domain=org.get("domain", topo.get("domain", "")),
                runtime_status="WAITING",
                systems=org.get("systems", topo.get("systems", [])),
                frameworks=org.get("frameworks", []),
                input_events=input_events,
                output_events=output_events,
                dependencies={
                    "upstream": upstream,
                    "downstream": downstream,
                },
            )
        )

    return nodes


def build_edges(payload: dict[str, Any], nodes: list[RuntimeNode]) -> list[RuntimeEdge]:
    topology = payload["topology"]
    coordination = payload["coordination"]

    shared_context = coordination.get("shared_context", [])
    topo_edges = topology.get("edges", [])

    node_ids = {n.node_id for n in nodes}
    edges: list[RuntimeEdge] = []

    for idx, edge in enumerate(topo_edges, start=1):
        src = edge.get("from", "")
        dst = edge.get("to", "")

        if src not in node_ids or dst not in node_ids:
            continue

        event_name = edge.get("event") or f"{_slug(src)}_updated"

        edges.append(
            RuntimeEdge(
                edge_id=f"EDGE-{idx:03d}",
                source_node=src,
                target_node=dst,
                event_name=event_name,
                event_type="swarm_event",
                required_context=shared_context,
                shield_validation_required=True,
                escalation_on_failure=True,
            )
        )

    return edges


def build_event_catalog(
    nodes: list[RuntimeNode], edges: list[RuntimeEdge]
) -> list[EventDefinition]:
    """DEPRECATED - kept for reference only, no longer called.

    runtime_core/event_catalog.py (Claude) is now the single producer of
    event_catalog.json. This function and EventDefinition exist only so
    this diff stays minimal; they are intentionally unused dead code, not
    an oversight. See build_topology_runtime() and
    SWARM_ARCHITECTURE_v1.md section 3.
    """
    targets_by_event: dict[str, list[str]] = {}
    source_by_event: dict[str, str] = {}

    for edge in edges:
        targets_by_event.setdefault(edge.event_name, [])
        if edge.target_node not in targets_by_event[edge.event_name]:
            targets_by_event[edge.event_name].append(edge.target_node)
        source_by_event[edge.event_name] = edge.source_node

    events: list[EventDefinition] = []

    for event_name, targets in targets_by_event.items():
        source = source_by_event.get(event_name, "")
        events.append(
            EventDefinition(
                event_name=event_name,
                source=source,
                targets=targets,
                required_context=[
                    "scenario_id",
                    "confidence_score",
                    "timestamp",
                    "source_organism",
                    "decision_id",
                ],
                payload_schema={
                    "event_name": "string",
                    "scenario_id": "string",
                    "source_organism": "string",
                    "payload": "object",
                    "confidence_score": "number",
                    "risk_score": "number",
                    "requires_escalation": "boolean",
                    "timestamp": "iso_datetime",
                },
            )
        )

    # Ensure each organism has a completion event even if no downstream edge exists.
    for node in nodes:
        event_name = event_from_organism_name(node.organism_name)
        if event_name not in targets_by_event:
            events.append(
                EventDefinition(
                    event_name=event_name,
                    source=node.node_id,
                    targets=[],
                    required_context=[
                        "scenario_id",
                        "confidence_score",
                        "timestamp",
                        "source_organism",
                    ],
                    payload_schema={
                        "event_name": "string",
                        "scenario_id": "string",
                        "source_organism": "string",
                        "payload": "object",
                        "confidence_score": "number",
                        "timestamp": "iso_datetime",
                    },
                )
            )

    events.append(
        EventDefinition(
            event_name="conflict_detected",
            source="swarm_coordinator",
            targets=["constraint_resolution_agent"],
            required_context=[
                "scenario_id",
                "conflict_type",
                "involved_organisms",
                "confidence_delta",
                "financial_impact",
            ],
            payload_schema={
                "conflict_type": "string",
                "involved_organisms": "array",
                "confidence_delta": "number",
                "financial_impact": "number",
                "recommended_route": "string",
            },
        )
    )

    return events


def build_escalation_routes(
    nodes: list[RuntimeNode], edges: list[RuntimeEdge]
) -> list[EscalationRoute]:
    routes: list[EscalationRoute] = []

    for node in nodes:
        routes.append(
            EscalationRoute(
                route_id=f"ESC-{_slug(node.organism_name).upper()}",
                trigger="low_confidence_or_policy_boundary",
                source=node.organism_name,
                first_level="Swarm Coordinator",
                second_level="Agentic Shield",
                final_level="Human Process Owner",
                human_required=True,
                notes="Any low-confidence decision or action outside autonomy boundaries must escalate.",
            )
        )

    routes.append(
        EscalationRoute(
            route_id="ESC-CONFLICT-RESOLUTION",
            trigger="organism_conflict",
            source="Swarm Coordinator",
            first_level="Constraint Resolution Organism",
            second_level="Agentic Shield",
            final_level="Human Executive Owner",
            human_required=True,
            notes="Conflicting recommendations across organisms are routed through Constraint Resolution.",
        )
    )

    routes.append(
        EscalationRoute(
            route_id="ESC-FINANCIAL-IMPACT",
            trigger="financial_or_cash_impact_above_threshold",
            source="Finance Reconciliation Organism",
            first_level="Swarm Coordinator",
            second_level="Agentic Shield",
            final_level="Finance Owner",
            human_required=True,
            notes="Financial threshold changes and budget impacts require approval.",
        )
    )

    return routes


def build_shared_context_schema(coordination: dict[str, Any]) -> dict[str, Any]:
    keys = coordination.get("shared_context", [])

    schema = {
        "schema_id": f"SHARED-CONTEXT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "created_at": _now(),
        "required_keys": keys,
        "fields": {},
    }

    default_types = {
        "scenario_id": "string",
        "planning_horizon": "string",
        "forecast_version": "string",
        "constraint_id": "string",
        "financial_impact": "number",
        "service_impact": "number",
        "confidence_score": "number",
        "risk_score": "number",
        "decision_owner": "string",
    }

    for key in keys:
        schema["fields"][key] = {
            "type": default_types.get(key, "string"),
            "required": True,
            "description": f"Shared swarm context field: {key}",
        }

    return schema


def build_readiness(
    nodes: list[RuntimeNode], edges: list[RuntimeEdge], events_count: int
) -> dict[str, Any]:
    issues = []

    if len(nodes) < 2:
        issues.append("Swarm must contain at least two organisms.")
    if len(edges) < 1:
        issues.append("Swarm topology must contain at least one edge.")
    if events_count < 1:
        issues.append("Event catalog is empty.")

    has_constraint = any("constraint" in n.agent_type for n in nodes)
    if not has_constraint:
        issues.append(
            "Constraint Resolution organism is recommended for swarm arbitration."
        )

    has_finance = any("finance" in n.agent_type for n in nodes)
    if not has_finance:
        issues.append("Finance organism is recommended for planning/IBP swarms.")

    return {
        "ready_for_swarm_generator": len(issues) == 0,
        "issues": issues,
        "nodes_count": len(nodes),
        "edges_count": len(edges),
        "events_count": events_count,
        "requires_swarm_coordinator": True,
        "requires_event_bus": True,
        "requires_shield_arbitration": True,
        "requires_the_machine_observation": True,
    }


def build_topology_runtime(package_dir: str | Path) -> SwarmTopologyRuntime:
    payload = load_swarm(package_dir)
    package_dir = payload["package_dir"]
    manifest = payload["manifest"]
    coordination = payload["coordination"]

    runtime_dir = package_dir / "10_swarm" / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    nodes = build_nodes(payload)
    edges = build_edges(payload, nodes)
    # event_catalog.json is no longer built here. runtime_core/event_catalog.py
    # (Claude) is the single producer of that artifact, already validated
    # end-to-end and consumed by event_router.py/policy_engine.py/
    # compliance_engine.py/observer.py. This module used to generate its own
    # competing event_catalog.json at the same path with a different schema
    # (source/payload_schema/required_context vs category/origin/
    # shield_required) - silently overwriting whichever one ran second.
    # See SWARM_ARCHITECTURE_v1.md section 3 for the agreed resolution.
    escalations = build_escalation_routes(nodes, edges)
    shared_context = build_shared_context_schema(coordination)

    topology_runtime_path = runtime_dir / "swarm_topology_runtime.json"
    event_catalog_path = runtime_dir / "event_catalog.json"
    escalation_routes_path = runtime_dir / "escalation_routes.json"
    shared_context_path = runtime_dir / "shared_context_schema.json"
    readiness_path = runtime_dir / "topology_readiness.json"

    # Delegate to the single producer instead of regenerating independently.
    from runtime_core.event_catalog import EventCatalog

    event_catalog_result = EventCatalog(
        runtime_config_dir=runtime_dir,
        coordination_file=payload["coordination_path"],
    ).run()
    events_count = len(event_catalog_result["catalog"].get("events", []))

    readiness = build_readiness(nodes, edges, events_count)

    result = SwarmTopologyRuntime(
        topology_runtime_id=f"SWARM-RUNTIME-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        package_dir=str(package_dir),
        parent_process=manifest.get("parent_process", ""),
        swarm_id=manifest.get("swarm_id", ""),
        nodes_count=len(nodes),
        edges_count=len(edges),
        event_count=events_count,
        nodes=nodes,
        edges=edges,
        readiness=readiness,
        outputs={
            "swarm_topology_runtime": str(topology_runtime_path),
            "event_catalog": str(event_catalog_path),
            "escalation_routes": str(escalation_routes_path),
            "shared_context_schema": str(shared_context_path),
            "topology_readiness": str(readiness_path),
        },
        next_step="Run organism_memory_seed_builder.py",
    )

    write_json(topology_runtime_path, asdict(result))
    # event_catalog.json already written by EventCatalog.run() above - this
    # module does not write it.
    write_json(escalation_routes_path, {"routes": [asdict(r) for r in escalations]})
    write_json(shared_context_path, shared_context)
    write_json(readiness_path, readiness)

    return result


def run_cli(package_dir: str):
    result = build_topology_runtime(package_dir)

    print("\nSwarm Topology Builder complete")
    print(f"Swarm ID: {result.swarm_id}")
    print(f"Process:  {result.parent_process}")
    print(f"Nodes:    {result.nodes_count}")
    print(f"Edges:    {result.edges_count}")
    print(f"Events:   {result.event_count}")
    print(f"Ready:    {result.readiness.get('ready_for_swarm_generator')}")

    if result.readiness.get("issues"):
        print("\nReadiness issues:")
        for issue in result.readiness["issues"]:
            print(f"  - {issue}")

    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")

    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agentic Zero - Swarm Topology Builder"
    )
    parser.add_argument(
        "--package-dir", required=True, help="Customer package directory"
    )
    args = parser.parse_args()

    run_cli(args.package_dir)
