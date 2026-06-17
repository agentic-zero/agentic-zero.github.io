"""
AGENTIC ZERO — PIONEER TEAM
Agent: SIOP VALIDATOR

Role:
Validate internal SIOP contracts before Architect consumes them.

Input:
  library/siop_internal/*.json

Output:
  library/siop_validations/*.json

Core question:
  Can Architect safely build agents from this SIOP?

Statuses:
  PASS
  PASS_WITH_WARNINGS
  FAIL

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
    "logs/siop_validator_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

SIOP_VALIDATOR_CONFIG = {
    "siop_internal_path": os.getenv("SIOP_INTERNAL_PATH", "library/siop_internal"),
    "siop_validation_path": os.getenv("SIOP_VALIDATION_PATH", "library/siop_validations"),
    "min_pass_score": float(os.getenv("SIOP_MIN_PASS_SCORE", "0.85")),
    "min_warning_score": float(os.getenv("SIOP_MIN_WARNING_SCORE", "0.65")),
}


class ValidationIssue(BaseModel):
    severity: str
    section: str
    field: str
    message: str
    recommendation: str = ""


class SectionScore(BaseModel):
    section: str
    score: float
    passed: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


class SIOPValidationResult(BaseModel):
    validation_id: str
    siop_id: str
    validated_at: str
    status: str
    score: float
    architect_ready: bool
    builder_ready: bool
    blocking_issues: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)
    section_scores: list[SectionScore] = Field(default_factory=list)
    required_human_review: bool = False
    notes: str = ""
    mantra_check: str = "Does this make it feel like a living enterprise?"


def load_json(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_slug(value: str) -> str:
    value = (value or "validation").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "validation"


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_items(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def issue(severity: str, section: str, field: str, message: str, recommendation: str = "") -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        section=section,
        field=field,
        message=message,
        recommendation=recommendation,
    )


def score_from_issues(issues: list[ValidationIssue], base: float = 1.0) -> float:
    score = base
    for item in issues:
        if item.severity == "blocking":
            score -= 0.35
        elif item.severity == "warning":
            score -= 0.15
        else:
            score -= 0.05
    return max(0.0, min(1.0, round(score, 2)))


def validate_executive_summary(siop: dict[str, Any]) -> SectionScore:
    section = "executive_summary"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not has_text(data.get("process_name")):
        issues.append(issue("blocking", section, "process_name", "Process name is missing.", "Provide a clear process name."))
    if not has_text(data.get("validated_description")):
        issues.append(issue("blocking", section, "validated_description", "Validated description is missing.", "Provide a concise validated process description."))
    if not isinstance(data.get("value_baseline"), dict):
        issues.append(issue("warning", section, "value_baseline", "Value baseline is missing or invalid.", "Include volume, team size, confidence or business value baseline."))
    if float(data.get("confidence") or 0) < 0.5:
        issues.append(issue("warning", section, "confidence", "Low confidence in executive summary.", "Review AUDIT / Fast Track inputs."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_business_context(siop: dict[str, Any]) -> SectionScore:
    section = "business_context"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not has_text(data.get("sector")):
        issues.append(issue("blocking", section, "sector", "Sector is missing.", "Sector is required for compliance and variant logic."))
    if not has_text(data.get("erp")):
        issues.append(issue("warning", section, "erp", "ERP/core system is missing.", "Identify ERP or core transaction system."))
    if not has_text(str(data.get("volume", ""))):
        issues.append(issue("warning", section, "volume", "Process volume is missing.", "Add order/day, cases/month, transactions/week or equivalent."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_process_flow(siop: dict[str, Any]) -> SectionScore:
    section = "process_flow"
    steps = siop.get(section, []) or []
    issues: list[ValidationIssue] = []

    if not has_items(steps):
        issues.append(issue("blocking", section, "steps", "No process steps found.", "Provide at least one executable workflow step."))
    else:
        for idx, step in enumerate(steps, start=1):
            if not has_text(step.get("name")):
                issues.append(issue("blocking", section, f"step_{idx}.name", "Step name is missing.", "Each step must have a clear name."))
            if not has_items(step.get("inputs", [])):
                issues.append(issue("warning", section, f"step_{idx}.inputs", "Step inputs are missing.", "Define the input data/object for this step."))
            if not has_items(step.get("outputs", [])):
                issues.append(issue("warning", section, f"step_{idx}.outputs", "Step outputs are missing.", "Define the output generated by this step."))
            if not has_text(step.get("system", "")):
                issues.append(issue("warning", section, f"step_{idx}.system", "Step system is missing.", "Map the step to ERP, email, WMS, TMS, API or other system."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_data_requirements(siop: dict[str, Any]) -> SectionScore:
    section = "data_requirements"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not has_items(data.get("input_objects", [])):
        issues.append(issue("blocking", section, "input_objects", "No input data objects defined.", "Define objects such as customer, order, inventory, invoice, shipment."))
    if not has_items(data.get("output_objects", [])):
        issues.append(issue("warning", section, "output_objects", "No output data objects defined.", "Define the outputs produced by the process."))
    if not has_items(data.get("master_data", [])) and not has_items(data.get("transactional_data", [])):
        issues.append(issue("warning", section, "data_classification", "Data is not classified as master/transactional.", "Classify relevant data objects for agent data model."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_business_rules(siop: dict[str, Any]) -> SectionScore:
    section = "business_rules"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not has_items(data.get("decision_rules", [])):
        issues.append(issue("blocking", section, "decision_rules", "No decision rules defined.", "Add business rules that drive autonomous decision logic."))
    if not has_items(data.get("exception_rules", [])):
        issues.append(issue("warning", section, "exception_rules", "No exception rules defined.", "Map known exceptions to handling logic."))
    if data.get("missing_rules"):
        issues.append(issue("warning", section, "missing_rules", "Some business rules are explicitly missing.", "Resolve missing rules before build stage if critical."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_compliance(siop: dict[str, Any]) -> SectionScore:
    section = "compliance"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not has_items(data.get("guardian_requirements", [])):
        issues.append(issue("blocking", section, "guardian_requirements", "Guardian requirements are missing.", "Define Agentic Shield / Guardian controls."))
    if data.get("regulated_process") and not has_items(data.get("applicable_frameworks", [])):
        issues.append(issue("blocking", section, "applicable_frameworks", "Regulated process without frameworks.", "Add applicable frameworks such as GxP, ITAR, HACCP, ISO."))
    if not data.get("audit_trail_required", False):
        issues.append(issue("warning", section, "audit_trail_required", "Audit trail is not required.", "Agentic processes should normally enforce traceability."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_autonomy_design(siop: dict[str, Any]) -> SectionScore:
    section = "autonomy_design"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not has_items(data.get("autonomous_actions", [])):
        issues.append(issue("blocking", section, "autonomous_actions", "No autonomous actions defined.", "Define at least read/validate/draft or executable actions."))
    if not has_items(data.get("escalation_paths", [])):
        issues.append(issue("blocking", section, "escalation_paths", "Escalation paths are missing.", "Define when and where agents escalate."))
    if not has_items(data.get("agentic_shield_requirements", [])):
        issues.append(issue("blocking", section, "agentic_shield_requirements", "Agentic Shield requirements are missing.", "Define thresholds, audit trails, fail-safes and accountability controls."))
    thresholds = data.get("thresholds", {})
    if not isinstance(thresholds, dict):
        issues.append(issue("warning", section, "thresholds", "Thresholds field is invalid.", "Provide threshold dictionary even if empty."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_acceptance_criteria(siop: dict[str, Any]) -> SectionScore:
    section = "acceptance_criteria"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not has_items(data.get("kpis", [])):
        issues.append(issue("blocking", section, "kpis", "KPIs are missing.", "Define measurable acceptance KPIs."))
    if not has_items(data.get("test_scenarios", [])):
        issues.append(issue("warning", section, "test_scenarios", "Test scenarios are missing.", "Define happy path, exception and escalation tests."))
    if not has_items(data.get("pass_fail_criteria", [])):
        issues.append(issue("blocking", section, "pass_fail_criteria", "Pass/fail criteria missing.", "Define certification criteria before build."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.65, issues=issues)


def validate_learning_hooks(siop: dict[str, Any]) -> SectionScore:
    section = "learning_hooks"
    data = siop.get(section, {}) or {}
    issues: list[ValidationIssue] = []

    if not data.get("enabled", False):
        issues.append(issue("info", section, "enabled", "Learning hooks are not enabled.", "Enable learning hooks to support continuous improvement."))
    if not has_items(data.get("observation_points", [])):
        issues.append(issue("warning", section, "observation_points", "No observation points defined.", "Define what the enterprise should observe during operation."))
    if not has_items(data.get("feedback_targets", [])):
        issues.append(issue("warning", section, "feedback_targets", "No feedback targets defined.", "Define what can be improved after operation."))

    score = score_from_issues(issues)
    return SectionScore(section=section, score=score, passed=score >= 0.60, issues=issues)


def validate_siop(siop: dict[str, Any]) -> SIOPValidationResult:
    siop_id = siop.get("siop_id", "UNKNOWN-SIOP")

    section_scores = [
        validate_executive_summary(siop),
        validate_business_context(siop),
        validate_process_flow(siop),
        validate_data_requirements(siop),
        validate_business_rules(siop),
        validate_compliance(siop),
        validate_autonomy_design(siop),
        validate_acceptance_criteria(siop),
        validate_learning_hooks(siop),
    ]

    all_issues = [item for section in section_scores for item in section.issues]
    blocking = [i for i in all_issues if i.severity == "blocking"]
    warnings = [i for i in all_issues if i.severity == "warning"]

    weighted_sections = [s for s in section_scores if s.section != "learning_hooks"]
    score = round(sum(s.score for s in weighted_sections) / len(weighted_sections), 2)

    required_human_review = bool(
        siop.get("compliance", {}).get("human_review_required")
        or siop.get("compliance", {}).get("regulated_process")
    )

    if blocking or score < SIOP_VALIDATOR_CONFIG["min_warning_score"]:
        status = "FAIL"
        architect_ready = False
        builder_ready = False
    elif warnings or score < SIOP_VALIDATOR_CONFIG["min_pass_score"]:
        status = "PASS_WITH_WARNINGS"
        architect_ready = True
        builder_ready = False
    else:
        status = "PASS"
        architect_ready = True
        builder_ready = True

    validation_id = f"VAL-{safe_slug(siop_id)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return SIOPValidationResult(
        validation_id=validation_id,
        siop_id=siop_id,
        validated_at=datetime.now().isoformat(),
        status=status,
        score=score,
        architect_ready=architect_ready,
        builder_ready=builder_ready,
        blocking_issues=blocking,
        warnings=warnings,
        section_scores=section_scores,
        required_human_review=required_human_review,
        notes=(
            "SIOP can proceed to Architect."
            if architect_ready
            else "SIOP cannot proceed to Architect until blocking issues are resolved."
        ),
    )


def save_validation(result: SIOPValidationResult) -> Path:
    out_dir = Path(SIOP_VALIDATOR_CONFIG["siop_validation_path"])
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = out_dir / f"{result.validation_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(f"SIOP validation saved: {filename}")
    return filename


def validate_siop_from_file(siop_path: str | Path) -> SIOPValidationResult:
    logger.info(f"Validating SIOP: {siop_path}")
    siop = load_json(siop_path)
    result = validate_siop(siop)
    save_validation(result)

    logger.success(
        f"SIOP validation complete | status={result.status} | score={result.score} | architect_ready={result.architect_ready}"
    )
    return result


def run_siop_validator(siop_path: str):
    result = validate_siop_from_file(siop_path)

    print("\n✅ SIOP Validator complete")
    print(f"   SIOP ID: {result.siop_id}")
    print(f"   Status: {result.status}")
    print(f"   Score: {result.score}")
    print(f"   Architect ready: {result.architect_ready}")
    print(f"   Builder ready: {result.builder_ready}")
    print(f"   Blocking issues: {len(result.blocking_issues)}")
    print(f"   Warnings: {len(result.warnings)}")

    if result.blocking_issues:
        print("\n❌ Blocking issues:")
        for item in result.blocking_issues:
            print(f"   → {item.section}.{item.field}: {item.message}")

    if result.warnings:
        print("\n⚠️ Warnings:")
        for item in result.warnings[:10]:
            print(f"   → {item.section}.{item.field}: {item.message}")

    if result.architect_ready:
        print("\nNext:")
        print("   Proceed to Architect / Agent Developer route.")
    else:
        print("\nNext:")
        print("   Resolve blocking issues or rerun Fast Track / Advanced AUDIT.")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero — SIOP Validator")
    parser.add_argument("--siop", required=True, help="Path to internal SIOP JSON")
    args = parser.parse_args()

    run_siop_validator(args.siop)
