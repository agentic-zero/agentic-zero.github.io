
"""
AGENTIC ZERO — Essential Blueprint Instruction Pack

Defines the Essential package output contract and validation gates.
Intended path:
  pioneer_team/architect/essential_blueprint.py

It does not replace existing agents. It gives customer_pipeline,
Architect Bridge, Builder, Packager, Guardian and Auditor a shared
delivery contract.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


ESSENTIAL_REQUIRED_ARTIFACTS = [
    "functional_analysis_json",
    "siop_internal_json",
    "siop_validation_json",
    "architect_blueprint_json",
    "agent_runtime_py",
    "sop_md",
    "integration_guide_md",
    "dashboard_html",
    "roi_calculator_html",
    "escalation_policy_md",
    "guardian_certificate",
    "auditor_decision_json",
    "delivery_manifest_json",
    "client_executive_summary_md",
]

ESSENTIAL_FINAL_STATUSES = [
    "DELIVERABLE",
    "DELIVERABLE_WITH_CONDITIONS",
    "BLOCKED_MISSING_INFORMATION",
    "BLOCKED_COMPLIANCE",
    "BLOCKED_BUILD_FAILURE",
]

LIVING_ENTERPRISE_REQUIRED_KEYS = [
    "observation_points",
    "failure_patterns",
    "kpi_deviation_signals",
    "feedback_targets",
    "improvement_loop",
]


@dataclass
class EssentialClientInput:
    company: str = ""
    contact_name: str = ""
    role: str = ""
    sector: str = ""
    erp: str = ""
    process_name: str = ""
    domains: list[str] = field(default_factory=list)
    subprocesses: list[str] = field(default_factory=list)
    volume: str = ""
    team_size: str = ""
    manual_time_per_transaction_min: str = ""
    business_rules: list[str] = field(default_factory=list)
    critical_exceptions: list[str] = field(default_factory=list)
    data_used: list[str] = field(default_factory=list)
    systems_involved: list[str] = field(default_factory=list)
    process_map_uploaded: bool = False
    documentation_score: float = 0.0
    recommended_route: str = ""


@dataclass
class EssentialArtifact:
    key: str
    path: str = ""
    required: bool = True
    exists: bool = False
    status: str = "missing"
    notes: str = ""


@dataclass
class EssentialGateResult:
    gate: str
    passed: bool
    score: float
    blocking_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class EssentialBlueprintContract:
    contract_id: str
    created_at: str
    client: EssentialClientInput
    artifacts: list[EssentialArtifact]
    gates: list[EssentialGateResult]
    final_status: str
    ready_for_delivery: bool
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "customer").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "customer"


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, dict):
        out: list[str] = []
        for v in value.values():
            out.extend(_as_list(v))
        return out
    if isinstance(value, str):
        if not value.strip():
            return []
        if "," in value and len(value) < 300:
            return [v.strip() for v in value.split(",") if v.strip()]
        return [value.strip()]
    return [str(value).strip()]


def normalize_client_input(raw: dict[str, Any]) -> EssentialClientInput:
    return EssentialClientInput(
        company=raw.get("company") or raw.get("Company") or raw.get("client") or "",
        contact_name=raw.get("contact_name") or raw.get("name") or "",
        role=raw.get("role") or raw.get("job_title") or "",
        sector=raw.get("sector") or raw.get("industry") or "",
        erp=raw.get("erp") or raw.get("core_system") or raw.get("system") or "",
        process_name=raw.get("process_name") or raw.get("process") or "",
        domains=_as_list(raw.get("domains") or raw.get("areas") or raw.get("selected_domains")),
        subprocesses=_as_list(raw.get("subprocesses") or raw.get("selected_subprocesses")),
        volume=str(raw.get("volume") or raw.get("daily_volume") or ""),
        team_size=str(raw.get("team_size") or raw.get("fte") or ""),
        manual_time_per_transaction_min=str(
            raw.get("manual_time_per_transaction_min")
            or raw.get("time_per_order")
            or raw.get("manual_minutes")
            or ""
        ),
        business_rules=_as_list(raw.get("business_rules")),
        critical_exceptions=_as_list(raw.get("critical_exceptions") or raw.get("exceptions")),
        data_used=_as_list(raw.get("data_used") or raw.get("data_objects")),
        systems_involved=_as_list(raw.get("systems_involved") or raw.get("systems")),
        process_map_uploaded=bool(raw.get("process_map_uploaded") or raw.get("uploaded_file")),
        documentation_score=float(raw.get("documentation_score") or 0),
        recommended_route=raw.get("recommended_route") or raw.get("recommended_path") or "",
    )


def validate_functional_readiness(client: EssentialClientInput) -> EssentialGateResult:
    issues: list[str] = []
    warnings: list[str] = []

    if not client.company:
        issues.append("company missing")
    if not client.sector:
        issues.append("sector missing")
    if not client.erp:
        warnings.append("erp/core system missing")
    if not client.process_name and not client.subprocesses:
        issues.append("process name or subprocesses missing")
    if not client.systems_involved and not client.erp:
        issues.append("systems involved missing")
    if not client.data_used:
        issues.append("data objects missing")
    if not client.business_rules:
        issues.append("business rules missing")
    if not client.critical_exceptions:
        warnings.append("critical exceptions missing or unknown")

    score = max(0.0, round(1.0 - len(issues) * 0.18 - len(warnings) * 0.07, 2))
    return EssentialGateResult(
        gate="functional_readiness",
        passed=len(issues) == 0 and score >= 0.70,
        score=score,
        blocking_issues=issues,
        warnings=warnings,
    )


def validate_siop_contract(siop: dict[str, Any]) -> EssentialGateResult:
    sections = [
        "executive_summary",
        "business_context",
        "process_flow",
        "data_requirements",
        "business_rules",
        "compliance",
        "autonomy_design",
        "acceptance_criteria",
    ]
    issues = [f"missing section: {s}" for s in sections if not siop.get(s)]
    warnings = []
    if not siop.get("learning_hooks"):
        warnings.append("learning_hooks missing")
    if not siop.get("ready_for_architect", False):
        warnings.append("ready_for_architect is false")
    score = round((len(sections) - len(issues)) / len(sections), 2)
    return EssentialGateResult("siop_contract", len(issues) == 0 and score >= 0.85, score, issues, warnings)


def validate_blueprint_contract(blueprint: dict[str, Any]) -> EssentialGateResult:
    required = [
        "process_id",
        "agent_class_name",
        "steps",
        "connectors",
        "escalations",
        "shield_requirements",
        "learning_hooks",
        "acceptance_tests",
        "builder_prompt",
    ]
    issues = [f"missing blueprint field: {k}" for k in required if not blueprint.get(k)]
    warnings = []
    if blueprint.get("ready_for_builder") is False:
        warnings.append("ready_for_builder is false")
    score = round((len(required) - len(issues)) / len(required), 2)
    return EssentialGateResult("blueprint_contract", len(issues) == 0 and score >= 0.85, score, issues, warnings)


def validate_living_enterprise_hooks(learning_hooks: dict[str, Any]) -> EssentialGateResult:
    warnings = [f"missing learning key: {k}" for k in LIVING_ENTERPRISE_REQUIRED_KEYS if not learning_hooks.get(k)]
    score = round((len(LIVING_ENTERPRISE_REQUIRED_KEYS) - len(warnings)) / len(LIVING_ENTERPRISE_REQUIRED_KEYS), 2)
    return EssentialGateResult("living_enterprise_hooks", len(warnings) == 0, score, [], warnings)


def build_artifact_manifest(package_dir: str | Path) -> list[EssentialArtifact]:
    package_dir = Path(package_dir)
    expected_paths = {
        "functional_analysis_json": "01_functional_analysis/functional_analysis.json",
        "siop_internal_json": "02_siop/siop_internal.json",
        "siop_validation_json": "02_siop/siop_validation.json",
        "architect_blueprint_json": "03_blueprint/architect_blueprint.json",
        "agent_runtime_py": "04_agent/agent_runtime.py",
        "sop_md": "05_delivery/sop.md",
        "integration_guide_md": "05_delivery/integration_guide.md",
        "dashboard_html": "05_delivery/dashboard.html",
        "roi_calculator_html": "05_delivery/roi_calculator.html",
        "escalation_policy_md": "05_delivery/escalation_policy.md",
        "guardian_certificate": "06_compliance/guardian_certificate.txt",
        "auditor_decision_json": "06_compliance/auditor_decision.json",
        "delivery_manifest_json": "delivery_manifest.json",
        "client_executive_summary_md": "05_delivery/client_executive_summary.md",
    }
    artifacts: list[EssentialArtifact] = []
    for key in ESSENTIAL_REQUIRED_ARTIFACTS:
        rel = expected_paths.get(key, key)
        path = package_dir / rel
        exists = path.exists()
        artifacts.append(EssentialArtifact(key=key, path=str(path), exists=exists, status="present" if exists else "missing"))
    return artifacts


def decide_final_status(gates: list[EssentialGateResult], artifacts: list[EssentialArtifact]) -> tuple[str, bool, str]:
    blocking = [i for g in gates for i in g.blocking_issues]
    missing_required = [a.key for a in artifacts if a.required and not a.exists]
    if blocking:
        return "BLOCKED_MISSING_INFORMATION", False, "Resolve blocking gate issues before delivery."
    if missing_required:
        return "BLOCKED_BUILD_FAILURE", False, "Generate missing required artifacts."
    warnings = [w for g in gates for w in g.warnings]
    if warnings:
        return "DELIVERABLE_WITH_CONDITIONS", True, "Deliver with documented conditions and remediation notes."
    return "DELIVERABLE", True, "Ready for customer delivery."


def create_essential_contract(
    client_payload: dict[str, Any],
    package_dir: str | Path,
    siop: Optional[dict[str, Any]] = None,
    blueprint: Optional[dict[str, Any]] = None,
) -> EssentialBlueprintContract:
    client = normalize_client_input(client_payload)
    artifacts = build_artifact_manifest(package_dir)
    gates = [validate_functional_readiness(client)]
    if siop is not None:
        gates.append(validate_siop_contract(siop))
        gates.append(validate_living_enterprise_hooks(siop.get("learning_hooks", {})))
    if blueprint is not None:
        gates.append(validate_blueprint_contract(blueprint))
        gates.append(validate_living_enterprise_hooks(blueprint.get("learning_hooks", {})))

    final_status, ready, next_step = decide_final_status(gates, artifacts)
    contract_id = f"ESS-{_slug(client.company)}-{_slug(client.process_name or 'process')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return EssentialBlueprintContract(contract_id, _now(), client, artifacts, gates, final_status, ready, next_step)


def save_contract(contract: EssentialBlueprintContract, package_dir: str | Path) -> Path:
    package_dir = Path(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    out = package_dir / "essential_blueprint_contract.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(asdict(contract), f, indent=2, ensure_ascii=False)
    return out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero — Essential Blueprint Contract")
    parser.add_argument("--client", required=True, help="Path to AUDIT ZERO / client JSON")
    parser.add_argument("--package-dir", required=True, help="Essential package output folder")
    parser.add_argument("--siop", default=None, help="Optional SIOP internal JSON")
    parser.add_argument("--blueprint", default=None, help="Optional Architect Blueprint JSON")
    args = parser.parse_args()

    with open(args.client, encoding="utf-8") as f:
        client_payload = json.load(f)

    siop = None
    if args.siop:
        with open(args.siop, encoding="utf-8") as f:
            siop = json.load(f)

    blueprint = None
    if args.blueprint:
        with open(args.blueprint, encoding="utf-8") as f:
            blueprint = json.load(f)

    contract = create_essential_contract(client_payload, args.package_dir, siop, blueprint)
    path = save_contract(contract, args.package_dir)

    print(f"Essential contract saved: {path}")
    print(f"Status: {contract.final_status}")
    print(f"Ready for delivery: {contract.ready_for_delivery}")
    print(f"Next: {contract.next_step}")
