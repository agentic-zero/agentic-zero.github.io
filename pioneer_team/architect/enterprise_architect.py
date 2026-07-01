"""
AGENTIC ZERO - PIONEER TEAM
Enterprise Architect v1.1

Role:
  Understand a customer SIOP or enterprise intent and decide what the factory must build.

Detects:
  - PROCESS_AGENT
  - COMPLEX_PROCESS_AGENT
  - SWARM
  - AGENTIC_ONE_ENTERPRISE

Important fix v1.1:
  S&OP, IBP, Control Tower, Digital Twin, MRP, DRP, APS, WMS/TMS networks,
  planning systems and other interconnected systems are classified as SWARM,
  not Agentic One, unless the SIOP clearly asks for whole-company autonomy.

Recommended path:
  pioneer_team/architect/enterprise_architect.py
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
    name: str
    organism: str
    agent_type: str
    domain: str
    purpose: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    systems: list[str] = field(default_factory=list)
    upstream_dependencies: list[str] = field(default_factory=list)
    downstream_dependencies: list[str] = field(default_factory=list)
    autonomy_level: str = "semi_autonomous"


@dataclass
class IntentClassification:
    intent_id: str
    created_at: str
    route: str
    tier: str
    confidence: float
    rationale: str
    detected_keywords: list[str]
    level_1_process: str
    coordination_required: bool
    agentic_one_required: bool
    swarm_required: bool


@dataclass
class SIOPDecomposition:
    decomposition_id: str
    created_at: str
    level_1_process: str
    route: str
    level_2_siops: list[Level2SIOP]
    coordination_required: bool
    coordination_siop_required: bool
    agentic_one_required: bool
    notes: str


@dataclass
class FactoryOrder:
    factory_order_id: str
    created_at: str
    route: str
    tier: str
    package_dir: str
    factory_mode: str
    level_1_process: str
    required_components: list[str]
    level_2_siop_ids: list[str]
    coordination_siop_required: bool
    agentic_one_required: bool
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


ENTERPRISE_SCOPE_TERMS = [
    "toda la empresa",
    "empresa completa",
    "mi empresa autonoma",
    "mi empresa autónoma",
    "whole company",
    "entire company",
    "entire enterprise",
    "make my company autonomous",
    "make the whole company autonomous",
    "autonomous enterprise",
    "agentic one",
    "living enterprise",
    "zero human company",
    "zero human enterprise",
    "enterprise wide autonomy",
    "enterprise-wide autonomy",
    "autonomous organization",
    "empresa viva",
    "empresa zero human",
]

SWARM_KEYWORDS = [
    "s&op",
    "sop",
    "siop",
    "ibp",
    "integrated business planning",
    "sales and operations planning",
    "demand planning",
    "demand sensing",
    "forecasting",
    "supply planning",
    "inventory planning",
    "capacity planning",
    "finance reconciliation",
    "constraint resolution",
    "control tower",
    "digital twin",
    "enterprise twin",
    "supply chain twin",
    "planning tower",
    "supply chain control tower",
    "integrated planning",
    "connected planning",
    "scenario planning",
    "what-if simulation",
    "aps",
    "advanced planning system",
    "mrp",
    "mrp ii",
    "drp",
    "distribution requirements planning",
    "mps",
    "master production schedule",
    "atp",
    "available to promise",
    "ctp",
    "capable to promise",
    "e2e planning",
    "end-to-end planning",
    "end to end planning",
    "cross-functional",
    "cross functional",
    "multi-domain",
    "multidomain",
    "multi organism",
    "multi-agent",
    "multi agent",
    "swarm",
    "orchestration",
    "synchronized planning",
    "network planning",
    "warehouse network",
    "transport network",
    "procurement planning",
    "supplier collaboration",
    "ariba",
    "kinaxis",
    "rapidresponse",
    "omp",
    "o9",
    "blue yonder",
    "sap ibp",
    "sap apo",
    "sap ppds",
    "sap tm",
    "sap ewm",
    "procesos interconectados",
    "sistemas interconectados",
    "procesos conectados",
    "planificacion integrada",
    "planificación integrada",
    "torre de control",
    "gemelo digital",
]

COMPLEX_PROCESS_KEYWORDS = [
    "workflow",
    "approval",
    "exception",
    "escalation",
    "multi-step",
    "varios pasos",
    "rules",
    "reglas",
    "sap",
    "erp",
    "tms",
    "wms",
    "crm",
    "api",
    "rpa",
    "human approval",
    "business rule",
]

SIMPLE_PROCESS_KEYWORDS = [
    "otc",
    "order to cash",
    "invoice matching",
    "order validation",
    "ap",
    "accounts payable",
    "procurement request",
    "ticket classification",
    "email classification",
]


DOMAIN_TEMPLATES = {
    "demand": {
        "name": "Demand Planning",
        "organism": "Demand Planning Organism",
        "agent_type": "demand_planning_agent",
        "domain": "planning",
        "purpose": "Forecast demand, detect deviations and generate demand scenarios.",
        "inputs": [
            "historical sales",
            "forecast baseline",
            "promotions",
            "market signals",
        ],
        "outputs": ["demand forecast", "demand risk signal", "forecast confidence"],
        "systems": ["SAP IBP", "ERP", "CRM", "Excel/CSV"],
    },
    "inventory": {
        "name": "Inventory Planning",
        "organism": "Inventory Planning Organism",
        "agent_type": "inventory_planning_agent",
        "domain": "planning",
        "purpose": "Evaluate inventory position, coverage, excess, shortage and replenishment needs.",
        "inputs": ["stock on hand", "safety stock", "open orders", "forecast"],
        "outputs": [
            "inventory plan",
            "shortage risk",
            "excess risk",
            "replenishment proposal",
        ],
        "systems": ["ERP", "WMS", "SAP IBP"],
    },
    "supply": {
        "name": "Supply Planning",
        "organism": "Supply Planning Organism",
        "agent_type": "supply_planning_agent",
        "domain": "supply",
        "purpose": "Match supply, procurement and production availability against demand.",
        "inputs": [
            "supplier capacity",
            "purchase orders",
            "production plan",
            "lead times",
        ],
        "outputs": ["supply plan", "supplier risk", "available-to-plan signal"],
        "systems": ["ERP", "SAP Ariba", "MRP", "SAP IBP"],
    },
    "capacity": {
        "name": "Capacity Planning",
        "organism": "Capacity Planning Organism",
        "agent_type": "capacity_planning_agent",
        "domain": "operations",
        "purpose": "Evaluate production, warehouse, labor or transport capacity constraints.",
        "inputs": [
            "resource capacity",
            "warehouse capacity",
            "transport capacity",
            "production calendar",
        ],
        "outputs": ["capacity plan", "constraint alert", "capacity utilization"],
        "systems": ["ERP", "TMS", "WMS", "MES"],
    },
    "finance": {
        "name": "Finance Reconciliation",
        "organism": "Finance Reconciliation Organism",
        "agent_type": "finance_reconciliation_agent",
        "domain": "finance",
        "purpose": "Translate operational plans into margin, cash, working capital and budget impact.",
        "inputs": ["sales forecast", "cost assumptions", "working capital", "budget"],
        "outputs": ["financial reconciliation", "margin impact", "cash impact"],
        "systems": ["ERP FI-CO", "EPM", "Excel/CSV"],
    },
    "constraint": {
        "name": "Constraint Resolution",
        "organism": "Constraint Resolution Organism",
        "agent_type": "constraint_resolution_agent",
        "domain": "orchestration",
        "purpose": "Resolve conflicts between demand, supply, inventory, capacity and financial constraints.",
        "inputs": [
            "demand plan",
            "supply plan",
            "inventory plan",
            "capacity plan",
            "financial impact",
        ],
        "outputs": ["resolved plan", "trade-off decision", "escalation recommendation"],
        "systems": ["Agentic Shield", "ERP", "Collaboration workflow"],
    },
    "risk": {
        "name": "Risk Monitoring",
        "organism": "Risk Monitoring Organism",
        "agent_type": "risk_monitoring_agent",
        "domain": "risk",
        "purpose": "Detect operational, supplier, demand, cash and compliance risk signals.",
        "inputs": [
            "risk events",
            "exceptions",
            "supplier alerts",
            "service deviations",
        ],
        "outputs": ["risk score", "risk classification", "mitigation recommendation"],
        "systems": ["Control Tower", "ERP", "External risk feeds"],
    },
    "control_tower": {
        "name": "Control Tower",
        "organism": "Control Tower Organism",
        "agent_type": "control_tower_agent",
        "domain": "operations",
        "purpose": "Monitor end-to-end flow, exceptions, alerts, service and execution health.",
        "inputs": ["orders", "shipments", "inventory", "exceptions", "KPIs"],
        "outputs": [
            "enterprise pulse",
            "alerts",
            "priority queue",
            "exception routing",
        ],
        "systems": ["Control Tower", "ERP", "TMS", "WMS", "BI"],
    },
    "digital_twin": {
        "name": "Digital Twin Simulation",
        "organism": "Digital Twin Organism",
        "agent_type": "digital_twin_agent",
        "domain": "simulation",
        "purpose": "Simulate scenarios, constraints and impact before execution.",
        "inputs": [
            "network model",
            "scenario parameters",
            "constraints",
            "historical performance",
        ],
        "outputs": ["scenario result", "impact simulation", "recommended option"],
        "systems": ["Digital Twin", "Simulation Engine", "BI", "ERP"],
    },
}


def extract_level_1_process(siop: dict[str, Any], text: str) -> str:
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

    if "s&op" in text or "sales and operations planning" in text:
        return "Sales and Operations Planning"
    if "ibp" in text or "integrated business planning" in text:
        return "Integrated Business Planning"
    if "control tower" in text or "torre de control" in text:
        return "Control Tower"
    if "digital twin" in text or "gemelo digital" in text:
        return "Digital Twin"
    if "otc" in text or "order to cash" in text:
        return "Order to Cash"
    if "empresa" in text and "auton" in text:
        return "Agentic One Autonomous Enterprise"

    return "Customer Process"


def detect_keywords(text: str, keywords: list[str]) -> list[str]:
    return [k for k in keywords if k.lower() in text]


def classify_intent(
    siop: dict[str, Any], package_dir: str | Path
) -> IntentClassification:
    text = flatten_text(siop).lower()
    level_1 = extract_level_1_process(siop, text)

    enterprise_hits = detect_keywords(text, ENTERPRISE_SCOPE_TERMS)
    swarm_hits = detect_keywords(text, SWARM_KEYWORDS)
    complex_hits = detect_keywords(text, COMPLEX_PROCESS_KEYWORDS)
    simple_hits = detect_keywords(text, SIMPLE_PROCESS_KEYWORDS)

    domain_count = 0
    for key in [
        "demand",
        "forecast",
        "inventory",
        "stock",
        "supply",
        "procurement",
        "capacity",
        "finance",
        "cash",
        "constraint",
        "risk",
        "control tower",
        "digital twin",
        "simulation",
        "planning",
    ]:
        if key in text:
            domain_count += 1

    explicit_swarm_system = any(
        k in text
        for k in [
            "s&op",
            "sales and operations planning",
            "ibp",
            "integrated business planning",
            "control tower",
            "digital twin",
            "torre de control",
            "gemelo digital",
            "aps",
            "mrp",
            "drp",
            "sap ibp",
            "kinaxis",
            "o9",
            "blue yonder",
            "omp",
        ]
    )

    if enterprise_hits:
        route = "AGENTIC_ONE_ENTERPRISE"
        tier = "Enterprise"
        confidence = 0.95
        rationale = "Whole-enterprise autonomy intent detected."
    elif explicit_swarm_system or (swarm_hits and domain_count >= 2):
        route = "SWARM"
        tier = "Enterprise"
        confidence = 0.90
        rationale = "Interconnected system or multi-domain process detected."
    elif swarm_hits:
        route = "COMPLEX_PROCESS_AGENT"
        tier = "Standard"
        confidence = 0.78
        rationale = (
            "Planning/system keywords detected but insufficient evidence for swarm."
        )
    elif complex_hits:
        route = "COMPLEX_PROCESS_AGENT"
        tier = "Standard"
        confidence = 0.76
        rationale = "Multi-step process with rules/systems/exceptions detected."
    else:
        route = "PROCESS_AGENT"
        tier = "Essential"
        confidence = 0.72 if simple_hits else 0.65
        rationale = "Simple or insufficiently decomposed process."

    return IntentClassification(
        intent_id=f"INTENT-{_upper_slug(level_1)}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        route=route,
        tier=tier,
        confidence=confidence,
        rationale=rationale,
        detected_keywords=enterprise_hits + swarm_hits + complex_hits + simple_hits,
        level_1_process=level_1,
        coordination_required=route in ["SWARM", "AGENTIC_ONE_ENTERPRISE"],
        agentic_one_required=route == "AGENTIC_ONE_ENTERPRISE",
        swarm_required=route == "SWARM",
    )


def domain_present(text: str, key: str) -> bool:
    synonyms = {
        "demand": ["demand", "forecast", "forecasting", "sales forecast", "demanda"],
        "inventory": ["inventory", "stock", "coverage", "inventario", "existencias"],
        "supply": [
            "supply",
            "supplier",
            "procurement",
            "purchase",
            "suministro",
            "compras",
            "mrp",
        ],
        "capacity": [
            "capacity",
            "constraint",
            "production capacity",
            "warehouse capacity",
            "transport capacity",
            "capacidad",
        ],
        "finance": [
            "finance",
            "financial",
            "margin",
            "cash",
            "working capital",
            "budget",
            "finanzas",
        ],
        "constraint": [
            "constraint resolution",
            "trade-off",
            "arbitration",
            "conflict",
            "restricción",
            "resolución",
        ],
        "risk": ["risk", "riesgo", "compliance", "alert"],
        "control_tower": [
            "control tower",
            "torre de control",
            "visibility",
            "exception monitoring",
        ],
        "digital_twin": [
            "digital twin",
            "gemelo digital",
            "simulation",
            "what-if",
            "scenario simulation",
        ],
    }
    return any(s in text for s in synonyms.get(key, [key]))


def build_level2_siop(template_key: str, level_1_process: str) -> Level2SIOP:
    t = DOMAIN_TEMPLATES[template_key]
    prefix = _upper_slug(level_1_process)
    return Level2SIOP(
        siop_id=f"{prefix}-{_upper_slug(t['name'])}",
        name=t["name"],
        organism=t["organism"],
        agent_type=t["agent_type"],
        domain=t["domain"],
        purpose=t["purpose"],
        inputs=t["inputs"],
        outputs=t["outputs"],
        systems=t["systems"],
    )


def infer_dependencies(level2: list[Level2SIOP]) -> list[Level2SIOP]:
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
    dep("demand_planning_agent", "finance_reconciliation_agent")
    dep("supply_planning_agent", "finance_reconciliation_agent")
    dep("inventory_planning_agent", "finance_reconciliation_agent")
    dep("capacity_planning_agent", "finance_reconciliation_agent")

    for agent in [
        "demand_planning_agent",
        "inventory_planning_agent",
        "supply_planning_agent",
        "capacity_planning_agent",
        "finance_reconciliation_agent",
        "risk_monitoring_agent",
        "control_tower_agent",
        "digital_twin_agent",
    ]:
        dep(agent, "constraint_resolution_agent")

    dep("control_tower_agent", "risk_monitoring_agent")
    dep("digital_twin_agent", "constraint_resolution_agent")
    dep("risk_monitoring_agent", "constraint_resolution_agent")

    return list(by_agent.values())


def decompose_siop(
    siop: dict[str, Any], classification: IntentClassification
) -> SIOPDecomposition:
    text = flatten_text(siop).lower()
    level_1 = classification.level_1_process
    selected: list[str] = []

    if classification.route == "AGENTIC_ONE_ENTERPRISE":
        selected = [
            "demand",
            "inventory",
            "supply",
            "capacity",
            "finance",
            "risk",
            "control_tower",
            "digital_twin",
            "constraint",
        ]
    elif classification.route == "SWARM":
        selected = [key for key in DOMAIN_TEMPLATES if domain_present(text, key)]

        if any(k in text for k in ["s&op", "sales and operations planning", "sop"]):
            for required in ["demand", "inventory", "supply", "finance", "constraint"]:
                if required not in selected:
                    selected.append(required)

        if any(k in text for k in ["ibp", "integrated business planning"]):
            for required in [
                "demand",
                "inventory",
                "supply",
                "capacity",
                "finance",
                "constraint",
            ]:
                if required not in selected:
                    selected.append(required)

        if "control tower" in text or "torre de control" in text:
            for required in [
                "control_tower",
                "risk",
                "inventory",
                "supply",
                "constraint",
            ]:
                if required not in selected:
                    selected.append(required)

        if "digital twin" in text or "gemelo digital" in text:
            for required in [
                "digital_twin",
                "capacity",
                "inventory",
                "supply",
                "finance",
                "constraint",
            ]:
                if required not in selected:
                    selected.append(required)

        if any(
            k in text
            for k in [
                "mrp",
                "drp",
                "aps",
                "sap ibp",
                "kinaxis",
                "o9",
                "blue yonder",
                "omp",
            ]
        ):
            for required in ["demand", "inventory", "supply", "capacity", "constraint"]:
                if required not in selected:
                    selected.append(required)

    level2 = [build_level2_siop(key, level_1) for key in selected]
    level2 = infer_dependencies(level2)

    return SIOPDecomposition(
        decomposition_id=f"DEC-{_upper_slug(level_1)}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        level_1_process=level_1,
        route=classification.route,
        level_2_siops=level2,
        coordination_required=classification.coordination_required,
        coordination_siop_required=classification.coordination_required
        and len(level2) >= 2,
        agentic_one_required=classification.agentic_one_required,
        notes=(
            "Swarm decomposition generated."
            if classification.route == "SWARM"
            else "Agentic One enterprise decomposition generated."
            if classification.route == "AGENTIC_ONE_ENTERPRISE"
            else "No decomposition required for this route."
        ),
    )


def build_coordination_siop(
    classification: IntentClassification, decomposition: SIOPDecomposition
) -> dict[str, Any]:
    if not decomposition.coordination_siop_required:
        return {}

    organisms = [asdict(x) for x in decomposition.level_2_siops]

    return {
        "coordination_siop_id": f"COORD-{_upper_slug(decomposition.level_1_process)}",
        "created_at": _now(),
        "level_1_process": decomposition.level_1_process,
        "route": classification.route,
        "purpose": "Coordinate organisms so the factory does not generate isolated linear agents.",
        "organisms": organisms,
        "coordination_rules": [
            "Demand changes must notify Inventory, Supply and Finance organisms.",
            "Supply constraints must notify Capacity, Finance and Constraint Resolution organisms.",
            "Inventory shortages must notify Supply and Constraint Resolution organisms.",
            "Control Tower events must notify Risk and Constraint Resolution organisms.",
            "Digital Twin simulations must be validated before operational recommendations are released.",
            "Constraint Resolution organism arbitrates conflicting recommendations.",
        ],
        "shared_context": [
            "planning_horizon",
            "forecast_version",
            "scenario_id",
            "constraint_id",
            "financial_impact",
            "confidence_score",
            "risk_score",
        ],
        "shield_arbitration": {
            "autonomous_allowed": [
                "low-risk scenario generation",
                "data validation",
                "variance detection",
                "draft recommendation creation",
                "risk classification",
            ],
            "approval_required": [
                "final plan approval",
                "policy threshold changes",
                "supplier commitment changes",
                "financial target changes",
                "network configuration changes",
            ],
            "always_human": [
                "strategic trade-off decision",
                "budget commitment",
                "customer promise outside policy",
                "irreversible operational change",
            ],
            "conflict_resolution": [
                "If two organisms disagree and confidence delta < 0.10, route to Constraint Resolution.",
                "If financial impact exceeds threshold, require human approval.",
                "If service risk and cash risk conflict, escalate to process owner.",
                "If Digital Twin simulation contradicts operational data, require review.",
            ],
        },
        "event_routes": [
            {
                "from": "Demand Planning Organism",
                "to": "Inventory Planning Organism",
                "event": "demand_plan_updated",
            },
            {
                "from": "Demand Planning Organism",
                "to": "Supply Planning Organism",
                "event": "demand_plan_updated",
            },
            {
                "from": "Supply Planning Organism",
                "to": "Capacity Planning Organism",
                "event": "supply_constraint_detected",
            },
            {
                "from": "Inventory Planning Organism",
                "to": "Constraint Resolution Organism",
                "event": "shortage_or_excess_detected",
            },
            {
                "from": "Finance Reconciliation Organism",
                "to": "Constraint Resolution Organism",
                "event": "financial_deviation_detected",
            },
            {
                "from": "Control Tower Organism",
                "to": "Risk Monitoring Organism",
                "event": "risk_signal_detected",
            },
            {
                "from": "Digital Twin Organism",
                "to": "Constraint Resolution Organism",
                "event": "scenario_conflict_detected",
            },
        ],
        "acceptance_criteria": [
            "All organism outputs are traceable.",
            "Conflicting recommendations are routed to Constraint Resolution.",
            "No final plan is approved without Shield validation.",
            "All coordination events are emitted to The Machine.",
        ],
        "learning_hooks": {
            "observation_points": [
                "organism_conflict",
                "coordination_delay",
                "human_override",
                "final_plan_rework",
                "simulation_deviation",
            ],
            "failure_patterns": [
                "isolated_agent_decision",
                "missing_context",
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


def required_components_for_route(route: str) -> list[str]:
    if route in ["PROCESS_AGENT", "COMPLEX_PROCESS_AGENT"]:
        return [
            "customer_pipeline",
            "agent_developer",
            "essential_packager",
            "guardian_adapter",
            "auditor_adapter",
            "delivery_gate",
        ]

    if route == "SWARM":
        return [
            "enterprise_architect",
            "swarm_splitter",
            "swarm_blueprint_generator",
            "agent_developer_multi",
            "swarm_coordinator",
            "swarm_packager",
            "guardian_adapter",
            "auditor_adapter",
            "delivery_gate",
        ]

    return [
        "enterprise_architect",
        "enterprise_blueprint_generator",
        "domain_swarm_planner",
        "swarm_splitter",
        "swarm_blueprint_generator",
        "agent_developer_multi",
        "swarm_coordinator",
        "swarm_packager",
        "the_machine_initializer",
        "guardian_adapter",
        "auditor_adapter",
        "delivery_gate",
    ]


def factory_mode_for_route(route: str) -> str:
    return {
        "PROCESS_AGENT": "FULL_BUILD",
        "COMPLEX_PROCESS_AGENT": "FULL_BUILD",
        "SWARM": "SWARM_BUILD",
        "AGENTIC_ONE_ENTERPRISE": "AGENTIC_ONE_BUILD",
    }.get(route, "FULL_BUILD")


def build_factory_order(
    package_dir: str | Path,
    classification: IntentClassification,
    decomposition: SIOPDecomposition,
) -> FactoryOrder:
    return FactoryOrder(
        factory_order_id=f"FO-{_upper_slug(classification.level_1_process)}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        route=classification.route,
        tier=classification.tier,
        package_dir=str(package_dir),
        factory_mode=factory_mode_for_route(classification.route),
        level_1_process=classification.level_1_process,
        required_components=required_components_for_route(classification.route),
        level_2_siop_ids=[x.siop_id for x in decomposition.level_2_siops],
        coordination_siop_required=decomposition.coordination_siop_required,
        agentic_one_required=decomposition.agentic_one_required,
        next_step=(
            "Run master_orchestrator.py for PROCESS_AGENT/COMPLEX_PROCESS_AGENT."
            if classification.route in ["PROCESS_AGENT", "COMPLEX_PROCESS_AGENT"]
            else "Run swarm_splitter.py / swarm_generator.py before master_orchestrator."
        ),
    )


def run_enterprise_architect(
    siop_path: str | Path, package_dir: str | Path
) -> dict[str, Any]:
    siop = read_json(siop_path)
    package_dir = Path(package_dir)

    out_dir = package_dir / "00_enterprise_intent"
    out_dir.mkdir(parents=True, exist_ok=True)

    classification = classify_intent(siop, package_dir)
    decomposition = decompose_siop(siop, classification)
    coordination_siop = build_coordination_siop(classification, decomposition)
    factory_order = build_factory_order(package_dir, classification, decomposition)

    paths = {
        "intent_classification": out_dir / "intent_classification.json",
        "siop_decomposition": out_dir / "siop_decomposition.json",
        "swarm_coordination_siop": out_dir / "swarm_coordination_siop.json",
        "factory_order": out_dir / "factory_order.json",
    }

    write_json(paths["intent_classification"], asdict(classification))
    write_json(paths["siop_decomposition"], asdict(decomposition))
    write_json(paths["swarm_coordination_siop"], coordination_siop)
    write_json(paths["factory_order"], asdict(factory_order))

    return {
        "route": classification.route,
        "tier": classification.tier,
        "confidence": classification.confidence,
        "level_1_process": classification.level_1_process,
        "level_2_count": len(decomposition.level_2_siops),
        "coordination_required": decomposition.coordination_required,
        "coordination_siop_required": decomposition.coordination_siop_required,
        "agentic_one_required": decomposition.agentic_one_required,
        "outputs": {k: str(v) for k, v in paths.items()},
        "next_step": factory_order.next_step,
    }


def run_cli(siop_path: str, package_dir: str):
    result = run_enterprise_architect(siop_path, package_dir)

    print("\nEnterprise Architect complete")
    print(f"Route:        {result['route']}")
    print(f"Tier:         {result['tier']}")
    print(f"Confidence:   {int(result['confidence'] * 100)}%")
    print(f"Process:      {result['level_1_process']}")
    print(f"Level 2 SIOPs:{result['level_2_count']}")
    print(f"Coordination: {result['coordination_siop_required']}")
    print(f"Agentic One:  {result['agentic_one_required']}")

    print("\nOutput:")
    for k, v in result["outputs"].items():
        print(f"  {k}: {v}")

    print(f"\nNext: {result['next_step']}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Enterprise Architect")
    parser.add_argument("--siop", required=True, help="Path to SIOP internal JSON")
    parser.add_argument(
        "--package-dir", required=True, help="Path to customer essential_package folder"
    )
    args = parser.parse_args()
    run_cli(args.siop, args.package_dir)
