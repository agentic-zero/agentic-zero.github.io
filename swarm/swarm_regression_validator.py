# swarm/swarm_regression_validator.py

"""
AGENTIC ZERO - SWARM
Swarm Regression Validator v1.0

Role:
  This is what Claude's old swarm_generator.py became, per the agreed
  decision in SWARM_ARCHITECTURE_v1.md section 9.4: that module used to
  WRITE siop_internal.json / organism_blueprint_seed.json from a
  swarm_coordination_*.json's organisms[] array - the exact same
  artifact GPT's swarm_splitter.py already produces (from Level2SIOPs,
  a richer upstream source). Two producers of the same artifact is
  exactly the kind of collision this project closed for event_catalog.json
  earlier - so Claude's generator was retired from production.

  Its real value was never the generation itself - it was the
  byte-for-byte fidelity check that proved the derived schema matched
  what's actually deployed in production (distribuciones_norte, 4
  organisms verified). This module keeps that value and drops the
  redundant production role: it NEVER writes to 10_swarm/organisms/ -
  it only reads what GPT's pipeline already produced and reports on it.

Two independent checks, neither requires the other:

  1. STRUCTURAL VALIDATION (works on any organism, no golden fixture
     needed) - confirms every organism GPT's swarm_splitter.py produced
     has the fields every downstream module already depends on:
     observation_points (or observer.py can never ground episodes for
     it), autonomy_design's three buckets (or policy_engine.py silently
     falls back to swarm-wide defaults), business_rules, etc. This is
     the check that runs for ANY client, including ones with no golden
     reference yet - it catches "GPT's pipeline silently regressed and
     stopped including learning_hooks" even on a brand-new client nobody
     has a baseline for.

  2. GOLDEN FIXTURE COMPARISON (optional, requires a known-good
     snapshot) - field-by-field diff against a previously-verified
     organism (e.g. distribuciones_norte's DEMAND_PLANNING,
     SUPPLY_PLANNING, FINANCE_RECONCILIATION, QUALITY_MANAGEMENT - the 4
     verified byte-for-byte weeks ago). Use this to catch "GPT's
     pipeline changed the output for an organism we already know is
     correct" - a true regression, not just a missing-field defect.

Input:
  <client_root>/10_swarm/organisms/<SLUG>/{siop_internal.json, organism_blueprint_seed.json}
  (the REAL output of GPT's swarm_splitter.py pipeline - this module
  never materializes anything itself)

  Optional --golden-dir: a directory with the same SLUG subfolders,
  holding known-good siop_internal.json/organism_blueprint_seed.json to
  diff against.

Output:
  <client_root>/10_swarm/regression_report.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# Fields every downstream module already depends on existing and being
# well-formed - confirmed by reading the real consumers, not assumed:
#   - learning_hooks.observation_points: observer.py grounds episodes
#     against this; empty means this organism can never be grounded.
#   - autonomy_design's three buckets: policy_engine.py matches against
#     these; missing means swarm-wide defaults silently apply instead
#     of organism-specific thresholds.
#   - business_rules: compliance_engine.py parses these for REJECT/
#     ESCALATE triggers; empty means this organism has zero compliance
#     enforcement.
REQUIRED_SIOP_FIELDS = [
    "siop_id", "organism", "agent_type", "domain", "purpose",
    "executive_summary", "business_context", "process_flow",
    "data_requirements", "business_rules", "compliance",
    "autonomy_design", "acceptance_criteria", "learning_hooks",
]

REQUIRED_AUTONOMY_KEYS = ["autonomous_actions", "approval_required", "always_human"]
REQUIRED_LEARNING_KEYS = ["observation_points"]

REQUIRED_BLUEPRINT_SEED_FIELDS = [
    "organism_id", "organism_name", "agent_type", "domain", "purpose",
    "inputs", "outputs", "dependencies", "autonomy_design",
    "learning_hooks", "blueprint_requirements",
]


@dataclass
class Issue:
    severity: str  # ERROR or WARNING
    organism: str
    check: str
    message: str


@dataclass
class OrganismReport:
    organism_slug: str
    structural_valid: bool
    golden_compared: bool
    golden_match: Optional[bool]
    issues: list[Issue]


@dataclass
class RegressionReport:
    checked_at: str
    client_root: str
    golden_dir: Optional[str]
    organisms_checked: int
    structural_errors: int
    golden_mismatches: int
    organisms: list[OrganismReport]


def read_json(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_structure(
    organism_slug: str, siop: Optional[dict[str, Any]], blueprint_seed: Optional[dict[str, Any]]
) -> list[Issue]:
    issues: list[Issue] = []

    if siop is None:
        issues.append(Issue("ERROR", organism_slug, "siop_internal_missing", "siop_internal.json not found or unreadable."))
    else:
        for field_name in REQUIRED_SIOP_FIELDS:
            if field_name not in siop:
                issues.append(Issue("ERROR", organism_slug, "siop_missing_field", f"siop_internal.json missing required field '{field_name}'."))

        learning_hooks = siop.get("learning_hooks", {})
        observation_points = learning_hooks.get("observation_points", [])
        if not observation_points:
            issues.append(Issue(
                "ERROR", organism_slug, "no_observation_points",
                "learning_hooks.observation_points is empty - observer.py can never ground episodes for this organism.",
            ))

        autonomy = siop.get("autonomy_design", {})
        for key in REQUIRED_AUTONOMY_KEYS:
            if key not in autonomy:
                issues.append(Issue(
                    "WARNING", organism_slug, "autonomy_design_incomplete",
                    f"autonomy_design missing '{key}' - policy_engine.py will fall back to swarm-wide defaults for this category.",
                ))

        business_rules = siop.get("business_rules", [])
        if not business_rules:
            issues.append(Issue(
                "WARNING", organism_slug, "no_business_rules",
                "business_rules is empty - compliance_engine.py has nothing to enforce for this organism.",
            ))

    if blueprint_seed is None:
        issues.append(Issue("ERROR", organism_slug, "blueprint_seed_missing", "organism_blueprint_seed.json not found or unreadable."))
    else:
        for field_name in REQUIRED_BLUEPRINT_SEED_FIELDS:
            if field_name not in blueprint_seed:
                issues.append(Issue("ERROR", organism_slug, "blueprint_seed_missing_field", f"organism_blueprint_seed.json missing required field '{field_name}'."))

    return issues


def diff_against_golden(
    organism_slug: str, actual: dict[str, Any], golden: dict[str, Any], file_label: str
) -> list[Issue]:
    """
    Field-by-field comparison against a known-good snapshot. Reports
    every top-level field that differs - not a full deep diff (which
    would be noisy for nested timestamps/ids that are expected to
    differ), but enough to catch a real regression: a field present in
    the golden reference that vanished, changed type, or changed value
    in a way that matters (business_rules, autonomy_design, process_flow
    content - the fields every downstream module actually reads).
    """
    issues: list[Issue] = []

    # Fields safe to ignore in the diff - identifiers/timestamps that
    # are EXPECTED to differ between any two generations, not a sign of
    # regression.
    ignore_fields = {"siop_id", "process_id", "organism_id"}

    golden_keys = set(golden.keys()) - ignore_fields
    actual_keys = set(actual.keys()) - ignore_fields

    missing = golden_keys - actual_keys
    for field_name in sorted(missing):
        issues.append(Issue(
            "ERROR", organism_slug, "golden_field_missing",
            f"{file_label}: field '{field_name}' present in golden reference but missing in actual output - regression.",
        ))

    for field_name in sorted(golden_keys & actual_keys):
        if golden[field_name] != actual[field_name]:
            issues.append(Issue(
                "WARNING", organism_slug, "golden_field_changed",
                f"{file_label}: field '{field_name}' differs from golden reference. "
                f"golden={json.dumps(golden[field_name], ensure_ascii=False)[:120]} "
                f"actual={json.dumps(actual[field_name], ensure_ascii=False)[:120]}",
            ))

    return issues


def validate_client_organisms(
    client_root: str | Path, golden_dir: Optional[str | Path] = None
) -> RegressionReport:
    client_root = Path(client_root)
    organisms_dir = client_root / "10_swarm" / "organisms"
    golden_dir = Path(golden_dir) if golden_dir else None

    organism_reports: list[OrganismReport] = []

    if not organisms_dir.exists():
        return RegressionReport(
            checked_at=now(),
            client_root=str(client_root),
            golden_dir=str(golden_dir) if golden_dir else None,
            organisms_checked=0,
            structural_errors=0,
            golden_mismatches=0,
            organisms=[],
        )

    for organism_path in sorted(organisms_dir.iterdir()):
        if not organism_path.is_dir():
            continue

        slug = organism_path.name
        siop = read_json(organism_path / "siop_internal.json")
        blueprint_seed = read_json(organism_path / "organism_blueprint_seed.json")

        issues = validate_structure(slug, siop, blueprint_seed)
        structural_valid = not any(i.severity == "ERROR" for i in issues)

        golden_compared = False
        golden_match: Optional[bool] = None

        if golden_dir:
            golden_organism_path = golden_dir / slug
            golden_siop = read_json(golden_organism_path / "siop_internal.json")
            golden_seed = read_json(golden_organism_path / "organism_blueprint_seed.json")

            if golden_siop is not None or golden_seed is not None:
                golden_compared = True
                golden_issues: list[Issue] = []

                if golden_siop is not None and siop is not None:
                    golden_issues.extend(diff_against_golden(slug, siop, golden_siop, "siop_internal.json"))
                if golden_seed is not None and blueprint_seed is not None:
                    golden_issues.extend(diff_against_golden(slug, blueprint_seed, golden_seed, "organism_blueprint_seed.json"))

                issues.extend(golden_issues)
                golden_match = not any(
                    i.check in ("golden_field_missing", "golden_field_changed")
                    for i in golden_issues
                )

        organism_reports.append(
            OrganismReport(
                organism_slug=slug,
                structural_valid=structural_valid,
                golden_compared=golden_compared,
                golden_match=golden_match,
                issues=issues,
            )
        )

    structural_errors = sum(
        1 for r in organism_reports for i in r.issues
        if i.severity == "ERROR" and i.check != "golden_field_missing"
    )
    golden_mismatches = sum(
        1 for r in organism_reports for i in r.issues
        if i.check in ("golden_field_missing", "golden_field_changed")
    )

    report = RegressionReport(
        checked_at=now(),
        client_root=str(client_root),
        golden_dir=str(golden_dir) if golden_dir else None,
        organisms_checked=len(organism_reports),
        structural_errors=structural_errors,
        golden_mismatches=golden_mismatches,
        organisms=organism_reports,
    )

    write_json(client_root / "10_swarm" / "regression_report.json", asdict(report))
    return report


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Swarm Regression Validator")
    parser.add_argument("--client-root", required=True, help="Client package root (containing 10_swarm/organisms/)")
    parser.add_argument("--golden-dir", default=None, help="Optional directory with known-good organism snapshots to diff against")
    args = parser.parse_args()

    report = validate_client_organisms(args.client_root, args.golden_dir)

    print("\nSwarm Regression Validator complete")
    print(f"Organisms checked:  {report.organisms_checked}")
    print(f"Structural errors:  {report.structural_errors}")
    print(f"Golden mismatches:  {report.golden_mismatches}")

    for r in report.organisms:
        marker = "OK" if r.structural_valid else "!!"
        golden_label = ""
        if r.golden_compared:
            golden_label = " | golden=MATCH" if r.golden_match else " | golden=MISMATCH"
        print(f"\n  [{marker}] {r.organism_slug}{golden_label}")
        for issue in r.issues:
            print(f"      [{issue.severity}] {issue.check}: {issue.message}")

    print(f"\nOutput: {Path(args.client_root) / '10_swarm' / 'regression_report.json'}")

    if report.structural_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    run_cli()
