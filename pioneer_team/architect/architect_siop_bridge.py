"""
AGENTIC ZERO -- PIONEER TEAM
architect_siop_bridge.py

Role:
  Reads a validated SIOPInternal JSON and produces an ArchitectBlueprint
  that the Builder can consume directly to generate the agent code.

  This is the link between:
    SIOP Generator (validated contract)
    Architect     (validation + sector variants)
    Builder       (code generation)

Input:
  library/siop_internal/{SIOP_ID}.json

Output:
  library/architect_blueprints/{SIOP_ID}_blueprint.json

The blueprint contains:
  - process_id        -> used as filename and agent identifier
  - agent_class_name  -> PascalCase class name for the generated agent
  - steps[]           -> each step with system, inputs, outputs, rule, escalation
  - connectors[]      -> external systems the agent must connect to
  - escalations[]     -> typed escalation scenarios with recipients and actions
  - shield_config     -> CooperBench Shield requirements from SIOP compliance
  - learning_hooks    -> observation points for The Machine
  - acceptance_tests  -> test scenarios the Guardian will validate
  - builder_prompt    -> enriched prompt for the Builder LLM
"""

import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict

# -- PATHS ---------------------------------------------------------------------
SIOP_PATH       = Path(os.getenv("SIOP_INTERNAL_PATH", "library/siop_internal"))
BLUEPRINT_PATH  = Path(os.getenv("BLUEPRINT_PATH", "library/architect_blueprints"))
BLUEPRINT_PATH.mkdir(parents=True, exist_ok=True)


# -- DATA MODELS ---------------------------------------------------------------
@dataclass
class BlueprintStep:
    step_id: str
    name: str
    owner: str
    system: str
    inputs: list[str]
    outputs: list[str]
    rule: str
    automation_candidate: bool
    escalation_trigger: str       # condition that triggers escalation
    escalation_type: str          # "credit" | "capacity" | "price" | "approval" | "none"
    sap_transactions: list[str]   # SAP tx codes extracted from system field
    external_apis: list[str]      # non-SAP APIs extracted from system field
    confidence: float


@dataclass
class BlueprintConnector:
    name: str
    type: str            # "sap_rfc" | "rest_api" | "email" | "file"
    system: str
    env_var_host: str    # env variable name for the host/url
    env_var_key: str     # env variable name for credentials
    operations: list[str]
    dry_run_mock: str    # name of the mock method in dry-run mode


@dataclass
class BlueprintEscalation:
    trigger: str
    condition: str
    recipient_env_var: str
    action: str          # "block_and_notify" | "draft_email" | "queue" | "alert"
    auto_resolvable: bool
    resolution_hint: str


@dataclass
class ArchitectBlueprint:
    blueprint_id: str
    siop_id: str
    source_fa_id: str
    created_at: str
    process_id: str                # e.g. "BPMN-OTC-001"
    agent_class_name: str          # e.g. "OTCAgent"
    agent_description: str
    company: str
    sector: str
    erp: str
    volume: str
    operating_hours: str
    confidence_threshold: float
    steps: list[BlueprintStep]
    connectors: list[BlueprintConnector]
    escalations: list[BlueprintEscalation]
    autonomous_actions: list[str]
    approval_required: list[str]
    always_human: list[str]
    shield_requirements: list[str]
    compliance_frameworks: list[str]
    kpis: list[str]
    learning_hooks: dict[str, Any]
    acceptance_tests: list[str]
    missing_info: list[dict]
    ready_for_builder: bool
    builder_prompt: str            # full enriched prompt for Builder LLM


# -- SAP TRANSACTION EXTRACTOR -------------------------------------------------
# Known SAP transaction codes the Builder should use
SAP_TX_PATTERNS = [
    "VA01", "VA02", "VA03",           # Sales orders
    "VL01N", "VL02N", "VL03N",        # Deliveries
    "VF01", "VF02", "VF04",           # Invoices
    "FD32", "FD33",                   # Credit management
    "VK11", "VK12", "VK13",           # Pricing conditions
    "ME21N", "ME22N", "ME23N",        # Purchase orders
    "MIGO", "MIRO",                   # Goods movement / invoice verification
    "FB01", "FB02", "FB03",           # FI postings
    "ZED1", "ZED2",                   # Custom output types
]

SAP_BAPI_PATTERNS = [
    "BAPI_CREDIT_CHECK",
    "BAPI_DELIVERYPROCESSING_EXEC",
    "RV_INVOICE_CREATE",
    "RFC_READ_TABLE",
    "BAPI_PRICING",
    "BAPI_MESSAGING_SEND",
]


def _extract_sap_artifacts(text: str) -> tuple[list[str], list[str]]:
    """Extract SAP transaction codes and BAPIs from a text string."""
    tx = [t for t in SAP_TX_PATTERNS if t.lower() in text.lower()]
    bapi = [b for b in SAP_BAPI_PATTERNS if b.lower() in text.lower()]
    return list(set(tx)), list(set(bapi))


def _extract_external_apis(text: str) -> list[str]:
    """Detect external (non-SAP) API references."""
    apis = []
    if "tms" in text.lower():
        apis.append("TMS_REST_API")
    if "email" in text.lower() or "buzon" in text.lower():
        apis.append("EMAIL_READER")
    if "pdf" in text.lower() or "extracto" in text.lower():
        apis.append("PDF_PARSER")
    return list(set(apis))


def _to_pascal_case(name: str) -> str:
    """Convert process name to PascalCase class name."""
    words = re.sub(r"[^a-zA-Z0-9 ]", " ", name).split()
    return "".join(w.capitalize() for w in words if w) + "Agent"


def _to_process_id(siop_id: str, process_name: str) -> str:
    """Derive a library-compatible process_id from SIOP data."""
    name_clean = re.sub(r"[^a-zA-Z0-9]", "-", process_name).upper()
    name_clean = re.sub(r"-+", "-", name_clean).strip("-")
    return f"CUSTOMER-{name_clean[:20]}"


def _escalation_type_from_rule(rule: str) -> str:
    """Classify escalation type from business rule text."""
    rule_l = rule.lower()
    if "credito" in rule_l or "credit" in rule_l or "vencido" in rule_l or "fd32" in rule_l:
        return "credit"
    if "capacidad" in rule_l or "capacity" in rule_l or "tms" in rule_l or "ruta" in rule_l:
        return "capacity"
    if "precio" in rule_l or "price" in rule_l or "vk11" in rule_l or "discrepancia" in rule_l:
        return "price"
    if "pago anticipado" in rule_l or "prepayment" in rule_l or "extracto" in rule_l:
        return "prepayment"
    if "international" in rule_l or "internacional" in rule_l or "zint" in rule_l:
        return "international_docs"
    if "escalat" in rule_l or "aprobacion" in rule_l or "approval" in rule_l:
        return "approval"
    return "none"


def _escalation_action_from_type(esc_type: str) -> str:
    mapping = {
        "credit":            "block_and_notify_finance",
        "capacity":          "draft_capacity_email_and_notify_ops",
        "price":             "block_and_notify_ops",
        "prepayment":        "queue_and_notify_ops",
        "international_docs": "block_and_notify_ops",
        "approval":          "queue_and_await_approval",
        "none":              "log_and_continue",
    }
    return mapping.get(esc_type, "log_and_continue")


# -- BUILDER PROMPT GENERATOR --------------------------------------------------
def _build_builder_prompt(siop: dict, blueprint: "ArchitectBlueprint") -> str:
    """
    Generate the full enriched prompt that the Builder LLM will use
    to generate the agent Python code.
    """
    steps_text = "\n".join([
        f"  {s.step_id}: {s.name}\n"
        f"    System: {s.system}\n"
        f"    Rule: {s.rule}\n"
        f"    SAP tx: {s.sap_transactions}\n"
        f"    External APIs: {s.external_apis}\n"
        f"    Escalation: {s.escalation_type} -> {s.escalation_trigger}"
        for s in blueprint.steps
    ])

    connectors_text = "\n".join([
        f"  {c.name} ({c.type}): {c.operations}"
        for c in blueprint.connectors
    ])

    escalations_text = "\n".join([
        f"  {e.trigger}: {e.action} -> env:{e.recipient_env_var}"
        for e in blueprint.escalations
    ])

    return f"""You are the Agentic Zero Builder Agent. Generate a complete, production-ready Python autonomous agent.

PROCESS: {blueprint.agent_description}
CLASS NAME: {blueprint.agent_class_name}
PROCESS ID: {blueprint.process_id}
COMPANY: {blueprint.company} | SECTOR: {blueprint.sector} | ERP: {blueprint.erp}
VOLUME: {blueprint.volume}
OPERATING HOURS: {blueprint.operating_hours}
CONFIDENCE THRESHOLD: {blueprint.confidence_threshold}

PROCESS STEPS (implement each as an async method):
{steps_text}

EXTERNAL CONNECTORS (implement each as a class with connect() and dry-run mock):
{connectors_text}

ESCALATION SCENARIOS (implement handle_escalation() with all cases):
{escalations_text}

AUTONOMOUS ACTIONS (agent executes without human approval):
{chr(10).join('  - ' + a for a in blueprint.autonomous_actions)}

APPROVAL REQUIRED (agent pauses and awaits human decision):
{chr(10).join('  - ' + a for a in blueprint.approval_required)}

ALWAYS HUMAN (agent never executes these autonomously):
{chr(10).join('  - ' + a for a in blueprint.always_human)}

AGENTIC SHIELD REQUIREMENTS (embed in every decision):
{chr(10).join('  - ' + s for s in blueprint.shield_requirements)}

COMPLIANCE FRAMEWORKS (embed compliance checks):
{chr(10).join('  - ' + f for f in blueprint.compliance_frameworks)}

KPIs TO TRACK (log in audit trail and dashboard events):
{chr(10).join('  - ' + k for k in blueprint.kpis)}

LEARNING HOOKS FOR THE MACHINE (emit these events):
{json.dumps(blueprint.learning_hooks, indent=2)}

ACCEPTANCE TEST SCENARIOS (all must pass before Guardian certification):
{chr(10).join('  - ' + t for t in blueprint.acceptance_tests)}

MISSING INFORMATION (handle gracefully with dry-run mock until resolved):
{chr(10).join('  - ' + m.get('field','?') + ': ' + m.get('reason','') for m in blueprint.missing_info)}

MANDATORY CODE REQUIREMENTS:
1. All process steps as async methods: step_01_order_received(), step_02_validate_order(), etc.
2. SAPConnector class with connect(), all required RFC/BAPI calls, and _mock_* dry-run methods
3. External API connectors (TMS, email) with connect() and _mock_* dry-run methods
4. handle_escalation(order, reason) covering ALL escalation scenarios above
5. EmailDraftGenerator for capacity notifications using xAI grok-3-mini
6. AuditEntry dataclass -- log every decision with timestamp, rule, confidence, outcome
7. Dashboard events JSONL stream for Autonomy Dashboard
8. CLI: --mode live/dry-run/single --order ORDER_ID
9. EU AI Act ART.12 audit trail -- ART.14 human oversight checkpoints
10. ASCII-only source code (Windows PowerShell compatible)
11. Dry-run mode must work with zero external dependencies
12. Config via environment variables (.env file)
13. Operating hours check: queue orders outside {blueprint.operating_hours}

The agent must make it feel like a living enterprise. Every order processed updates the Enterprise Pulse.
Generate complete, runnable Python code. No placeholders. No TODO comments. Production-ready."""


# -- MAIN BRIDGE FUNCTION ------------------------------------------------------
def siop_to_blueprint(siop: dict) -> ArchitectBlueprint:
    """
    Convert a validated SIOPInternal into an ArchitectBlueprint
    that the Builder can consume directly.
    """
    siop_id   = siop.get("siop_id", "")
    fa_id     = siop.get("source_functional_analysis_id", "")
    es        = siop.get("executive_summary", {})
    bc        = siop.get("business_context", {})
    flow      = siop.get("process_flow", [])
    data_req  = siop.get("data_requirements", {})
    biz_rules = siop.get("business_rules", {})
    compliance = siop.get("compliance", {})
    autonomy  = siop.get("autonomy_design", {})
    ac        = siop.get("acceptance_criteria", {})
    learning  = siop.get("learning_hooks", {})
    missing   = siop.get("missing_information", [])

    process_name = es.get("process_name", "Customer Process")
    company      = bc.get("company", "customer")

    # -- STEPS -----------------------------------------------------------------
    steps: list[BlueprintStep] = []
    for step in flow:
        rule = step.get("rule", "")
        system = step.get("system", "")
        full_text = f"{rule} {system} {step.get('name','')}".lower()

        tx, bapi = _extract_sap_artifacts(full_text)
        ext_apis = _extract_external_apis(full_text)
        esc_type = _escalation_type_from_rule(rule)

        # Determine escalation trigger condition from rule text
        esc_trigger = ""
        if esc_type == "credit":
            esc_trigger = "overdue_days > credit_overdue_days OR sap_credit_blocked"
        elif esc_type == "capacity":
            esc_trigger = "tms_capacity_available == False"
        elif esc_type == "price":
            esc_trigger = "abs(quoted_price - condition_price) / condition_price > price_tolerance"
        elif esc_type == "prepayment":
            esc_trigger = "payment_terms == PREPAYMENT"
        elif esc_type == "international_docs":
            esc_trigger = "order_type == ZINT AND NOT international_docs"

        steps.append(BlueprintStep(
            step_id=step.get("step_id", f"STEP-{len(steps)+1:02d}"),
            name=step.get("name", ""),
            owner=step.get("owner", ""),
            system=system,
            inputs=step.get("inputs", []) or step.get("input", []),
            outputs=step.get("outputs", []) or step.get("output", []),
            rule=rule,
            automation_candidate=step.get("automation_candidate", True),
            escalation_trigger=esc_trigger,
            escalation_type=esc_type,
            sap_transactions=tx + bapi,
            external_apis=ext_apis,
            confidence=float(step.get("confidence", 0.5)),
        ))

    # -- CONNECTORS ------------------------------------------------------------
    connectors: list[BlueprintConnector] = []

    # Detect SAP connector need
    all_systems = " ".join([s.get("system", "") for s in flow]).lower()
    if "sap" in all_systems:
        # Collect all unique SAP tx from steps
        all_tx = list(set(tx for s in steps for tx in s.sap_transactions))
        connectors.append(BlueprintConnector(
            name="SAPConnector",
            type="sap_rfc",
            system=bc.get("erp", "SAP ECC"),
            env_var_host="SAP_HOST",
            env_var_key="SAP_PASSWORD",
            operations=all_tx or ["RFC_READ_TABLE", "BAPI_CREDIT_CHECK"],
            dry_run_mock="_mock_sap_data",
        ))

    if "tms" in all_systems or "api rest" in all_systems:
        connectors.append(BlueprintConnector(
            name="TMSConnector",
            type="rest_api",
            system="TMS External",
            env_var_host="TMS_API_URL",
            env_var_key="TMS_API_KEY",
            operations=["check_capacity", "assign_route"],
            dry_run_mock="_mock_tms_capacity",
        ))

    if "email" in all_systems or "pdf" in all_systems or "extracto" in all_systems:
        connectors.append(BlueprintConnector(
            name="EmailConnector",
            type="email",
            system="Email / PDF reader",
            env_var_host="EMAIL_HOST",
            env_var_key="EMAIL_PASSWORD",
            operations=["read_inbox", "parse_pdf_statement"],
            dry_run_mock="_mock_email_inbox",
        ))

    # -- ESCALATIONS -----------------------------------------------------------
    escalations: list[BlueprintEscalation] = []
    decision_rules = biz_rules.get("decision_rules", [])
    exception_rules = biz_rules.get("exception_rules", [])
    approval_rules  = biz_rules.get("approval_rules", [])

    # Build escalations from rules
    for rule_text in decision_rules + exception_rules + approval_rules:
        esc_type = _escalation_type_from_rule(rule_text)
        if esc_type == "none":
            continue

        recipient_map = {
            "credit":             "ESCALATION_FINANCE",
            "capacity":           "ESCALATION_OPS",
            "price":              "ESCALATION_OPS",
            "prepayment":         "ESCALATION_OPS",
            "international_docs": "ESCALATION_OPS",
            "approval":           "ESCALATION_OPS",
        }

        # Deduplicate by escalation type (esc_type), comparing against the
        # 'trigger' field already set on each BlueprintEscalation built so far.
        if any(e.trigger == esc_type for e in escalations):
            continue

        escalations.append(BlueprintEscalation(
            trigger=esc_type,
            condition=rule_text[:200],
            recipient_env_var=recipient_map.get(esc_type, "ESCALATION_OPS"),
            action=_escalation_action_from_type(esc_type),
            auto_resolvable=(esc_type in ["capacity"]),
            resolution_hint=(
                "Generate capacity email draft with 2 alternative TMS slots"
                if esc_type == "capacity"
                else "Await human decision via Autonomy Dashboard"
            ),
        ))

    # -- PROCESS ID + CLASS NAME -----------------------------------------------
    process_id     = _to_process_id(siop_id, process_name)
    agent_class    = _to_pascal_case(process_name)

    # -- BLUEPRINT -------------------------------------------------------------
    thresholds = autonomy.get("thresholds", {})
    blueprint = ArchitectBlueprint(
        blueprint_id=f"BP-{siop_id}",
        siop_id=siop_id,
        source_fa_id=fa_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        process_id=process_id,
        agent_class_name=agent_class,
        agent_description=es.get("validated_description", process_name),
        company=company,
        sector=bc.get("sector", ""),
        erp=bc.get("erp", ""),
        volume=bc.get("volume", ""),
        operating_hours=str(thresholds.get("approval_threshold", "07:00-22:00 CET")),
        confidence_threshold=float(thresholds.get("documentation_score", 0.85)) or 0.85,
        steps=steps,
        connectors=connectors,
        escalations=escalations,
        autonomous_actions=autonomy.get("autonomous_actions", []),
        approval_required=autonomy.get("approval_required", []),
        always_human=autonomy.get("always_human", []),
        shield_requirements=autonomy.get("agentic_shield_requirements", []),
        compliance_frameworks=compliance.get("applicable_frameworks", []),
        kpis=ac.get("kpis", []),
        learning_hooks={
            "enabled":              learning.get("enabled", True),
            "observation_points":   learning.get("observation_points", []),
            "failure_patterns":     learning.get("failure_patterns_to_monitor", []),
            "kpi_deviation_signals": learning.get("kpi_deviation_signals", []),
            "feedback_targets":     learning.get("feedback_targets", []),
            "improvement_loop":     learning.get("improvement_loop", ""),
        },
        acceptance_tests=ac.get("test_scenarios", []),
        missing_info=[m for m in missing if isinstance(m, dict)],
        ready_for_builder=siop.get("ready_for_architect", False),
        builder_prompt="",  # filled below
    )

    # Generate builder prompt after blueprint is assembled
    blueprint.builder_prompt = _build_builder_prompt(siop, blueprint)

    return blueprint


def save_blueprint(blueprint: ArchitectBlueprint) -> Path:
    filename = BLUEPRINT_PATH / f"{blueprint.siop_id}_blueprint.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(asdict(blueprint), f, indent=2, ensure_ascii=False)
    print(f"Blueprint saved: {filename}")
    return filename


def save_process_for_builder(blueprint: ArchitectBlueprint) -> Path:
    """
    Save a process entry in the format Builder expects.
    Builder searches: library/*/processes/{process_id}.json
    We write to:      library/sector_specific/processes/{process_id}.json
    """
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    processes_dir = library_path / "sector_specific" / "processes"
    processes_dir.mkdir(parents=True, exist_ok=True)

    bp = asdict(blueprint)

    # Collect all unique inputs/outputs from steps
    all_inputs  = list(dict.fromkeys(
        inp for s in blueprint.steps for inp in s.inputs
    ))[:15]
    all_outputs = list(dict.fromkeys(
        out for s in blueprint.steps for out in s.outputs
    ))[:15]

    process_entry = {
        "process_id":          blueprint.process_id,
        "name":                (blueprint.agent_description or blueprint.agent_class_name)[:80],
        "framework":           "CUSTOMER_FUNCTIONAL_ANALYSIS",
        "domain":              blueprint.sector or "operations",
        "level":               "L3",
        "description":         blueprint.agent_description,
        "inputs":              all_inputs,
        "outputs":             all_outputs,
        "kpis":                blueprint.kpis,
        "compliance_flags":    blueprint.compliance_frameworks + blueprint.shield_requirements,
        "business_rules":      [e.condition for e in blueprint.escalations if e.condition],
        "sector_applicability": [blueprint.sector or "all"],
        "source":              "Architect SIOP Bridge -- Customer Pipeline",
        "confidence":          blueprint.confidence_threshold,
        # Extended fields -- Builder uses builder_prompt for LLM enrichment
        "procedure_steps":     [asdict(s) for s in blueprint.steps],
        "connectors":          [c.name for c in blueprint.connectors],
        "escalation_types":    list(dict.fromkeys(e.trigger for e in blueprint.escalations)),
        "builder_prompt":      blueprint.builder_prompt,
        "blueprint_id":        blueprint.blueprint_id,
        "siop_id":             blueprint.siop_id,
        "company":             blueprint.company,
        "erp":                 blueprint.erp,
        "volume":              blueprint.volume,
        "operating_hours":     blueprint.operating_hours,
        "agent_class_name":    blueprint.agent_class_name,
        "learning_hooks":      blueprint.learning_hooks,
        "acceptance_tests":    blueprint.acceptance_tests,
        "missing_info":        blueprint.missing_info,
    }

    filename = processes_dir / f"{blueprint.process_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(process_entry, f, indent=2, ensure_ascii=False)

    print(f"Process entry saved for Builder: {filename}")
    return filename


def run_bridge(siop_path: str) -> ArchitectBlueprint:
    with open(siop_path, encoding="utf-8") as f:
        siop = json.load(f)

    blueprint = siop_to_blueprint(siop)
    path = save_blueprint(blueprint)
    save_process_for_builder(blueprint)  # -> library/sector_specific/processes/{process_id}.json

    print(f"\n== Architect SIOP Bridge ==")
    print(f"  SIOP ID:          {blueprint.siop_id}")
    print(f"  Process ID:       {blueprint.process_id}")
    print(f"  Agent class:      {blueprint.agent_class_name}")
    print(f"  Steps:            {len(blueprint.steps)}")
    print(f"  Connectors:       {len(blueprint.connectors)} ({[c.name for c in blueprint.connectors]})")
    print(f"  Escalations:      {len(blueprint.escalations)} ({[e.trigger for e in blueprint.escalations]})")
    print(f"  Shield reqs:      {len(blueprint.shield_requirements)}")
    print(f"  Ready for Builder:{blueprint.ready_for_builder}")
    print(f"  Blueprint saved:  {path}")
    print(f"\nNext:")
    print(f"  python builder.py --blueprint {path}")
    return blueprint


if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description="Agentic Zero -- Architect SIOP Bridge")
    parser.add_argument("--siop", required=True, help="Path to SIOPInternal JSON")
    args = parser.parse_args()
    run_bridge(args.siop)
