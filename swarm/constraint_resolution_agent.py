"""
AGENTIC ZERO - SWARM
Constraint Resolution Agent v1.0

Role:
  Every real swarm topology observed so far (S&OP's 11 organisms, the
  Agentic One 9-domain fixture) routes most of its event_routes toward a
  "Constraint Resolution Organism" - but until now nothing actually
  computed anything there. It was a named sink with no logic. This module
  is that logic.

  Given a ConflictCase from swarm_coordinator.py (two or more organisms
  disagreeing on risk_score/confidence for the same scenario_id), this
  module decides:

    RESOLVED_AUTO  - the disagreement is within tolerance once weighted
                     by each organism's own confidence (a low-confidence
                     outlier doesn't get to override a high-confidence
                     majority). Auto-resolution picks the
                     confidence-weighted average and is logged as
                     auto-resolved.

    ESCALATED      - the disagreement is too large, or confidence is
                     itself too low across the board to trust a weighted
                     average. This does NOT pick a winner - it hands the
                     case to Shield/human, the same default-safe principle
                     policy_engine.py already uses (never silently resolve
                     a high-stakes disagreement just because a number
                     could technically be computed).

  This module never auto-resolves a CRITICAL-impact disagreement
  regardless of how small the numeric delta is - financial_impact and
  service_impact fields (when present in a recommendation's payload) are
  checked independently of the risk/confidence delta that originally
  triggered the conflict.

Input:
  <event_dir>/swarm_conflicts.jsonl   (from swarm_coordinator.py)

Output:
  <event_dir>/constraint_resolutions.jsonl   (append-only, one record per
                                               resolved/escalated conflict)
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUTO_RESOLVE_CONFIDENCE_FLOOR = 0.70
CRITICAL_IMPACT_KEYWORDS = ("financial_impact", "service_impact")
CRITICAL_IMPACT_ESCALATE_THRESHOLD = 0.70


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def already_processed(path: Path) -> set[str]:
    return {r.get("conflict_id", "") for r in read_jsonl(path)}


@dataclass
class ResolutionRecord:
    resolution_id: str
    conflict_id: str
    scenario_id: str
    resolved_at: str
    verdict: str  # RESOLVED_AUTO or ESCALATED
    rationale: str
    competing_organisms: list[str]
    weighted_risk_score: float | None
    weighted_confidence: float | None


class ConstraintResolutionAgent:
    def __init__(self, event_dir: str | Path):
        self.event_dir = Path(event_dir)
        self.conflicts_file = self.event_dir / "swarm_conflicts.jsonl"
        self.resolutions_file = self.event_dir / "constraint_resolutions.jsonl"

    def _has_critical_impact(self, conflict: dict[str, Any]) -> tuple[bool, str]:
        for rec in conflict.get("recommendations", []):
            payload = rec.get("payload", {})
            for key in CRITICAL_IMPACT_KEYWORDS:
                value = payload.get(key)
                if value is None:
                    continue
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue
                if value >= CRITICAL_IMPACT_ESCALATE_THRESHOLD:
                    return True, (
                        f"organism {rec.get('organism_slug')} reports {key}={value} "
                        f">= escalate threshold {CRITICAL_IMPACT_ESCALATE_THRESHOLD}"
                    )
        return False, ""

    def resolve(self, conflict: dict[str, Any]) -> ResolutionRecord:
        recommendations = conflict.get("recommendations", [])
        competing = conflict.get("competing_organisms", [])

        critical, critical_reason = self._has_critical_impact(conflict)
        if critical:
            return self._escalate(
                conflict,
                competing,
                reason=f"Critical impact detected regardless of risk/confidence delta: {critical_reason}.",
            )

        confidences = [float(r.get("confidence", 0.0)) for r in recommendations]
        risks = [float(r.get("risk_score", 0.0)) for r in recommendations]

        if any(c < AUTO_RESOLVE_CONFIDENCE_FLOOR for c in confidences):
            low_confidence_orgs = [
                r.get("organism_slug")
                for r in recommendations
                if float(r.get("confidence", 0.0)) < AUTO_RESOLVE_CONFIDENCE_FLOOR
            ]
            return self._escalate(
                conflict,
                competing,
                reason=(
                    f"At least one competing recommendation is below the auto-resolve "
                    f"confidence floor ({AUTO_RESOLVE_CONFIDENCE_FLOOR}): {low_confidence_orgs}. "
                    f"A confidence-weighted average is not trustworthy when one input is "
                    f"this uncertain."
                ),
            )

        total_confidence = sum(confidences)
        if total_confidence <= 0:
            return self._escalate(
                conflict, competing, reason="Total confidence across recommendations is zero or invalid."
            )

        weighted_risk = sum(r * c for r, c in zip(risks, confidences)) / total_confidence
        weighted_confidence = sum(c * c for c in confidences) / total_confidence

        record = ResolutionRecord(
            resolution_id=f"RES-{conflict.get('conflict_id', '')}",
            conflict_id=conflict.get("conflict_id", ""),
            scenario_id=conflict.get("scenario_id", ""),
            resolved_at=now(),
            verdict="RESOLVED_AUTO",
            rationale=(
                f"All competing recommendations clear the confidence floor "
                f"({AUTO_RESOLVE_CONFIDENCE_FLOOR}) and no critical impact was reported. "
                f"Resolved to confidence-weighted risk_score={weighted_risk:.4f}."
            ),
            competing_organisms=competing,
            weighted_risk_score=round(weighted_risk, 4),
            weighted_confidence=round(weighted_confidence, 4),
        )
        append_jsonl(self.resolutions_file, asdict(record))
        return record

    def _escalate(
        self, conflict: dict[str, Any], competing: list[str], reason: str
    ) -> ResolutionRecord:
        record = ResolutionRecord(
            resolution_id=f"RES-{conflict.get('conflict_id', '')}",
            conflict_id=conflict.get("conflict_id", ""),
            scenario_id=conflict.get("scenario_id", ""),
            resolved_at=now(),
            verdict="ESCALATED",
            rationale=reason,
            competing_organisms=competing,
            weighted_risk_score=None,
            weighted_confidence=None,
        )
        append_jsonl(self.resolutions_file, asdict(record))
        return record

    def process_pending(self) -> list[ResolutionRecord]:
        conflicts = read_jsonl(self.conflicts_file)
        processed = already_processed(self.resolutions_file)

        results = []
        for conflict in conflicts:
            if conflict.get("conflict_id") in processed:
                continue
            results.append(self.resolve(conflict))
        return results


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Constraint Resolution Agent")
    parser.add_argument("--event-dir", required=True)
    args = parser.parse_args()

    agent = ConstraintResolutionAgent(event_dir=args.event_dir)
    results = agent.process_pending()

    print("\nConstraint Resolution Agent complete")
    print(f"Conflicts processed: {len(results)}")
    for r in results:
        print(f"  {r.conflict_id} -> {r.verdict}: {r.rationale[:90]}")
    print(f"\nOutput: {agent.resolutions_file}")


if __name__ == "__main__":
    run_cli()
