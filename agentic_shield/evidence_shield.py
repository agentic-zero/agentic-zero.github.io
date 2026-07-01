# agentic_shield/evidence_shield.py

"""
AGENTIC ZERO - AGENTIC SHIELD
Evidence Shield v1.0 (M12)

Role:
  Compiles the governance trail Agentic Shield already produces
  (agentic_shield/audit_trails.py consolidates shield_decisions.jsonl,
  compliance_violations.jsonl, approval_log.jsonl, accountability_log.jsonl
  per decision) into a self-contained, exportable EVIDENCE PACKAGE
  suitable for an external compliance audit (ISO 42001, EU AI Act, NIST
  AI RMF - the frameworks already tagged throughout this platform's
  process library).

  This is the layer between "we technically logged everything" and "we
  can hand an auditor a single document that proves what happened, why,
  and that it hasn't been altered since." Internal system name - per
  the project's own constraint, never disclosed in public-facing copy.

Why this does NOT re-derive the decision timeline itself:
  agentic_shield/audit_trails.py already builds the per-decision
  timeline correctly (and is the SINGLE producer of that artifact, per
  the same "one producer per artifact" rule this project adopted for
  event_catalog.json). Evidence Shield consumes that timeline as input -
  it does not re-read the 4 underlying logs independently. The exact
  call site (audit_trails.show_decision(decision_id) or equivalent) is
  the one integration point to verify against the real audit_trails.py
  API once this module is reunited with the actual codebase - the
  interface here (DecisionTimelineEvent) is intentionally generic so
  this module keeps working even if that exact function name differs.

Responsibilities:
  - compile_evidence_package(): assembles one decision's full timeline +
    organism compliance frameworks + confidence/risk scores + human
    accountability records (if any) into one structured package.
  - The package gets its OWN SHA-256 hash over its full content -
    same integrity principle as security/tamper_detection.py, applied
    to the EXPORTED artifact itself: an auditor (or a future Claude/GPT
    session) can verify the package they're holding wasn't altered after
    export, independent of whatever happened to the live system since.
  - export_evidence_package(): writes the package + a parallel .sha256
    file, the same pattern as a checksum file shipped alongside a
    software release.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class DecisionTimelineEvent:
    """
    Generic shape for one event in a decision's timeline - matches what
    agentic_shield/audit_trails.py already aggregates (shield decision,
    compliance violation, approval, accountability record), kept generic
    here so this module doesn't assume audit_trails.py's exact internal
    field names.
    """
    event_type: str
    timestamp_utc: str
    actor: str
    outcome: str
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidencePackage:
    package_id: str
    generated_at: str
    decision_id: str
    client_id: str
    organism: str
    applicable_frameworks: list[str]
    confidence_score: Optional[float]
    risk_score: Optional[float]
    final_verdict: str
    timeline: list[DecisionTimelineEvent]
    human_accountability_present: bool
    integrity_sha256: str = ""  # computed after assembly, over everything above


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_package_content(package_dict_without_hash: dict[str, Any]) -> str:
    canonical = json.dumps(package_dict_without_hash, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compile_evidence_package(
    *,
    decision_id: str,
    client_id: str,
    organism: str,
    applicable_frameworks: list[str],
    timeline: list[DecisionTimelineEvent],
    confidence_score: Optional[float] = None,
    risk_score: Optional[float] = None,
) -> EvidencePackage:
    """
    Assembles one decision's evidence package. `timeline` is expected to
    already be the full chronological history for this decision_id -
    sourced from agentic_shield/audit_trails.py's existing aggregation,
    not re-derived here.
    """
    final_verdict = timeline[-1].outcome if timeline else "UNKNOWN"
    # Two distinct human-accountability vocabularies feed evidence
    # packages: agentic_shield/human_accountability.py's own override
    # types (Shield policy decisions on organism actions) and
    # pioneer_team/architect/consultant_accountability.py's correction
    # type (route/tier classification corrections). Both are genuine
    # named-human, mandatory-rationale accountability events - this
    # module must recognize either, not just the one it was originally
    # written against, or a real human correction silently reports as
    # human_accountability_present=False, which is itself exactly the
    # kind of cross-module vocabulary mismatch this whole project has
    # been hunting down today.
    HUMAN_ACCOUNTABILITY_EVENT_TYPES = (
        "CONFIRM_REJECT", "CONFIRM_ESCALATION", "OVERRIDE_TO_APPROVE", "OVERRIDE_TO_SANDBOX",
        "CONSULTANT_DECISION_CORRECTED",
    )
    human_accountability_present = any(
        e.event_type in HUMAN_ACCOUNTABILITY_EVENT_TYPES
        for e in timeline
    )

    package = EvidencePackage(
        package_id=f"EVIDENCE-{decision_id}",
        generated_at=_now(),
        decision_id=decision_id,
        client_id=client_id,
        organism=organism,
        applicable_frameworks=applicable_frameworks,
        confidence_score=confidence_score,
        risk_score=risk_score,
        final_verdict=final_verdict,
        timeline=timeline,
        human_accountability_present=human_accountability_present,
        integrity_sha256="",
    )

    package_dict = asdict(package)
    del package_dict["integrity_sha256"]
    package.integrity_sha256 = _hash_package_content(package_dict)

    return package


def verify_evidence_package(package_dict: dict[str, Any]) -> bool:
    """
    Re-hashes a package's content (minus the stored hash) and compares
    against the stored integrity_sha256. Use this on a package that was
    previously exported, to confirm nothing in it was altered since.
    """
    stored_hash = package_dict.get("integrity_sha256", "")
    content_without_hash = dict(package_dict)
    del content_without_hash["integrity_sha256"]
    recomputed = _hash_package_content(content_without_hash)
    return recomputed == stored_hash


DEFAULT_EVIDENCE_ROOT = Path("agentic_shield/evidence")


def export_evidence_package(package: EvidencePackage, output_dir: Optional[str | Path] = None) -> Path:
    """
    Default storage: agentic_shield/evidence/<client_id>/<package_id>.json
    (+ .sha256 alongside). Deliberately separate from agentic_shield/state/
    (the active work queue - pending prescriptions, in-flight decisions) -
    evidence/ is historical/exportable record, not operational state in
    progress. Pass output_dir explicitly only to override this for a
    one-off export (e.g. directly into a folder being handed to an
    external auditor).
    """
    if output_dir is None:
        output_dir = DEFAULT_EVIDENCE_ROOT / package.client_id

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    package_path = output_dir / f"{package.package_id}.json"
    package_dict = asdict(package)
    package_path.write_text(json.dumps(package_dict, indent=2, ensure_ascii=False), encoding="utf-8")

    checksum_path = output_dir / f"{package.package_id}.sha256"
    checksum_path.write_text(package.integrity_sha256, encoding="utf-8")

    return package_path


def run_cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero - Evidence Shield (verify mode)")
    parser.add_argument("--verify", required=True, help="Path to an exported evidence package JSON")
    args = parser.parse_args()

    package_dict = json.loads(Path(args.verify).read_text(encoding="utf-8"))
    valid = verify_evidence_package(package_dict)

    print("\nEvidence Shield - verification")
    print(f"Package: {args.verify}")
    print(f"Integrity: {'VALID - unaltered since export' if valid else 'TAMPERED - content does not match stored hash'}")

    if not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    run_cli()
