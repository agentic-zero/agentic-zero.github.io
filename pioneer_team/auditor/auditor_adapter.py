"""
AGENTIC ZERO - PIONEER TEAM
Auditor Adapter v1.0

Role:
  Adapt the customer Essential Package audit flow to the existing auditor.py logic.

Why this exists:
  The current auditor.py is valid and should not be replaced.
  It audits library/review_queue based artifacts.
  Essential packages now live under:

    clients/{client}/{process}/essential_package/

This adapter audits Essential packages directly and writes customer-delivery
audit outputs into:

    07_audit/

Recommended location:
  pioneer_team/auditor/auditor_adapter.py

Input:
  --package-dir clients/{client}/{process}/essential_package

Expected package structure:
  01_functional_analysis/
  02_siop/
  03_blueprint/
  04_agent/
  05_delivery/
  06_compliance/

Output:
  07_audit/
    auditor_decision.json
    audit_report.md
    audit_scorecard.json
    qa_findings.json

Decision:
  AUTO_APPROVE
  APPROVE_WITH_CONDITIONS
  HOLD
  REJECT

Next:
  delivery_gate.py

Mantra:
  Does this make it feel like a living enterprise?
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------


@dataclass
class AuditFinding:
    area: str
    severity: str  # INFO | LOW | MEDIUM | HIGH | CRITICAL
    message: str
    recommendation: str = ""


@dataclass
class AuditCheck:
    name: str
    status: str  # PASS | WARN | FAIL
    score: float
    findings: list[AuditFinding] = field(default_factory=list)


@dataclass
class AuditorAdapterResult:
    process_id: str
    package_dir: str
    audited_at: str
    decision: str
    delivery: bool
    restricted: bool
    escalate: bool
    overall_score: float
    checks: list[AuditCheck]
    conditions: list[str]
    outputs: dict[str, str]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


# ---------------------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def pct(score: float) -> int:
    return int(round(score * 100))


def read_json(
    path: str | Path, default: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return default or {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_text(path: str | Path, default: str = "") -> str:
    path = Path(path)
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8", errors="replace")


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


# ---------------------------------------------------------------------------
# PACKAGE LOADER
# ---------------------------------------------------------------------------


def load_package(package_dir: str | Path) -> dict[str, Any]:
    root = Path(package_dir)

    paths = {
        "functional": root / "01_functional_analysis" / "functional_analysis.json",
        "siop": root / "02_siop" / "siop_internal.json",
        "siop_validation": root / "02_siop" / "siop_validation.json",
        "blueprint": root / "03_blueprint" / "architect_blueprint.json",
        "agent_runtime": root / "04_agent" / "agent_runtime.py",
        "developer_manifest": root / "04_agent" / "developer_manifest.json",
        "sop": root / "05_delivery" / "sop.md",
        "integration_guide": root / "05_delivery" / "integration_guide.md",
        "escalation_policy": root / "05_delivery" / "escalation_policy.md",
        "client_summary": root / "05_delivery" / "client_executive_summary.md",
        "dashboard": root / "05_delivery" / "dashboard.html",
        "roi": root / "05_delivery" / "roi_calculator.html",
        "delivery_manifest": root / "delivery_manifest.json",
        "guardian_result": root / "06_compliance" / "guardian_result.json",
        "guardian_certificate": root / "06_compliance" / "guardian_certificate.txt",
        "agentic_certificate": root / "06_compliance" / "agentic_certificate.json",
    }

    functional = read_json(paths["functional"])
    siop = read_json(paths["siop"])
    validation = read_json(paths["siop_validation"])
    blueprint = read_json(paths["blueprint"])
    developer = read_json(paths["developer_manifest"])
    delivery_manifest = read_json(paths["delivery_manifest"])
    guardian = read_json(paths["guardian_result"])
    agentic_certificate = read_json(paths["agentic_certificate"])

    process_id = (
        blueprint.get("process_id")
        or siop.get("process_id")
        or siop.get("siop_id")
        or guardian.get("process_id")
        or delivery_manifest.get("process_id")
        or "ESSENTIAL-PROCESS"
    )

    agent_name = (
        blueprint.get("agent_class_name")
        or developer.get("agent_class_name")
        or guardian.get("agentic_certificate", {}).get("agent_name")
        or "EssentialAgent"
    )

    company = (
        blueprint.get("company")
        or siop.get("business_context", {}).get("company")
        or functional.get("business_context", {}).get("company")
        or delivery_manifest.get("company")
        or "Customer"
    )

    return {
        "root": root,
        "paths": paths,
        "functional": functional,
        "siop": siop,
        "validation": validation,
        "blueprint": blueprint,
        "developer": developer,
        "delivery_manifest": delivery_manifest,
        "guardian": guardian,
        "agentic_certificate": agentic_certificate,
        "process_id": process_id,
        "agent_name": agent_name,
        "company": company,
        "agent_runtime_text": read_text(paths["agent_runtime"]),
    }


# ---------------------------------------------------------------------------
# CHECKS
# ---------------------------------------------------------------------------


def check_package_completeness(pkg: dict[str, Any]) -> AuditCheck:
    required = [
        "functional",
        "siop",
        "siop_validation",
        "blueprint",
        "agent_runtime",
        "developer_manifest",
        "sop",
        "integration_guide",
        "escalation_policy",
        "client_summary",
        "dashboard",
        "roi",
        "delivery_manifest",
        "guardian_result",
        "guardian_certificate",
        "agentic_certificate",
    ]

    findings: list[AuditFinding] = []

    for key in required:
        if not pkg["paths"][key].exists():
            severity = (
                "HIGH"
                if key in ["guardian_result", "agent_runtime", "blueprint"]
                else "MEDIUM"
            )
            findings.append(
                AuditFinding(
                    area="package_completeness",
                    severity=severity,
                    message=f"Missing required artifact: {key}",
                    recommendation=f"Generate {key} before delivery.",
                )
            )

    score = max(0.0, 1.0 - len(findings) * 0.06)
    status = "PASS" if not findings else ("WARN" if score >= 0.70 else "FAIL")

    return AuditCheck("package_completeness", status, round(score, 2), findings)


def check_cross_document_consistency(pkg: dict[str, Any]) -> AuditCheck:
    findings: list[AuditFinding] = []

    # process_id is the short business-process identifier used consistently
    # by Blueprint, Guardian and Delivery Manifest (e.g. CUSTOMER-ORDER-TO-CASH-OTC).
    # SIOP intentionally does NOT carry this field -- it has its own siop_id,
    # which encodes the document's unique generation identity (slug + timestamp).
    # These two identifiers serve different purposes and must NOT be compared
    # against each other. Comparing them produced false-positive HIGH findings
    # on every package (found during Sprint validation, 19 Jun 2026).
    process_ids = {
        "blueprint": pkg["blueprint"].get("process_id"),
        "guardian": pkg["guardian"].get("process_id"),
        "delivery_manifest": pkg["delivery_manifest"].get("process_id"),
    }
    present_ids = {k: v for k, v in process_ids.items() if v}

    if len(set(present_ids.values())) > 1:
        findings.append(
            AuditFinding(
                area="cross_document_consistency",
                severity="HIGH",
                message=f"Process ID mismatch across documents: {present_ids}",
                recommendation="Normalize process_id across Blueprint, Guardian and Delivery Manifest.",
            )
        )

    # SIOP traceability check -- informational only, never blocking.
    # Confirms the SIOP this package was built from is still identifiable,
    # without forcing it to share the business process_id namespace.
    siop_id = pkg["siop"].get("siop_id") or pkg["siop"].get("process_id")
    if not siop_id:
        findings.append(
            AuditFinding(
                area="cross_document_consistency",
                severity="LOW",
                message="SIOP document has no siop_id or process_id for traceability.",
                recommendation="Ensure SIOP Generator always assigns a siop_id.",
            )
        )

    agent_names = {
        "blueprint": pkg["blueprint"].get("agent_class_name"),
        "developer": pkg["developer"].get("agent_class_name"),
        "agentic_certificate": pkg["agentic_certificate"].get("agent_name"),
    }
    present_agents = {k: v for k, v in agent_names.items() if v}

    if len(set(present_agents.values())) > 1:
        findings.append(
            AuditFinding(
                area="cross_document_consistency",
                severity="MEDIUM",
                message=f"Agent name mismatch across documents: {present_agents}",
                recommendation="Normalize agent_class_name across Blueprint, Developer Manifest and Agentic Certificate.",
            )
        )

    company_values = [
        pkg["company"],
        pkg["blueprint"].get("company"),
        pkg["siop"].get("business_context", {}).get("company"),
    ]
    company_values = [c for c in company_values if c]

    if company_values and len(set(company_values)) > 1:
        findings.append(
            AuditFinding(
                area="cross_document_consistency",
                severity="LOW",
                message=f"Company name variations detected: {company_values}",
                recommendation="Normalize company naming for customer-facing delivery.",
            )
        )

    score = max(0.0, 1.0 - len(findings) * 0.18)
    status = "PASS" if not findings else ("WARN" if score >= 0.70 else "FAIL")

    return AuditCheck("cross_document_consistency", status, round(score, 2), findings)


def check_blueprint_runtime_coherence(pkg: dict[str, Any]) -> AuditCheck:
    findings: list[AuditFinding] = []
    blueprint = pkg["blueprint"]
    runtime = pkg["agent_runtime_text"]

    class_name = blueprint.get("agent_class_name")
    if class_name and class_name not in runtime:
        findings.append(
            AuditFinding(
                area="blueprint_runtime",
                severity="HIGH",
                message=f"Agent runtime does not contain blueprint class_name: {class_name}",
                recommendation="Regenerate agent runtime from the Architect Blueprint.",
            )
        )

    steps = blueprint.get("steps", [])
    if steps:
        step_hits = 0
        for idx, step in enumerate(steps, start=1):
            expected = f"step_{idx:02d}"
            if expected in runtime:
                step_hits += 1
        if step_hits < len(steps):
            findings.append(
                AuditFinding(
                    area="blueprint_runtime",
                    severity="MEDIUM",
                    message=f"Runtime implements {step_hits}/{len(steps)} expected step methods.",
                    recommendation="Regenerate runtime or add missing async step methods.",
                )
            )

    required_runtime_features = {
        "audit trail": ["audit", "AuditEntry"],
        "dashboard events": ["emit_dashboard_event", "dashboard"],
        "learning events": ["emit_learning_event", "learning"],
        "escalation handling": ["handle_escalation", "escalation"],
        "dry-run mode": ["dry-run", "mode"],
    }

    for label, terms in required_runtime_features.items():
        if not all(t.lower() in runtime.lower() for t in terms):
            findings.append(
                AuditFinding(
                    area="blueprint_runtime",
                    severity="MEDIUM",
                    message=f"Runtime missing or weak feature: {label}",
                    recommendation=f"Add explicit {label} support to runtime.",
                )
            )

    score = max(0.0, 1.0 - len(findings) * 0.12)
    status = "PASS" if not findings else ("WARN" if score >= 0.70 else "FAIL")

    return AuditCheck("blueprint_runtime_coherence", status, round(score, 2), findings)


def check_connectors_and_escalations(pkg: dict[str, Any]) -> AuditCheck:
    findings: list[AuditFinding] = []
    blueprint = pkg["blueprint"]
    runtime = pkg["agent_runtime_text"]

    connectors = blueprint.get("connectors", [])
    for connector in connectors:
        name = connector.get("name", "")
        conn_type = connector.get("type", "")
        env_host = connector.get("env_var_host", "")
        env_key = connector.get("env_var_key", "")
        if not env_host or not env_key:
            findings.append(
                AuditFinding(
                    area="connectors",
                    severity="MEDIUM",
                    message=f"Connector {name or conn_type} missing environment variable mapping.",
                    recommendation="Define env_var_host and env_var_key in Architect Blueprint.",
                )
            )

    if connectors and "connectors" not in runtime.lower():
        findings.append(
            AuditFinding(
                area="connectors",
                severity="HIGH",
                message="Blueprint defines connectors but runtime does not expose connector handling.",
                recommendation="Regenerate agent runtime with connector initialization.",
            )
        )

    escalations = blueprint.get("escalations", [])
    if escalations and "handle_escalation" not in runtime:
        findings.append(
            AuditFinding(
                area="escalations",
                severity="HIGH",
                message="Blueprint defines escalations but runtime does not implement handle_escalation.",
                recommendation="Regenerate runtime with escalation handling.",
            )
        )

    if not escalations:
        findings.append(
            AuditFinding(
                area="escalations",
                severity="LOW",
                message="No explicit escalation scenarios detected.",
                recommendation="Confirm low-confidence fallback escalation to process owner.",
            )
        )

    score = max(0.0, 1.0 - len(findings) * 0.14)
    status = "PASS" if not findings else ("WARN" if score >= 0.70 else "FAIL")

    return AuditCheck("connectors_and_escalations", status, round(score, 2), findings)


def check_guardian_and_agentic_certificate(pkg: dict[str, Any]) -> AuditCheck:
    findings: list[AuditFinding] = []
    guardian = pkg["guardian"]
    agentic = pkg["agentic_certificate"]

    guardian_status = guardian.get("overall_status") or guardian.get(
        "certificate", {}
    ).get("overall_status", "")
    guardian_score = guardian.get("overall_score") or guardian.get(
        "certificate", {}
    ).get("overall_score", 0)

    if isinstance(guardian_score, (int, float)) and guardian_score > 1:
        guardian_score = guardian_score / 100

    if not guardian:
        findings.append(
            AuditFinding(
                area="guardian",
                severity="CRITICAL",
                message="Guardian result missing.",
                recommendation="Run guardian_adapter.py before auditor_adapter.py.",
            )
        )
    elif str(guardian_status).upper() in ["REJECTED", "FAIL"]:
        findings.append(
            AuditFinding(
                area="guardian",
                severity="CRITICAL",
                message=f"Guardian status is blocking: {guardian_status}",
                recommendation="Resolve Guardian remediation plan before delivery.",
            )
        )
    elif str(guardian_status).upper() in ["CONDITIONAL", "WARNING"]:
        findings.append(
            AuditFinding(
                area="guardian",
                severity="MEDIUM",
                message=f"Guardian status is conditional: {guardian_status}",
                recommendation="Carry Guardian conditions into Delivery Gate.",
            )
        )

    if not agentic:
        findings.append(
            AuditFinding(
                area="agentic_certificate",
                severity="HIGH",
                message="Agentic certificate missing.",
                recommendation="Run guardian_adapter.py to generate agentic_certificate.json.",
            )
        )
    else:
        if not agentic.get("machine_compatible", False):
            findings.append(
                AuditFinding(
                    area="agentic_certificate",
                    severity="MEDIUM",
                    message="Agent is not fully Machine-compatible.",
                    recommendation="Complete learning hooks before enabling autonomous learning.",
                )
            )

    score = guardian_score if guardian_score else 0.0
    if not agentic.get("machine_compatible", False):
        score = min(score, 0.82)
    if not guardian:
        score = 0.0

    status = "PASS" if not findings else ("WARN" if score >= 0.70 else "FAIL")

    return AuditCheck(
        "guardian_and_agentic_certificate", status, round(score, 2), findings
    )


def check_delivery_readiness(pkg: dict[str, Any]) -> AuditCheck:
    findings: list[AuditFinding] = []

    required_delivery = [
        "sop",
        "integration_guide",
        "escalation_policy",
        "client_summary",
        "dashboard",
        "roi",
    ]

    for key in required_delivery:
        path = pkg["paths"][key]
        if not path.exists():
            findings.append(
                AuditFinding(
                    area="delivery_readiness",
                    severity="HIGH",
                    message=f"Missing delivery artifact: {key}",
                    recommendation=f"Generate 05_delivery/{key}.",
                )
            )
        elif path.stat().st_size < 100:
            findings.append(
                AuditFinding(
                    area="delivery_readiness",
                    severity="LOW",
                    message=f"Delivery artifact appears too small: {key}",
                    recommendation=f"Review generated content for {key}.",
                )
            )

    score = max(0.0, 1.0 - len(findings) * 0.12)
    status = "PASS" if not findings else ("WARN" if score >= 0.70 else "FAIL")

    return AuditCheck("delivery_readiness", status, round(score, 2), findings)


def check_learning_hooks(pkg: dict[str, Any]) -> AuditCheck:
    findings: list[AuditFinding] = []

    hooks = (
        pkg["blueprint"].get("learning_hooks")
        or pkg["siop"].get("learning_hooks")
        or {}
    )
    required = [
        "observation_points",
        "failure_patterns",
        "kpi_deviation_signals",
        "feedback_targets",
        "improvement_loop",
    ]

    for key in required:
        if not hooks.get(key):
            findings.append(
                AuditFinding(
                    area="learning_hooks",
                    severity="MEDIUM",
                    message=f"Missing learning hook: {key}",
                    recommendation="Complete learning hooks before connecting the agent to The Machine.",
                )
            )

    score = max(0.0, 1.0 - len(findings) * 0.16)
    status = "PASS" if not findings else ("WARN" if score >= 0.60 else "FAIL")

    return AuditCheck("learning_hooks", status, round(score, 2), findings)


def run_checks(pkg: dict[str, Any]) -> list[AuditCheck]:
    return [
        check_package_completeness(pkg),
        check_cross_document_consistency(pkg),
        check_blueprint_runtime_coherence(pkg),
        check_connectors_and_escalations(pkg),
        check_guardian_and_agentic_certificate(pkg),
        check_delivery_readiness(pkg),
        check_learning_hooks(pkg),
    ]


# ---------------------------------------------------------------------------
# DECISION ENGINE
# ---------------------------------------------------------------------------


def make_decision(
    checks: list[AuditCheck],
) -> tuple[str, bool, bool, bool, float, list[str]]:
    scores = [c.score for c in checks]
    overall_score = round(sum(scores) / len(scores), 2) if scores else 0.0

    critical_findings = [
        f for c in checks for f in c.findings if f.severity == "CRITICAL"
    ]
    high_findings = [f for c in checks for f in c.findings if f.severity == "HIGH"]
    medium_findings = [f for c in checks for f in c.findings if f.severity == "MEDIUM"]

    conditions = []
    for c in checks:
        for f in c.findings:
            if f.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                conditions.append(f"{f.area}: {f.message}")

    if critical_findings:
        return "REJECT", False, False, True, overall_score, conditions

    if overall_score >= 0.88 and not high_findings and not medium_findings:
        return "AUTO_APPROVE", True, False, False, overall_score, conditions

    if overall_score >= 0.75 and not high_findings:
        return "APPROVE_WITH_CONDITIONS", True, True, True, overall_score, conditions

    if overall_score >= 0.65:
        return "HOLD", False, True, True, overall_score, conditions

    return "REJECT", False, False, True, overall_score, conditions


# ---------------------------------------------------------------------------
# REPORTS
# ---------------------------------------------------------------------------


def render_audit_report(result: AuditorAdapterResult) -> str:
    lines = [
        "# Agentic Zero Audit Report",
        "",
        f"**Process ID:** {result.process_id}",
        f"**Audited at:** {result.audited_at}",
        f"**Decision:** {result.decision}",
        f"**Overall score:** {pct(result.overall_score)}%",
        f"**Delivery:** {result.delivery}",
        f"**Restricted:** {result.restricted}",
        f"**Escalate:** {result.escalate}",
        "",
        "## Check Summary",
        "",
    ]

    for check in result.checks:
        lines.extend(
            [
                f"### {check.name}",
                "",
                f"- Status: {check.status}",
                f"- Score: {pct(check.score)}%",
                "",
            ]
        )
        if check.findings:
            lines.append("Findings:")
            for f in check.findings:
                lines.append(f"- **{f.severity}** {f.area}: {f.message}")
                if f.recommendation:
                    lines.append(f"  - Recommendation: {f.recommendation}")
            lines.append("")

    lines.extend(
        [
            "## Conditions",
            "",
        ]
    )

    if result.conditions:
        lines.extend([f"- {c}" for c in result.conditions])
    else:
        lines.append("- No conditions.")

    lines.extend(
        [
            "",
            "## Final Note",
            "",
            "Guardian certifies safety and compliance. Auditor certifies package consistency and delivery readiness.",
            "",
            f"**Mantra:** {result.mantra}",
        ]
    )

    return "\n".join(lines)


def save_outputs(
    pkg: dict[str, Any], result: AuditorAdapterResult
) -> AuditorAdapterResult:
    audit_dir = pkg["root"] / "07_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    decision_path = audit_dir / "auditor_decision.json"
    report_path = audit_dir / "audit_report.md"
    scorecard_path = audit_dir / "audit_scorecard.json"
    findings_path = audit_dir / "qa_findings.json"

    write_json(decision_path, asdict(result))
    write_text(report_path, render_audit_report(result))

    scorecard = {
        "process_id": result.process_id,
        "overall_score": result.overall_score,
        "decision": result.decision,
        "checks": [
            {
                "name": c.name,
                "status": c.status,
                "score": c.score,
                "findings_count": len(c.findings),
            }
            for c in result.checks
        ],
    }

    findings = {
        "process_id": result.process_id,
        "findings": [asdict(f) for c in result.checks for f in c.findings],
    }

    write_json(scorecard_path, scorecard)
    write_json(findings_path, findings)

    result.outputs = {
        "auditor_decision_json": str(decision_path),
        "audit_report_md": str(report_path),
        "audit_scorecard_json": str(scorecard_path),
        "qa_findings_json": str(findings_path),
    }

    write_json(decision_path, asdict(result))
    return result


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------


def audit_essential_package(package_dir: str | Path) -> AuditorAdapterResult:
    pkg = load_package(package_dir)
    checks = run_checks(pkg)

    decision, delivery, restricted, escalate, overall_score, conditions = make_decision(
        checks
    )

    result = AuditorAdapterResult(
        process_id=pkg["process_id"],
        package_dir=str(pkg["root"]),
        audited_at=_now(),
        decision=decision,
        delivery=delivery,
        restricted=restricted,
        escalate=escalate,
        overall_score=overall_score,
        checks=checks,
        conditions=conditions,
        outputs={},
        next_step="Run delivery_gate.py",
    )

    return save_outputs(pkg, result)


def run_cli(package_dir: str):
    result = audit_essential_package(package_dir)

    print("\nAuditor Adapter complete")
    print(f"Decision: {result.decision}")
    print(f"Score:    {pct(result.overall_score)}%")
    print(f"Delivery: {result.delivery}")
    print(f"Escalate: {result.escalate}")
    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")
    print(f"\nNext: {result.next_step}")

    if result.conditions:
        print("\nConditions:")
        for c in result.conditions[:10]:
            print(f"  - {c}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Auditor Adapter")
    parser.add_argument(
        "--package-dir", required=True, help="Path to customer essential_package folder"
    )
    args = parser.parse_args()
    run_cli(args.package_dir)
