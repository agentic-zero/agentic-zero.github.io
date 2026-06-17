"""
AGENTIC ZERO — PIONEER TEAM
Agent: SIOP GENERATOR

Role:
Convert Functional Analysis into an internal SIOP contract for Architect.

Input:
  library/functional_analysis/*.json

Output:
  library/siop_internal/*.json

SIOP v1 sections:
1. Executive Summary
2. Business Context
3. Process Flow
4. Data Requirements
5. Business Rules
6. Compliance
7. Autonomy Design
8. Acceptance Criteria

Mantra:
"Does this make it feel like a living enterprise?"
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from loguru import logger

load_dotenv()

logger.add(
    "logs/siop_generator_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

SIOP_CONFIG = {
    "functional_analysis_path": os.getenv(
        "FUNCTIONAL_ANALYSIS_PATH", "library/functional_analysis"
    ),
    "siop_internal_path": os.getenv("SIOP_INTERNAL_PATH", "library/siop_internal"),
}


class ExecutiveSummary(BaseModel):
    process_name: str = ""
    validated_description: str = ""
    business_goal: str = ""
    value_baseline: dict[str, Any] = Field(default_factory=dict)
    recommended_route: str = ""
    confidence: float = 0.0


class BusinessContextSection(BaseModel):
    company: str = ""
    sector: str = ""
    erp: str = ""
    volume: str = ""
    team_size: str = ""
    documentation_score: float = 0.0
    compliance_implications: list[str] = Field(default_factory=list)


class ProcessFlowStep(BaseModel):
    step_id: str
    name: str
    owner: str = ""
    system: str = ""
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    rule: str = ""
    automation_candidate: bool = True
    confidence: float = 0.0


class DataRequirements(BaseModel):
    input_objects: list[str] = Field(default_factory=list)
    output_objects: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    master_data: list[str] = Field(default_factory=list)
    transactional_data: list[str] = Field(default_factory=list)
    data_quality_risks: list[str] = Field(default_factory=list)


class BusinessRulesSection(BaseModel):
    decision_rules: list[str] = Field(default_factory=list)
    approval_rules: list[str] = Field(default_factory=list)
    exception_rules: list[str] = Field(default_factory=list)
    missing_rules: list[str] = Field(default_factory=list)


class ComplianceSection(BaseModel):
    applicable_frameworks: list[str] = Field(default_factory=list)
    guardian_requirements: list[str] = Field(default_factory=list)
    audit_trail_required: bool = True
    human_review_required: bool = False
    regulated_process: bool = False


class AutonomyDesign(BaseModel):
    autonomous_actions: list[str] = Field(default_factory=list)
    approval_required: list[str] = Field(default_factory=list)
    always_human: list[str] = Field(default_factory=list)
    thresholds: dict[str, Any] = Field(default_factory=dict)
    escalation_paths: list[str] = Field(default_factory=list)
    agentic_shield_requirements: list[str] = Field(default_factory=list)


class AcceptanceCriteria(BaseModel):
    kpis: list[str] = Field(default_factory=list)
    certification_metrics: list[str] = Field(default_factory=list)
    minimum_confidence: float = 0.75
    test_scenarios: list[str] = Field(default_factory=list)
    pass_fail_criteria: list[str] = Field(default_factory=list)


class LearningHooks(BaseModel):
    enabled: bool = True
    observation_points: list[str] = Field(default_factory=list)
    failure_patterns_to_monitor: list[str] = Field(default_factory=list)
    kpi_deviation_signals: list[str] = Field(default_factory=list)
    feedback_targets: list[str] = Field(default_factory=list)
    improvement_loop: str = "observe_analyze_recommend_validate_deploy"


class SIOPInternal(BaseModel):
    siop_id: str
    created_at: str
    source_functional_analysis_id: str = ""
    internal_only: bool = True
    mantra: str = "Does this make it feel like a living enterprise?"
    executive_summary: ExecutiveSummary
    business_context: BusinessContextSection
    process_flow: list[ProcessFlowStep]
    data_requirements: DataRequirements
    business_rules: BusinessRulesSection
    compliance: ComplianceSection
    autonomy_design: AutonomyDesign
    acceptance_criteria: AcceptanceCriteria
    learning_hooks: LearningHooks
    missing_information: list[dict[str, Any]] = Field(default_factory=list)
    ready_for_validation: bool = False
    ready_for_architect: bool = False


def load_json(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_slug(value: str) -> str:
    value = (value or "siop").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "siop"


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(as_list(item))
        return out
    if isinstance(value, dict):
        out: list[str] = []
        for v in value.values():
            out.extend(as_list(v))
        return out
    if isinstance(value, str):
        if not value.strip():
            return []
        if "," in value and len(value) < 300:
            return [v.strip() for v in value.split(",") if v.strip()]
        return [value.strip()]
    return [str(value).strip()]


def unique(values: list[str]) -> list[str]:
    seen = set()
    out = []
    for v in values:
        key = v.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(v.strip())
    return out


def infer_compliance(sector: str, systems: list[str], rules: list[str]) -> ComplianceSection:
    sector_l = (sector or "").lower()
    text = (" ".join(rules) + " " + " ".join(systems)).lower()

    frameworks: list[str] = []
    guardian = [
        "Identity & Access",
        "Real-time Audit Trails",
        "Escalation Pathways",
        "Human Accountability",
    ]
    regulated = False
    human_review = False

    if "pharma" in sector_l or "gxp" in text:
        frameworks.extend(["GxP", "GMP", "GDP", "GAMP 5", "21 CFR Part 11"])
        guardian.extend(["Electronic Signature Control", "Validated Audit Trail"])
        regulated = True
        human_review = True

    if "defense" in sector_l or "aerospace" in sector_l:
        frameworks.extend(["AS9100", "ITAR/EAR", "Configuration Management"])
        guardian.extend(["Export Control", "Access Classification"])
        regulated = True
        human_review = True

    if "food" in sector_l:
        frameworks.extend(["HACCP", "ISO 22000", "FSSC 22000"])
        guardian.append("Critical Control Point Monitoring")
        regulated = True

    if "chemical" in sector_l:
        frameworks.extend(["REACH", "ADR/RID", "ISO 14001"])
        guardian.append("Hazardous Material Handling")
        regulated = True
        human_review = True

    if "ai" in text or "model" in text:
        frameworks.extend(["EU AI Act", "ISO/IEC 42001", "NIST AI RMF"])
        guardian.extend(["AI Risk Classification", "Explainability", "Model Monitoring"])

    if any(s.lower() in ["sap", "erp"] for s in systems):
        guardian.append("ERP Transaction Traceability")

    return ComplianceSection(
        applicable_frameworks=unique(frameworks),
        guardian_requirements=unique(guardian),
        audit_trail_required=True,
        human_review_required=human_review,
        regulated_process=regulated,
    )


def generate_siop(functional_analysis: dict[str, Any]) -> SIOPInternal:
    fa_id = functional_analysis.get("functional_analysis_id", "")
    bc = functional_analysis.get("business_context", {}) or {}
    pc = functional_analysis.get("process_context", {}) or {}

    process_name = pc.get("process_name") or "Customer Process"
    company = bc.get("company") or "customer"

    data_raw = functional_analysis.get("data_requirements", {}) or {}
    rules_raw = unique(as_list(functional_analysis.get("business_rules")))
    exceptions_raw = unique(as_list(functional_analysis.get("exceptions")))
    systems_raw = unique(as_list(functional_analysis.get("systems")))
    kpis_raw = unique(as_list(functional_analysis.get("kpis")))

    compliance = infer_compliance(bc.get("sector", ""), systems_raw, rules_raw)

    executive_summary = ExecutiveSummary(
        process_name=process_name,
        validated_description=(
            functional_analysis.get("procedure_overview")
            or f"Internal functional contract for {process_name}"
        ),
        business_goal=(
            f"Enable safe agentic automation for {process_name} while preserving "
            "control, traceability and continuous improvement."
        ),
        value_baseline={
            "volume": bc.get("volume", ""),
            "team_size": bc.get("team_size", ""),
            "documentation_score": bc.get("documentation_score", 0),
            "confidence": functional_analysis.get("confidence", 0),
        },
        recommended_route=bc.get("recommended_route", ""),
        confidence=float(functional_analysis.get("confidence") or 0),
    )

    business_context = BusinessContextSection(
        company=company,
        sector=bc.get("sector", ""),
        erp=bc.get("erp", ""),
        volume=str(bc.get("volume", "")),
        team_size=str(bc.get("team_size", "")),
        documentation_score=float(bc.get("documentation_score") or 0),
        compliance_implications=compliance.applicable_frameworks,
    )

    process_flow: list[ProcessFlowStep] = []
    for i, step in enumerate(functional_analysis.get("business_process_flow", []) or [], start=1):
        process_flow.append(
            ProcessFlowStep(
                step_id=step.get("step_id") or f"STEP-{i:02d}",
                name=step.get("name") or f"Step {i}",
                owner=step.get("owner", ""),
                system=step.get("system", ""),
                inputs=as_list(step.get("input")),
                outputs=as_list(step.get("output")),
                rule=step.get("business_rule", ""),
                automation_candidate=True,
                confidence=float(step.get("confidence") or 0.5),
            )
        )

    input_objects = unique(as_list(data_raw.get("input_objects")))
    output_objects = unique(as_list(data_raw.get("output_objects")))
    documents = unique(as_list(data_raw.get("documents")))

    data_requirements = DataRequirements(
        input_objects=input_objects,
        output_objects=output_objects,
        documents=documents,
        master_data=[
            x for x in input_objects
            if x.lower() in ["customer", "supplier", "product", "material", "price"]
        ],
        transactional_data=[
            x for x in input_objects + output_objects
            if x.lower() in ["order", "invoice", "shipment", "payment", "forecast", "purchase order"]
        ],
        data_quality_risks=[
            "Missing master data",
            "Incomplete transaction data",
            "Inconsistent system ownership",
        ],
    )

    approval_rules = [
        r for r in rules_raw
        if any(k in r.lower() for k in ["approval", "threshold", "authorize", "blocked", "credit"])
    ]

    business_rules = BusinessRulesSection(
        decision_rules=rules_raw,
        approval_rules=unique(approval_rules),
        exception_rules=unique([f"Exception handling required: {e}" for e in exceptions_raw]),
        missing_rules=[],
    )

    autonomy_raw = functional_analysis.get("autonomy_boundaries", {}) or {}
    allowed = unique(as_list(autonomy_raw.get("allowed") or autonomy_raw.get("fully_automated") or autonomy_raw.get("autonomous_actions")))
    approval = unique(as_list(autonomy_raw.get("approval_required")))
    always_human = unique(as_list(autonomy_raw.get("always_human")))

    if not allowed:
        allowed = ["Read data", "Validate data", "Create draft recommendation"]
    if compliance.human_review_required and not approval:
        approval = ["Regulated or critical decisions require human approval"]

    autonomy_design = AutonomyDesign(
        autonomous_actions=allowed,
        approval_required=approval,
        always_human=always_human,
        thresholds={
            "approval_threshold": autonomy_raw.get("approval_threshold", ""),
            "documentation_score": bc.get("documentation_score", 0),
        },
        escalation_paths=[
            "Escalate low-confidence decisions",
            "Escalate exceptions not covered by business rules",
            "Escalate regulated decisions when required",
        ],
        agentic_shield_requirements=unique(
            compliance.guardian_requirements
            + ["Action Thresholds", "Fail-Safes", "Real-time Audit Trails", "Human Accountability"]
        ),
    )

    acceptance_criteria = AcceptanceCriteria(
        kpis=kpis_raw or ["cycle time", "error rate", "automation rate", "exception rate"],
        certification_metrics=[
            "All mandatory data objects available",
            "All critical exceptions have handling path",
            "Autonomy thresholds configured",
            "Audit trail active",
            "Human escalation path tested",
        ],
        test_scenarios=[
            f"Happy path test for {process_name}",
            "Missing data exception test",
            "System unavailable exception test",
            "Human approval escalation test",
            "Audit trail verification test",
        ],
        pass_fail_criteria=[
            "No critical missing information",
            "Process flow contains at least one executable step",
            "Systems and data objects are defined",
            "Business rules or Fast Track validation captured",
            "Autonomy design includes escalation handling",
        ],
    )

    learning_hooks = LearningHooks(
        enabled=True,
        observation_points=[
            "step execution time",
            "exception frequency",
            "human escalation frequency",
            "manual override frequency",
            "KPI deviation from target",
        ],
        failure_patterns_to_monitor=exceptions_raw or ["unknown exception", "manual rework", "approval delay"],
        kpi_deviation_signals=acceptance_criteria.kpis,
        feedback_targets=[
            "business_rules",
            "exceptions",
            "autonomy_design",
            "acceptance_criteria",
            "agent_blueprint",
        ],
    )

    missing = functional_analysis.get("missing_information", []) or []
    critical_missing = [
        m for m in missing
        if isinstance(m, dict) and m.get("severity") == "critical"
    ]

    ready = (
        len(process_flow) > 0
        and len(data_requirements.input_objects) > 0
        and len(systems_raw) > 0
        and len(business_rules.decision_rules) > 0
        and len(critical_missing) == 0
    )

    siop_id = f"SIOP-{safe_slug(company)}-{safe_slug(process_name)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return SIOPInternal(
        siop_id=siop_id,
        created_at=datetime.now().isoformat(),
        source_functional_analysis_id=fa_id,
        executive_summary=executive_summary,
        business_context=business_context,
        process_flow=process_flow,
        data_requirements=data_requirements,
        business_rules=business_rules,
        compliance=compliance,
        autonomy_design=autonomy_design,
        acceptance_criteria=acceptance_criteria,
        learning_hooks=learning_hooks,
        missing_information=missing,
        ready_for_validation=True,
        ready_for_architect=ready,
    )


def save_siop(siop: SIOPInternal) -> Path:
    out_dir = Path(SIOP_CONFIG["siop_internal_path"])
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"{siop.siop_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(siop.model_dump(), f, indent=2, ensure_ascii=False)
    logger.info(f"SIOP internal saved: {filename}")
    return filename


def generate_siop_from_file(functional_analysis_path: str | Path) -> SIOPInternal:
    logger.info(f"Generating SIOP from: {functional_analysis_path}")
    functional_analysis = load_json(functional_analysis_path)
    siop = generate_siop(functional_analysis)
    save_siop(siop)
    logger.success(
        f"SIOP generated | id={siop.siop_id} | ready_for_validation={siop.ready_for_validation} | ready_for_architect={siop.ready_for_architect}"
    )
    return siop


def run_siop_generator(functional_analysis_path: str):
    result = generate_siop_from_file(functional_analysis_path)
    print("\n✅ SIOP Generator complete")
    print(f"   SIOP ID: {result.siop_id}")
    print(f"   Source Functional Analysis: {result.source_functional_analysis_id}")
    print(f"   Ready for validation: {result.ready_for_validation}")
    print(f"   Ready for Architect: {result.ready_for_architect}")
    print(f"   Missing information: {len(result.missing_information)}")
    print("\nNext:")
    print("   python siop_validator.py --siop <generated_siop_path>")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero — SIOP Generator")
    parser.add_argument("--functional-analysis", required=True, help="Path to Functional Analysis JSON")
    args = parser.parse_args()
    run_siop_generator(args.functional_analysis)
