# pioneer_team/architect/consultant_accountability.py

"""
AGENTIC ZERO - PIONEER TEAM
Consultant Accountability v1.0

Role:
  functional_consultant.py is THE most important judgment call in the
  commercial pipeline (per explicit product direction, 26 Jun 2026) -
  but until now it was the only major decision-making component in this
  platform that did NOT log to the audit trail, and had no mechanism for
  a human to correct a wrong classification.

  Every other governance-relevant decision already follows this exact
  pattern:
    - SecurityGateway / EntitlementGuard -> security/audit_logger.py
    - Agentic Shield's human overrides -> agentic_shield/human_accountability.py
      (mandatory attribution, no empty rationale, permanently auditable)
    - threshold_engine.py calibrates from real override history

  This module closes that gap for the Functional Consultant:

    1. log_consultation() - every consultation, whether decided by Claude
       or the deterministic fallback, gets written to the SAME audit
       trail everything else uses (security/state/audit_logs/). This
       does not duplicate AuditLogger - it calls it, same as every
       other module in this codebase.

    2. record_correction() - a human can correct a wrong route/tier
       classification, but ONLY with a named corrector and a non-empty
       rationale - same mandatory-attribution pattern as
       human_accountability.py. No silent overrides, ever.

    3. get_correction_patterns() - the honest version of "learning from
       mistakes" for this component: aggregates the correction log into
       which (original_route -> corrected_route) pairs repeat, with
       sample rationales. This is NOT a machine-learning feedback loop -
       it is a structured signal a human reviews periodically (the same
       kind of signal threshold_engine.py computes from Shield override
       history) to notice "the consultant keeps under-calling Standard as
       Essential for X kind of request" before it costs real revenue or
       under-builds for a client.

Without this module, the single highest-leverage decision in the whole
commercial pipeline was also the only one nobody could ever audit or
correct with accountability. That is the gap this closes.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger

def _corrections_log_path() -> Path:
    return _repo_root() / "security" / "state" / "consultant_corrections.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_client_id(raw: str, fallback: str = "_unknown_consultation") -> str:
    """
    Same principle as security/lead_notifier.py's _safe_client_id():
    client_id ends up as a filename component inside AuditLogger. The
    company name or level_1_process string here can originate from a
    public-facing audit form - untrusted input - so it must be slugified
    before it ever reaches the audit log path, not trusted as-is.
    """
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", (raw or "").strip())
    slug = slug.strip("_")[:80]
    return slug or fallback


@dataclass
class CorrectionRecord:
    correction_id: str
    consultation_id: str
    client_id: str
    original_route: str
    original_tier: str
    original_confidence: float
    corrected_route: str
    corrected_tier: str
    corrected_by: str
    rationale: str
    corrected_at: str


def _repo_root() -> Path:
    """Same pattern as system_detector.py's repo_root() - find the real
    repo root by locating a stable marker, not by trusting the current
    working directory. Without this, AuditLogger()'s relative default
    path ("security/state/audit_logs") resolves differently depending
    on the cwd of whatever process imports this module - confirmed
    during this module's own regression testing: running from
    pioneer_team/architect/ silently created a SECOND, fragmented
    security/state/audit_logs/ nested inside that folder, separate from
    the real one every other security/ and saas/ module writes to. Same
    marker-file convention already established in this folder.
    """
    marker = Path("pioneer_team") / "architect" / "knowledge" / "interconnected_systems_ontology.json"
    root = Path.cwd()
    while True:
        if (root / marker).exists():
            return root
        if root.parent == root:
            return Path.cwd()
        root = root.parent


def log_consultation(result: Any, client_id_hint: str = "") -> None:
    """
    Call this right after consult_on_intent() produces a result - logs
    the decision to the same audit trail every other governance-relevant
    decision in this platform already uses. Never raises: a logging
    failure must not break the consultation itself, same principle
    AuditLogger's own callers already follow throughout security/.
    """
    client_id = _safe_client_id(client_id_hint or result.level_1_process)

    try:
        AuditLogger(audit_root=_repo_root() / "security" / "state" / "audit_logs").log(
            event_type="CONSULTANT_DECISION",
            client_id=client_id,
            actor="functional_consultant",
            action="consult_on_intent",
            outcome=result.method.upper(),
            severity="WARNING" if result.method == "deterministic_fallback" else "INFO",
            reason=result.rationale,
            metadata={
                "consultation_id": result.consultation_id,
                "route": result.route,
                "tier": result.tier,
                "confidence": result.confidence,
                "level_1_process": result.level_1_process,
                "organism_count": len(result.organisms),
                "synthesized_organism_count": sum(1 for o in result.organisms if o.synthesized),
                "matched_organisms": [o.organism for o in result.organisms if not o.synthesized],
                "synthesized_organisms": [o.organism for o in result.organisms if o.synthesized],
            },
        )
    except Exception:
        # Logging must never break the actual consultation result the
        # caller already has - same fail-open-for-observability,
        # fail-closed-for-decisions principle used throughout security/.
        pass


def record_correction(
    *,
    consultation_id: str,
    client_id: str,
    original_route: str,
    original_tier: str,
    original_confidence: float,
    corrected_route: str,
    corrected_tier: str,
    corrected_by: str,
    rationale: str,
) -> CorrectionRecord:
    """
    A human reviewing a consultation found the route/tier wrong and is
    correcting it. Same mandatory-attribution rule as
    agentic_shield/human_accountability.py: empty corrected_by or empty
    rationale is rejected outright, not silently defaulted.
    """
    if not corrected_by or not corrected_by.strip():
        raise ValueError(
            "corrected_by cannot be empty - every correction to a consultant "
            "decision must be attributable to a named person."
        )
    if not rationale or not rationale.strip():
        raise ValueError(
            "rationale cannot be empty - every correction must explain why "
            "the original classification was wrong."
        )

    safe_client_id = _safe_client_id(client_id)

    record = CorrectionRecord(
        correction_id=f"CORRECTION-{consultation_id}",
        consultation_id=consultation_id,
        client_id=safe_client_id,
        original_route=original_route,
        original_tier=original_tier,
        original_confidence=original_confidence,
        corrected_route=corrected_route,
        corrected_tier=corrected_tier,
        corrected_by=corrected_by,
        rationale=rationale,
        corrected_at=_now(),
    )

    _corrections_log_path().parent.mkdir(parents=True, exist_ok=True)
    with _corrections_log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    AuditLogger(audit_root=_repo_root() / "security" / "state" / "audit_logs").log(
        event_type="CONSULTANT_DECISION_CORRECTED",
        client_id=safe_client_id,
        actor=corrected_by,
        action="record_correction",
        outcome="CORRECTED",
        severity="WARNING",
        reason=rationale,
        metadata={
            "consultation_id": consultation_id,
            "original_route": original_route,
            "corrected_route": corrected_route,
        },
    )

    try:
        from agentic_shield.evidence_shield import (
            DecisionTimelineEvent, compile_evidence_package, export_evidence_package,
        )

        # This does NOT depend on agentic_shield/audit_trails.py at all -
        # deliberately so, since that integration needs the real file to
        # verify field names against (documented as a separate pending
        # item). A human correction already carries every fact a
        # compliance auditor would want to see: what the AI decided,
        # what a named human changed it to, and why - exactly the
        # "human oversight actually works" evidence ISO 42001/EU AI Act
        # audits ask for. Building this on real correction data (not
        # guessed audit_trails.py fields) means zero risk of the kind of
        # field-name mismatch bugs found elsewhere today.
        timeline = [
            DecisionTimelineEvent(
                event_type="CONSULTANT_DECISION",
                timestamp_utc=record.corrected_at,  # original timestamp not tracked here; corrected_at is the only confirmed timestamp available at this call site
                actor="functional_consultant",
                outcome=original_route,
                reason=f"Originally classified as {original_route} ({original_tier}), confidence {original_confidence}.",
            ),
            DecisionTimelineEvent(
                event_type="CONSULTANT_DECISION_CORRECTED",
                timestamp_utc=record.corrected_at,
                actor=corrected_by,
                outcome=corrected_route,
                reason=rationale,
            ),
        ]

        package = compile_evidence_package(
            decision_id=consultation_id,
            client_id=safe_client_id,
            organism="FUNCTIONAL_CONSULTATION",
            applicable_frameworks=["ISO 42001", "EU AI Act"],
            timeline=timeline,
            confidence_score=original_confidence,
        )
        export_evidence_package(package)
    except Exception:
        # Same fail-open-for-observability principle as everywhere else -
        # a missing evidence package must never block the correction
        # itself from being recorded.
        pass

    return record


def read_corrections() -> list[dict[str, Any]]:
    if not _corrections_log_path().exists():
        return []
    records = []
    for line in _corrections_log_path().read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def get_correction_patterns() -> dict[str, Any]:
    """
    The honest version of "learning from mistakes" for this component:
    not a machine-learning feedback loop, a structured aggregate of real
    human corrections - which (original_route -> corrected_route) pairs
    repeat, how often, and a sample of the rationales given. A human
    (not this module) decides what to do about a recurring pattern -
    e.g. "PROCESS_AGENT -> SWARM keeps happening for requests mentioning
    multiple named systems" might mean enterprise_architect.py's
    COMPLEX_PROCESS_KEYWORDS list, or Claude's prompt, needs adjusting.
    """
    corrections = read_corrections()

    pairs: dict[str, dict[str, Any]] = {}
    for c in corrections:
        key = f"{c['original_route']} -> {c['corrected_route']}"
        bucket = pairs.setdefault(
            key,
            {"original_route": c["original_route"], "corrected_route": c["corrected_route"], "count": 0, "sample_rationales": []},
        )
        bucket["count"] += 1
        if len(bucket["sample_rationales"]) < 3:
            bucket["sample_rationales"].append(c["rationale"])

    return {
        "generated_at": _now(),
        "total_corrections": len(corrections),
        "patterns": sorted(pairs.values(), key=lambda p: p["count"], reverse=True),
    }


def run_cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero - Consultant Accountability")
    sub = parser.add_subparsers(dest="command", required=True)

    p_correct = sub.add_parser("correct", help="Record a human correction to a consultation")
    p_correct.add_argument("--consultation-id", required=True)
    p_correct.add_argument("--client-id", required=True)
    p_correct.add_argument("--original-route", required=True)
    p_correct.add_argument("--original-tier", required=True)
    p_correct.add_argument("--original-confidence", type=float, required=True)
    p_correct.add_argument("--corrected-route", required=True)
    p_correct.add_argument("--corrected-tier", required=True)
    p_correct.add_argument("--corrected-by", required=True)
    p_correct.add_argument("--rationale", required=True)

    sub.add_parser("patterns", help="Show recurring correction patterns")

    args = parser.parse_args()

    if args.command == "correct":
        try:
            record = record_correction(
                consultation_id=args.consultation_id,
                client_id=args.client_id,
                original_route=args.original_route,
                original_tier=args.original_tier,
                original_confidence=args.original_confidence,
                corrected_route=args.corrected_route,
                corrected_tier=args.corrected_tier,
                corrected_by=args.corrected_by,
                rationale=args.rationale,
            )
        except ValueError as e:
            print(f"\nREJECTED: {e}\n")
            raise SystemExit(1)

        print("\nCorrection recorded")
        print(f"  {record.original_route} -> {record.corrected_route}")
        print(f"  by {record.corrected_by}: {record.rationale}")

    elif args.command == "patterns":
        report = get_correction_patterns()
        print(f"\nTotal corrections: {report['total_corrections']}")
        for p in report["patterns"]:
            print(f"\n  {p['original_route']} -> {p['corrected_route']}  ({p['count']}x)")
            for r in p["sample_rationales"]:
                print(f"    - {r}")


if __name__ == "__main__":
    run_cli()
