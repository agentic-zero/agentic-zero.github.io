"""
AGENTIC ZERO - PIONEER TEAM
Delivery Gate v1.0

Role:
  Final release gate for customer Essential packages.

Why this exists:
  Guardian certifies safety/compliance.
  Auditor certifies package consistency/delivery readiness.
  Delivery Gate decides whether the package can be handed over to the customer.

Recommended location:
  pioneer_team/delivery/delivery_gate.py

Input:
  --package-dir clients/{client}/{process}/essential_package

Expected inputs:
  delivery_manifest.json
  06_compliance/guardian_result.json
  06_compliance/guardian_certificate.txt
  06_compliance/agentic_certificate.json
  07_audit/auditor_decision.json
  07_audit/audit_report.md

Output:
  08_delivery_gate/
    delivery_gate_decision.json
    delivery_release_note.md
    customer_handover_checklist.md
    final_delivery_status.json

Final statuses:
  DELIVERABLE
  DELIVERABLE_WITH_CONDITIONS
  BLOCKED_MISSING_INFORMATION
  BLOCKED_COMPLIANCE
  BLOCKED_AUDIT_REJECTED
  BLOCKED_BUILD_FAILURE

Next:
  Customer delivery / Master Orchestrator / The Machine

Mantra:
  Does this make it feel like a living enterprise?
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------


@dataclass
class DeliveryGateFinding:
    area: str
    severity: str  # INFO | LOW | MEDIUM | HIGH | CRITICAL
    message: str
    action_required: str = ""


@dataclass
class DeliveryGateDecision:
    package_dir: str
    process_id: str
    company: str
    agent_name: str
    decided_at: str
    final_status: str
    release_allowed: bool
    restricted_release: bool
    human_signoff_required: bool
    score: float
    findings: list[DeliveryGateFinding]
    required_actions: list[str]
    outputs: dict[str, str]
    next_step: str
    commercial_documents: list[str] = field(default_factory=list)
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


def normalize_score(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, str):
        value = value.replace("%", "").strip()
        try:
            value = float(value)
        except Exception:
            return 0.0
    if isinstance(value, (int, float)):
        if value > 1:
            return round(float(value) / 100, 2)
        return round(float(value), 2)
    return 0.0


# ---------------------------------------------------------------------------
# PACKAGE LOADER
# ---------------------------------------------------------------------------


def load_package(package_dir: str | Path) -> dict[str, Any]:
    root = Path(package_dir)

    paths = {
        "delivery_manifest": root / "delivery_manifest.json",
        "guardian_result": root / "06_compliance" / "guardian_result.json",
        "guardian_certificate": root / "06_compliance" / "guardian_certificate.txt",
        "agentic_certificate": root / "06_compliance" / "agentic_certificate.json",
        "auditor_decision": root / "07_audit" / "auditor_decision.json",
        "audit_report": root / "07_audit" / "audit_report.md",
        "audit_scorecard": root / "07_audit" / "audit_scorecard.json",
        "qa_findings": root / "07_audit" / "qa_findings.json",
        "functional": root / "01_functional_analysis" / "functional_analysis.json",
        "siop": root / "02_siop" / "siop_internal.json",
        "blueprint": root / "03_blueprint" / "architect_blueprint.json",
        "agent_runtime": root / "04_agent" / "agent_runtime.py",
        "sop": root / "05_delivery" / "sop.md",
        "integration_guide": root / "05_delivery" / "integration_guide.md",
        "escalation_policy": root / "05_delivery" / "escalation_policy.md",
        "client_summary": root / "05_delivery" / "client_executive_summary.md",
        "dashboard": root / "05_delivery" / "dashboard.html",
        "roi": root / "05_delivery" / "roi_calculator.html",
    }

    delivery_manifest = read_json(paths["delivery_manifest"])
    guardian = read_json(paths["guardian_result"])
    agentic = read_json(paths["agentic_certificate"])
    auditor = read_json(paths["auditor_decision"])
    blueprint = read_json(paths["blueprint"])
    siop = read_json(paths["siop"])
    functional = read_json(paths["functional"])

    process_id = (
        auditor.get("process_id")
        or guardian.get("process_id")
        or blueprint.get("process_id")
        or siop.get("process_id")
        or siop.get("siop_id")
        or delivery_manifest.get("process_id")
        or "ESSENTIAL-PROCESS"
    )

    company = (
        delivery_manifest.get("company")
        or blueprint.get("company")
        or siop.get("business_context", {}).get("company")
        or functional.get("business_context", {}).get("company")
        or "Customer"
    )

    agent_name = (
        delivery_manifest.get("agent_class_name")
        or blueprint.get("agent_class_name")
        or agentic.get("agent_name")
        or "EssentialAgent"
    )

    commercial_dir = root / "11_commercial"
    commercial_documents = []
    if commercial_dir.exists():
        for f in sorted(commercial_dir.iterdir()):
            if f.is_file():
                commercial_documents.append(f.name)

    return {
        "root": root,
        "paths": paths,
        "delivery_manifest": delivery_manifest,
        "guardian": guardian,
        "agentic": agentic,
        "auditor": auditor,
        "blueprint": blueprint,
        "siop": siop,
        "functional": functional,
        "process_id": process_id,
        "company": company,
        "agent_name": agent_name,
        "commercial_documents": commercial_documents,
    }


# ---------------------------------------------------------------------------
# CHECKS
# ---------------------------------------------------------------------------


def check_required_release_artifacts(pkg: dict[str, Any]) -> list[DeliveryGateFinding]:
    required = [
        "delivery_manifest",
        "guardian_result",
        "guardian_certificate",
        "agentic_certificate",
        "auditor_decision",
        "audit_report",
        "agent_runtime",
        "sop",
        "integration_guide",
        "escalation_policy",
        "client_summary",
        "dashboard",
        "roi",
    ]

    findings = []
    for key in required:
        path = pkg["paths"][key]
        if not path.exists():
            severity = (
                "CRITICAL"
                if key in ["guardian_result", "auditor_decision", "agent_runtime"]
                else "HIGH"
            )
            findings.append(
                DeliveryGateFinding(
                    area="required_release_artifacts",
                    severity=severity,
                    message=f"Missing required release artifact: {key}",
                    action_required=f"Generate {key} before customer delivery.",
                )
            )
    return findings


def check_guardian_release(pkg: dict[str, Any]) -> list[DeliveryGateFinding]:
    guardian = pkg["guardian"]
    findings = []

    if not guardian:
        return [
            DeliveryGateFinding(
                area="guardian",
                severity="CRITICAL",
                message="Guardian result missing.",
                action_required="Run guardian_adapter.py before Delivery Gate.",
            )
        ]

    status = str(
        guardian.get("overall_status")
        or guardian.get("certificate", {}).get("overall_status")
        or ""
    ).upper()

    score = normalize_score(
        guardian.get("overall_score")
        or guardian.get("certificate", {}).get("overall_score")
    )

    if status in ["REJECTED", "FAIL", "FAILED"]:
        findings.append(
            DeliveryGateFinding(
                area="guardian",
                severity="CRITICAL",
                message=f"Guardian rejected package: {status}.",
                action_required="Resolve Guardian remediation plan before delivery.",
            )
        )

    elif status in ["CONDITIONAL", "WARNING"]:
        findings.append(
            DeliveryGateFinding(
                area="guardian",
                severity="MEDIUM",
                message=f"Guardian approval is conditional. Score {pct(score)}%.",
                action_required="Carry Guardian conditions into handover checklist.",
            )
        )

    elif status not in ["CERTIFIED", "APPROVED", "AUTO_APPROVE"]:
        findings.append(
            DeliveryGateFinding(
                area="guardian",
                severity="HIGH",
                message=f"Unknown Guardian status: {status or 'missing'}.",
                action_required="Confirm Guardian result before delivery.",
            )
        )

    return findings


def check_auditor_release(pkg: dict[str, Any]) -> list[DeliveryGateFinding]:
    auditor = pkg["auditor"]
    findings = []

    if not auditor:
        return [
            DeliveryGateFinding(
                area="auditor",
                severity="CRITICAL",
                message="Auditor decision missing.",
                action_required="Run auditor_adapter.py before Delivery Gate.",
            )
        ]

    decision = str(auditor.get("decision") or "").upper()
    delivery = bool(auditor.get("delivery", False))
    score = normalize_score(auditor.get("overall_score"))

    if decision in ["REJECT"]:
        findings.append(
            DeliveryGateFinding(
                area="auditor",
                severity="CRITICAL",
                message=f"Auditor rejected package. Score {pct(score)}%.",
                action_required="Resolve audit findings before release.",
            )
        )

    elif decision in ["HOLD"]:
        findings.append(
            DeliveryGateFinding(
                area="auditor",
                severity="HIGH",
                message=f"Auditor placed package on HOLD. Score {pct(score)}%.",
                action_required="Resolve audit HOLD conditions before release.",
            )
        )

    elif decision == "APPROVE_WITH_CONDITIONS":
        findings.append(
            DeliveryGateFinding(
                area="auditor",
                severity="MEDIUM",
                message=f"Auditor approved with conditions. Score {pct(score)}%.",
                action_required="Include all audit conditions in customer handover.",
            )
        )

    elif decision not in ["AUTO_APPROVE", "APPROVE_WITH_CONDITIONS"]:
        findings.append(
            DeliveryGateFinding(
                area="auditor",
                severity="HIGH",
                message=f"Unknown Auditor decision: {decision or 'missing'}.",
                action_required="Confirm Auditor result before release.",
            )
        )

    if not delivery:
        findings.append(
            DeliveryGateFinding(
                area="auditor",
                severity="HIGH",
                message="Auditor delivery flag is False.",
                action_required="Delivery is blocked until auditor delivery flag is True.",
            )
        )

    return findings


def check_agentic_release(pkg: dict[str, Any]) -> list[DeliveryGateFinding]:
    agentic = pkg["agentic"]
    findings = []

    if not agentic:
        return [
            DeliveryGateFinding(
                area="agentic_certificate",
                severity="HIGH",
                message="Agentic certificate missing.",
                action_required="Run guardian_adapter.py to generate agentic_certificate.json.",
            )
        ]

    if not agentic.get("machine_compatible", False):
        findings.append(
            DeliveryGateFinding(
                area="agentic_certificate",
                severity="MEDIUM",
                message="Agent is not fully compatible with The Machine learning layer.",
                action_required="Delivery can proceed, but autonomous learning activation must remain disabled until hooks are complete.",
            )
        )

    if not agentic.get("learning_ready", False):
        findings.append(
            DeliveryGateFinding(
                area="agentic_certificate",
                severity="MEDIUM",
                message="Learning readiness is incomplete.",
                action_required="Complete observation points and feedback targets before connecting to The Machine.",
            )
        )

    return findings


def check_customer_handover(pkg: dict[str, Any]) -> list[DeliveryGateFinding]:
    findings = []

    # Customer handover minimum
    minimum_docs = {
        "client_summary": "Client executive summary missing.",
        "integration_guide": "Integration guide missing.",
        "escalation_policy": "Escalation policy missing.",
        "sop": "SOP missing.",
        "roi": "ROI calculator missing.",
        "dashboard": "Dashboard missing.",
    }

    for key, message in minimum_docs.items():
        path = pkg["paths"][key]
        if not path.exists():
            findings.append(
                DeliveryGateFinding(
                    area="customer_handover",
                    severity="HIGH",
                    message=message,
                    action_required=f"Generate {key} before client handover.",
                )
            )
        elif path.stat().st_size < 100:
            findings.append(
                DeliveryGateFinding(
                    area="customer_handover",
                    severity="LOW",
                    message=f"{key} exists but appears too small.",
                    action_required=f"Review {key} content before delivery.",
                )
            )

    return findings


def run_checks(pkg: dict[str, Any]) -> list[DeliveryGateFinding]:
    findings = []
    findings.extend(check_required_release_artifacts(pkg))
    findings.extend(check_guardian_release(pkg))
    findings.extend(check_auditor_release(pkg))
    findings.extend(check_agentic_release(pkg))
    findings.extend(check_customer_handover(pkg))
    return findings


# ---------------------------------------------------------------------------
# DECISION
# ---------------------------------------------------------------------------


def decide_release(
    pkg: dict[str, Any], findings: list[DeliveryGateFinding]
) -> tuple[str, bool, bool, bool, float, list[str]]:
    critical = [f for f in findings if f.severity == "CRITICAL"]
    high = [f for f in findings if f.severity == "HIGH"]
    medium = [f for f in findings if f.severity == "MEDIUM"]

    guardian_score = normalize_score(
        pkg["guardian"].get("overall_score")
        or pkg["guardian"].get("certificate", {}).get("overall_score")
    )
    auditor_score = normalize_score(pkg["auditor"].get("overall_score"))

    score_values = [s for s in [guardian_score, auditor_score] if s > 0]
    base_score = sum(score_values) / len(score_values) if score_values else 0.0

    penalty = len(critical) * 0.40 + len(high) * 0.15 + len(medium) * 0.06
    score = max(0.0, round(base_score - penalty, 2))

    required_actions = [
        f"{f.area}: {f.action_required}" for f in findings if f.action_required
    ]

    if critical:
        return "BLOCKED_COMPLIANCE", False, False, True, score, required_actions

    if any(f.area == "auditor" and f.severity == "HIGH" for f in findings):
        return "BLOCKED_AUDIT_REJECTED", False, False, True, score, required_actions

    if high:
        return (
            "BLOCKED_MISSING_INFORMATION",
            False,
            False,
            True,
            score,
            required_actions,
        )

    if medium:
        return "DELIVERABLE_WITH_CONDITIONS", True, True, True, score, required_actions

    return "DELIVERABLE", True, False, False, score, required_actions


# ---------------------------------------------------------------------------
# OUTPUTS
# ---------------------------------------------------------------------------


def render_release_note(result: DeliveryGateDecision) -> str:
    lines = [
        "# Agentic Zero Essential Package - Delivery Release Note",
        "",
        f"**Company:** {result.company}",
        f"**Process ID:** {result.process_id}",
        f"**Agent:** {result.agent_name}",
        f"**Decision date:** {result.decided_at}",
        f"**Final status:** {result.final_status}",
        f"**Release allowed:** {result.release_allowed}",
        f"**Restricted release:** {result.restricted_release}",
        f"**Human signoff required:** {result.human_signoff_required}",
        f"**Release score:** {pct(result.score)}%",
        "",
        "## Decision Summary",
        "",
    ]

    if result.release_allowed:
        if result.restricted_release:
            lines.append(
                "The package can be delivered with conditions. Conditions must be communicated before client handover."
            )
        else:
            lines.append("The package is approved for customer delivery.")
    else:
        lines.append(
            "The package is blocked and cannot be delivered until required actions are completed."
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
        ]
    )

    if result.findings:
        for f in result.findings:
            lines.append(f"- **{f.severity}** {f.area}: {f.message}")
    else:
        lines.append("- No findings.")

    lines.extend(
        [
            "",
            "## Required Actions",
            "",
        ]
    )

    if result.required_actions:
        for action in result.required_actions:
            lines.append(f"- {action}")
    else:
        lines.append("- No required actions.")

    lines.extend(
        [
            "",
            "## Final Note",
            "",
            "Guardian certifies safety and compliance. Auditor certifies consistency and readiness. Delivery Gate authorizes customer release.",
            "",
            f"**Mantra:** {result.mantra}",
        ]
    )

    return "\n".join(lines)


def render_handover_checklist(result: DeliveryGateDecision) -> str:
    checks = [
        "Functional Analysis reviewed",
        "SIOP Internal validated",
        "Architect Blueprint generated",
        "Agent Runtime generated",
        "Dry-run mode available",
        "SOP included",
        "Integration Guide included",
        "Escalation Policy included",
        "Dashboard included",
        "ROI Calculator included",
        "Guardian Certificate included",
        "Agentic Certificate included",
        "Auditor Decision included",
        "Delivery Gate release note included",
        "Conditions communicated to client",
        "Human signoff completed if required",
    ]

    lines = [
        "# Customer Handover Checklist",
        "",
        f"**Company:** {result.company}",
        f"**Process ID:** {result.process_id}",
        f"**Agent:** {result.agent_name}",
        "",
    ]

    for item in checks:
        if result.final_status == "DELIVERABLE" and "Conditions" in item:
            mark = "[ ]"
        else:
            mark = "[ ]"
        lines.append(f"- {mark} {item}")

    if result.commercial_documents:
        lines.extend(["", "## Commercial Documents", ""])
        for doc in result.commercial_documents:
            lines.append(f"- [ ] {doc} -- `11_commercial/{doc}`")

    lines.extend(
        [
            "",
            "## Release Status",
            "",
            f"- Final status: {result.final_status}",
            f"- Release allowed: {result.release_allowed}",
            f"- Restricted release: {result.restricted_release}",
            f"- Human signoff required: {result.human_signoff_required}",
        ]
    )

    return "\n".join(lines)


def save_outputs(
    pkg: dict[str, Any], result: DeliveryGateDecision
) -> DeliveryGateDecision:
    out_dir = pkg["root"] / "08_delivery_gate"
    out_dir.mkdir(parents=True, exist_ok=True)

    decision_path = out_dir / "delivery_gate_decision.json"
    release_note_path = out_dir / "delivery_release_note.md"
    checklist_path = out_dir / "customer_handover_checklist.md"
    final_status_path = out_dir / "final_delivery_status.json"

    result.outputs = {
        "delivery_gate_decision_json": str(decision_path),
        "delivery_release_note_md": str(release_note_path),
        "customer_handover_checklist_md": str(checklist_path),
        "final_delivery_status_json": str(final_status_path),
    }

    write_json(decision_path, asdict(result))
    write_text(release_note_path, render_release_note(result))
    write_text(checklist_path, render_handover_checklist(result))
    write_json(
        final_status_path,
        {
            "process_id": result.process_id,
            "company": result.company,
            "agent_name": result.agent_name,
            "final_status": result.final_status,
            "release_allowed": result.release_allowed,
            "restricted_release": result.restricted_release,
            "human_signoff_required": result.human_signoff_required,
            "score": result.score,
            "decided_at": result.decided_at,
            "next_step": result.next_step,
        },
    )

    write_json(decision_path, asdict(result))
    return result


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------


def run_delivery_gate(package_dir: str | Path) -> DeliveryGateDecision:
    pkg = load_package(package_dir)
    findings = run_checks(pkg)
    (
        final_status,
        release_allowed,
        restricted_release,
        human_signoff_required,
        score,
        required_actions,
    ) = decide_release(pkg, findings)

    result = DeliveryGateDecision(
        package_dir=str(pkg["root"]),
        process_id=pkg["process_id"],
        company=pkg["company"],
        agent_name=pkg["agent_name"],
        decided_at=_now(),
        final_status=final_status,
        release_allowed=release_allowed,
        restricted_release=restricted_release,
        human_signoff_required=human_signoff_required,
        score=score,
        findings=findings,
        required_actions=required_actions,
        outputs={},
        next_step="Customer handover"
        if release_allowed
        else "Resolve required actions and re-run Delivery Gate",
        commercial_documents=pkg.get("commercial_documents", []),
    )

    return save_outputs(pkg, result)


def run_cli(package_dir: str):
    result = run_delivery_gate(package_dir)

    print("\nDelivery Gate complete")
    print(f"Status:   {result.final_status}")
    print(f"Score:    {pct(result.score)}%")
    print(f"Release:  {result.release_allowed}")
    print(f"Restrict: {result.restricted_release}")
    print(f"Signoff:  {result.human_signoff_required}")

    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")

    if result.required_actions:
        print("\nRequired actions:")
        for action in result.required_actions[:10]:
            print(f"  - {action}")

    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Delivery Gate")
    parser.add_argument(
        "--package-dir", required=True, help="Path to customer essential_package folder"
    )
    args = parser.parse_args()
    run_cli(args.package_dir)
