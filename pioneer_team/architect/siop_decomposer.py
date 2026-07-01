"""
AGENTIC ZERO - PIONEER TEAM
SIOP Decomposer v1.0

Role:
  Decompose an interconnected Level 1 SIOP into Level 2 SIOPs ready for swarm generation.

Input:
  00_enterprise_intent/system_detection.json
  02_siop/siop_internal.json

Output:
  00_enterprise_intent/siop_decomposition.json
  00_enterprise_intent/swarm_coordination_siop.json
  00_enterprise_intent/level_2_siops/{siop_id}.json

Recommended path:
  pioneer_team/architect/siop_decomposer.py
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
class Level2SIOP:
    siop_id: str
    parent_process: str
    name: str
    organism: str
    agent_type: str
    domain: str
    purpose: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    systems: list[str] = field(default_factory=list)
    scor_level_1_2: list[str] = field(default_factory=list)
    scor_level_3: list[str] = field(default_factory=list)
    bpmn_processes: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    upstream_dependencies: list[str] = field(default_factory=list)
    downstream_dependencies: list[str] = field(default_factory=list)
    autonomy_design: dict[str, Any] = field(default_factory=dict)
    acceptance_criteria: list[str] = field(default_factory=list)
    learning_hooks: dict[str, Any] = field(default_factory=dict)


@dataclass
class SIOPDecompositionResult:
    decomposition_id: str
    created_at: str
    package_dir: str
    parent_process: str
    route: str
    level_2_count: int
    coordination_required: bool
    level_2_siops: list[Level2SIOP]
    outputs: dict[str, str]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "process").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "process"


def _upper_slug(value: str) -> str:
    return _slug(value).upper().replace("_", "-")


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


PROCESS_TEMPLATES = {
    "demand_planning": {
        "name": "Demand Planning",
        "organism": "Demand Planning Organism",
        "agent_type": "demand_planning_agent",
        "domain": "planning",
        "purpose": "Generate, validate and monitor demand plans, forecast deviations and demand risks.",
        "inputs": [
            "historical sales",
            "customer orders",
            "forecast baseline",
            "promotions",
            "market signals",
        ],
        "outputs": [
            "demand plan",
            "forecast confidence",
            "demand deviation alert",
            "scenario demand signal",
        ],
        "systems": ["SAP IBP", "ERP", "CRM", "Excel/CSV"],
        "autonomous_actions": [
            "validate demand data",
            "detect deviations",
            "draft forecast scenarios",
        ],
        "approval_required": [
            "publish consensus demand plan",
            "change forecast policy",
        ],
        "always_human": ["strategic market assumption change"],
    },
    "supply_planning": {
        "name": "Supply Planning",
        "organism": "Supply Planning Organism",
        "agent_type": "supply_planning_agent",
        "domain": "supply",
        "purpose": "Translate demand into supply plans, procurement needs, production constraints and supplier risk signals.",
        "inputs": [
            "demand plan",
            "purchase orders",
            "supplier capacity",
            "lead times",
            "production plan",
        ],
        "outputs": [
            "supply plan",
            "supplier risk",
            "supply constraint",
            "available-to-plan signal",
        ],
        "systems": ["ERP", "SAP IBP", "SAP Ariba", "MRP"],
        "autonomous_actions": [
            "detect supplier constraints",
            "draft supply scenarios",
            "validate lead time risk",
        ],
        "approval_required": ["supplier commitment change", "expedite proposal"],
        "always_human": ["strategic supplier switch"],
    },
    "inventory_planning": {
        "name": "Inventory Planning",
        "organism": "Inventory Planning Organism",
        "agent_type": "inventory_planning_agent",
        "domain": "planning",
        "purpose": "Evaluate stock, coverage, shortages, excess, replenishment and inventory risk.",
        "inputs": [
            "stock on hand",
            "safety stock",
            "open orders",
            "forecast",
            "service policy",
        ],
        "outputs": [
            "inventory plan",
            "coverage alert",
            "shortage risk",
            "excess risk",
            "replenishment proposal",
        ],
        "systems": ["ERP", "WMS", "SAP IBP"],
        "autonomous_actions": [
            "calculate coverage",
            "detect shortage/excess",
            "draft replenishment proposal",
        ],
        "approval_required": ["change safety stock", "change service policy"],
        "always_human": ["inventory policy redesign"],
    },
    "capacity_planning": {
        "name": "Capacity Planning",
        "organism": "Capacity Planning Organism",
        "agent_type": "capacity_planning_agent",
        "domain": "operations",
        "purpose": "Assess production, warehouse, transport, labor and resource capacity constraints.",
        "inputs": [
            "supply plan",
            "production calendar",
            "resource capacity",
            "warehouse capacity",
            "transport capacity",
        ],
        "outputs": [
            "capacity plan",
            "utilization signal",
            "capacity constraint",
            "overflow recommendation",
        ],
        "systems": ["ERP", "MES", "WMS", "TMS"],
        "autonomous_actions": [
            "detect overload",
            "draft capacity alternatives",
            "validate available capacity",
        ],
        "approval_required": ["overtime proposal", "capacity allocation change"],
        "always_human": ["structural capacity investment"],
    },
    "finance_reconciliation": {
        "name": "Finance Reconciliation",
        "organism": "Finance Reconciliation Organism",
        "agent_type": "finance_reconciliation_agent",
        "domain": "finance",
        "purpose": "Translate operational plans into margin, cash, working capital and budget impact.",
        "inputs": [
            "demand plan",
            "supply plan",
            "inventory plan",
            "cost assumptions",
            "budget",
        ],
        "outputs": [
            "financial reconciliation",
            "margin impact",
            "cash impact",
            "working capital alert",
        ],
        "systems": ["ERP FI-CO", "EPM", "Excel/CSV"],
        "autonomous_actions": [
            "calculate margin impact",
            "detect cash risk",
            "draft finance reconciliation",
        ],
        "approval_required": [
            "budget deviation acceptance",
            "working capital policy exception",
        ],
        "always_human": ["financial target reset"],
    },
    "constraint_resolution": {
        "name": "Constraint Resolution",
        "organism": "Constraint Resolution Organism",
        "agent_type": "constraint_resolution_agent",
        "domain": "orchestration",
        "purpose": "Resolve conflicts between demand, supply, inventory, capacity, finance, risk and execution constraints.",
        "inputs": [
            "demand plan",
            "supply plan",
            "inventory plan",
            "capacity plan",
            "financial impact",
            "risk signal",
        ],
        "outputs": [
            "resolved plan",
            "trade-off decision",
            "escalation recommendation",
            "approved scenario candidate",
        ],
        "systems": ["Agentic Shield", "Collaboration workflow", "ERP"],
        "autonomous_actions": [
            "classify conflict",
            "rank scenarios",
            "draft resolution recommendation",
        ],
        "approval_required": ["final trade-off decision", "service vs cash conflict"],
        "always_human": ["strategic trade-off"],
    },
    "control_tower_monitoring": {
        "name": "Control Tower Monitoring",
        "organism": "Control Tower Organism",
        "agent_type": "control_tower_agent",
        "domain": "operations",
        "purpose": "Monitor end-to-end execution, KPIs, alerts, exceptions and operational health.",
        "inputs": [
            "orders",
            "shipments",
            "inventory",
            "execution events",
            "KPI signals",
        ],
        "outputs": [
            "enterprise pulse",
            "exception alert",
            "priority queue",
            "decision route",
        ],
        "systems": ["Control Tower", "ERP", "TMS", "WMS", "BI"],
        "autonomous_actions": [
            "classify alerts",
            "route exceptions",
            "update dashboard",
        ],
        "approval_required": ["critical route override"],
        "always_human": ["customer commitment outside policy"],
    },
    "risk_monitoring": {
        "name": "Risk Monitoring",
        "organism": "Risk Monitoring Organism",
        "agent_type": "risk_monitoring_agent",
        "domain": "risk",
        "purpose": "Detect, classify and prioritize supplier, demand, execution, cash, compliance and operational risks.",
        "inputs": [
            "exceptions",
            "supplier alerts",
            "service deviations",
            "compliance signals",
            "external risk feeds",
        ],
        "outputs": ["risk score", "risk classification", "mitigation recommendation"],
        "systems": ["GRC", "Control Tower", "ERP", "External feeds"],
        "autonomous_actions": [
            "classify risk",
            "draft mitigation",
            "escalate high risk",
        ],
        "approval_required": ["risk acceptance", "mitigation cost approval"],
        "always_human": ["strategic risk decision"],
    },
    "digital_twin_simulation": {
        "name": "Digital Twin Simulation",
        "organism": "Digital Twin Organism",
        "agent_type": "digital_twin_agent",
        "domain": "simulation",
        "purpose": "Simulate scenarios, constraints and business impact before operational execution.",
        "inputs": [
            "network model",
            "scenario parameters",
            "constraints",
            "historical performance",
        ],
        "outputs": ["simulation result", "impact assessment", "recommended scenario"],
        "systems": ["Digital Twin", "Simulation Engine", "ERP", "BI"],
        "autonomous_actions": [
            "run low-risk simulation",
            "compare scenarios",
            "draft scenario ranking",
        ],
        "approval_required": ["execute scenario recommendation"],
        "always_human": ["network redesign decision"],
    },
    "quality_management": {
        "name": "Quality Management",
        "organism": "Quality Management Organism",
        "agent_type": "quality_management_agent",
        "domain": "quality",
        "purpose": "Monitor non-conformance, deviation, CAPA, 8D and quality risk events.",
        "inputs": [
            "quality events",
            "inspection results",
            "deviations",
            "CAPA records",
        ],
        "outputs": ["quality alert", "root cause candidate", "CAPA recommendation"],
        "systems": ["QMS", "ERP QM", "MES"],
        "autonomous_actions": [
            "classify deviation",
            "draft CAPA",
            "monitor effectiveness",
        ],
        "approval_required": ["CAPA closure", "quality release"],
        "always_human": ["regulated quality decision"],
    },
    "source_execution": {
        "name": "Source Execution",
        "organism": "Source Execution Organism",
        "agent_type": "source_execution_agent",
        "domain": "procurement",
        "purpose": "Manage sourcing execution, supplier commitments, purchase orders and source risks.",
        "inputs": [
            "purchase requisitions",
            "supplier confirmations",
            "contracts",
            "lead times",
        ],
        "outputs": ["source plan", "supplier confirmation", "procurement exception"],
        "systems": ["ERP MM", "SAP Ariba", "SRM"],
        "autonomous_actions": [
            "validate PO status",
            "detect supplier delay",
            "draft supplier follow-up",
        ],
        "approval_required": ["supplier change", "price deviation"],
        "always_human": ["strategic sourcing decision"],
    },
    "make_execution": {
        "name": "Make Execution",
        "organism": "Make Execution Organism",
        "agent_type": "make_execution_agent",
        "domain": "manufacturing",
        "purpose": "Coordinate production execution, work orders, materials, shop floor and feedback to planning.",
        "inputs": [
            "production orders",
            "materials",
            "shop floor status",
            "quality checks",
        ],
        "outputs": ["production status", "material issue alert", "execution deviation"],
        "systems": ["ERP PP", "MES", "QMS"],
        "autonomous_actions": [
            "monitor work order",
            "detect deviation",
            "draft reschedule signal",
        ],
        "approval_required": ["sequence change", "material substitution"],
        "always_human": ["regulated production release"],
    },
    "deliver_execution": {
        "name": "Deliver Execution",
        "organism": "Deliver Execution Organism",
        "agent_type": "deliver_execution_agent",
        "domain": "logistics",
        "purpose": "Coordinate delivery execution, order fulfillment, shipment, carrier and customer delivery status.",
        "inputs": [
            "sales orders",
            "shipment plans",
            "carrier status",
            "warehouse status",
        ],
        "outputs": ["delivery status", "shipment exception", "OTIF risk"],
        "systems": ["ERP SD", "TMS", "WMS"],
        "autonomous_actions": [
            "detect OTIF risk",
            "route exception",
            "draft confirmation",
        ],
        "approval_required": ["carrier change", "expedite cost"],
        "always_human": ["customer promise outside policy"],
    },
}


def infer_parent_process(siop: dict[str, Any], detection: dict[str, Any]) -> str:
    candidates = [
        siop.get("process_name"),
        siop.get("level_1_process"),
        siop.get("executive_summary", {}).get("process_name"),
        siop.get("business_context", {}).get("process_name"),
        siop.get("process_id"),
        siop.get("siop_id"),
    ]
    for c in candidates:
        if c:
            return str(c)

    systems = detection.get("systems_detected", [])
    if systems:
        return systems[0].get("name", "Interconnected Process")

    return "Interconnected Process"


def unique_processes(detection: dict[str, Any]) -> list[str]:
    processes: list[str] = []
    for system in detection.get("systems_detected", []):
        for p in system.get("default_level2_processes", []):
            if p not in processes:
                processes.append(p)
    return processes


def apply_dependencies(level2: list[Level2SIOP]) -> list[Level2SIOP]:
    by_agent = {x.agent_type: x for x in level2}

    def dep(src: str, dst: str):
        if src in by_agent and dst in by_agent:
            if by_agent[src].siop_id not in by_agent[dst].upstream_dependencies:
                by_agent[dst].upstream_dependencies.append(by_agent[src].siop_id)
            if by_agent[dst].siop_id not in by_agent[src].downstream_dependencies:
                by_agent[src].downstream_dependencies.append(by_agent[dst].siop_id)

    dep("demand_planning_agent", "inventory_planning_agent")
    dep("demand_planning_agent", "supply_planning_agent")
    dep("inventory_planning_agent", "supply_planning_agent")
    dep("supply_planning_agent", "capacity_planning_agent")
    dep("capacity_planning_agent", "finance_reconciliation_agent")
    dep("demand_planning_agent", "finance_reconciliation_agent")
    dep("supply_planning_agent", "finance_reconciliation_agent")
    dep("control_tower_agent", "risk_monitoring_agent")
    dep("digital_twin_agent", "constraint_resolution_agent")
    dep("risk_monitoring_agent", "constraint_resolution_agent")

    for agent in [
        "demand_planning_agent",
        "inventory_planning_agent",
        "supply_planning_agent",
        "capacity_planning_agent",
        "finance_reconciliation_agent",
        "risk_monitoring_agent",
        "control_tower_agent",
        "digital_twin_agent",
        "quality_management_agent",
        "source_execution_agent",
        "make_execution_agent",
        "deliver_execution_agent",
    ]:
        dep(agent, "constraint_resolution_agent")

    return level2


def build_level2_siop(
    process_key: str, parent_process: str, detection: dict[str, Any]
) -> Optional[Level2SIOP]:
    template = PROCESS_TEMPLATES.get(process_key)
    if not template:
        return None

    systems = detection.get("systems_detected", [])
    scor_l12: list[str] = []
    scor_l3: list[str] = []
    bpmn: list[str] = []
    frameworks: list[str] = []

    for s in systems:
        for x in s.get("scor_level_1_2", []):
            if x not in scor_l12:
                scor_l12.append(x)
        for x in s.get("scor_level_3", []):
            if x not in scor_l3:
                scor_l3.append(x)
        for x in s.get("bpmn_processes", []):
            if x not in bpmn:
                bpmn.append(x)
        for x in s.get("frameworks", []):
            if x not in frameworks:
                frameworks.append(x)

    prefix = _upper_slug(parent_process)
    siop_id = f"{prefix}-{_upper_slug(template['name'])}"

    return Level2SIOP(
        siop_id=siop_id,
        parent_process=parent_process,
        name=template["name"],
        organism=template["organism"],
        agent_type=template["agent_type"],
        domain=template["domain"],
        purpose=template["purpose"],
        inputs=template["inputs"],
        outputs=template["outputs"],
        systems=template["systems"],
        scor_level_1_2=scor_l12,
        scor_level_3=scor_l3,
        bpmn_processes=bpmn,
        frameworks=frameworks,
        autonomy_design={
            "autonomous_actions": template.get("autonomous_actions", []),
            "approval_required": template.get("approval_required", []),
            "always_human": template.get("always_human", []),
        },
        acceptance_criteria=[
            "Inputs are validated before action.",
            "Outputs are traceable.",
            "Low-confidence decisions are escalated.",
            "All decisions emit audit and learning events.",
        ],
        learning_hooks={
            "observation_points": [
                f"{template['agent_type']}_started",
                f"{template['agent_type']}_completed",
                f"{template['agent_type']}_exception",
                f"{template['agent_type']}_confidence_drop",
            ],
            "failure_patterns": [
                "missing_input",
                "conflicting_recommendation",
                "low_confidence",
                "late_signal",
            ],
            "kpi_deviation_signals": [
                "service_deviation",
                "cost_deviation",
                "time_deviation",
                "risk_score_increase",
            ],
            "feedback_targets": [
                template["agent_type"],
                "swarm_coordinator",
                "the_machine",
            ],
            "improvement_loop": [
                "observe",
                "store_episode",
                "detect_pattern",
                "recommend_improvement",
                "update_shield_rule_if_validated",
            ],
        },
    )


def build_coordination_siop(
    parent_process: str, level2: list[Level2SIOP]
) -> dict[str, Any]:
    return {
        "coordination_siop_id": f"COORD-{_upper_slug(parent_process)}",
        "created_at": _now(),
        "parent_process": parent_process,
        "purpose": "Coordinate Level 2 organisms so the factory does not generate isolated agents working in a line.",
        "organisms": [asdict(x) for x in level2],
        "coordination_model": {
            "type": "event_driven_swarm",
            "coordinator_required": True,
            "shield_arbitration_required": True,
            "the_machine_observation_required": True,
        },
        "coordination_rules": [
            "Every organism must publish its output as a swarm event.",
            "Every downstream organism must consume validated upstream events.",
            "Conflicting recommendations are routed to Constraint Resolution.",
            "Financial or compliance impact requires Shield validation.",
            "The Machine observes all coordination failures and repeated conflicts.",
        ],
        "shared_context": [
            "scenario_id",
            "planning_horizon",
            "confidence_score",
            "risk_score",
            "financial_impact",
            "service_impact",
            "constraint_id",
            "decision_owner",
        ],
        "event_routes": build_event_routes(level2),
        "shield_arbitration": {
            "autonomous_allowed": [
                "data validation",
                "scenario creation",
                "exception classification",
                "draft recommendation",
                "low-risk notification",
            ],
            "approval_required": [
                "final plan approval",
                "budget impact",
                "policy threshold change",
                "supplier/customer commitment change",
            ],
            "always_human": [
                "strategic trade-off",
                "irreversible operational change",
                "regulated compliance decision",
            ],
        },
        "learning_hooks": {
            "observation_points": [
                "organism_conflict",
                "coordination_delay",
                "missing_context",
                "human_override",
                "final_plan_rework",
            ],
            "failure_patterns": [
                "isolated_agent_decision",
                "broken_dependency",
                "conflicting_recommendation",
                "late_finance_alignment",
                "simulation_mismatch",
            ],
            "kpi_deviation_signals": [
                "forecast_accuracy_drop",
                "inventory_coverage_gap",
                "capacity_overload",
                "margin_deviation",
                "risk_score_increase",
            ],
            "feedback_targets": [
                "swarm_coordinator",
                "shield_arbitrator",
                "enterprise_architect",
                "the_machine",
            ],
            "improvement_loop": [
                "store conflict pattern",
                "recommend coordination rule",
                "update Shield arbitration",
                "update swarm topology if repeated",
            ],
        },
    }


def build_event_routes(level2: list[Level2SIOP]) -> list[dict[str, str]]:
    routes: list[dict[str, str]] = []
    by_id = {x.siop_id: x for x in level2}

    for item in level2:
        for dst_id in item.downstream_dependencies:
            dst = by_id.get(dst_id)
            if not dst:
                continue
            routes.append(
                {
                    "from": item.organism,
                    "to": dst.organism,
                    "event": f"{_slug(item.name)}_updated",
                }
            )

    return routes


def decompose(package_dir: str | Path) -> SIOPDecompositionResult:
    package_dir = Path(package_dir)

    detection_path = package_dir / "00_enterprise_intent" / "system_detection.json"
    siop_path = package_dir / "02_siop" / "siop_internal.json"

    detection = read_json(detection_path)
    siop = read_json(siop_path)

    if not detection:
        raise FileNotFoundError(f"Missing system_detection.json: {detection_path}")

    parent_process = infer_parent_process(siop, detection)
    process_keys = unique_processes(detection)

    level2: list[Level2SIOP] = []
    for key in process_keys:
        l2 = build_level2_siop(key, parent_process, detection)
        if l2:
            level2.append(l2)

    level2 = apply_dependencies(level2)

    out_dir = package_dir / "00_enterprise_intent"
    l2_dir = out_dir / "level_2_siops"
    l2_dir.mkdir(parents=True, exist_ok=True)

    for l2 in level2:
        write_json(l2_dir / f"{l2.siop_id}.json", asdict(l2))

    coordination = build_coordination_siop(parent_process, level2)

    decomposition_path = out_dir / "siop_decomposition.json"
    coordination_path = out_dir / "swarm_coordination_siop.json"

    result = SIOPDecompositionResult(
        decomposition_id=f"DECOMP-{_upper_slug(parent_process)}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        package_dir=str(package_dir),
        parent_process=parent_process,
        route="SWARM",
        level_2_count=len(level2),
        coordination_required=len(level2) >= 2,
        level_2_siops=level2,
        outputs={
            "siop_decomposition": str(decomposition_path),
            "swarm_coordination_siop": str(coordination_path),
            "level_2_siops_dir": str(l2_dir),
        },
        next_step="Run swarm_splitter.py / swarm_generator.py",
    )

    write_json(decomposition_path, asdict(result))
    write_json(coordination_path, coordination)

    return result


def run_cli(package_dir: str):
    result = decompose(package_dir)

    print("\nSIOP Decomposer complete")
    print(f"Parent process: {result.parent_process}")
    print(f"Route:          {result.route}")
    print(f"Level 2 SIOPs:  {result.level_2_count}")
    print(f"Coordination:   {result.coordination_required}")

    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")

    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - SIOP Decomposer")
    parser.add_argument(
        "--package-dir", required=True, help="Customer package directory"
    )
    args = parser.parse_args()

    run_cli(args.package_dir)
