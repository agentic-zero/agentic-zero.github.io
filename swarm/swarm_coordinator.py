"""
AGENTIC ZERO - SWARM
Swarm Coordinator v1.0

Role:
  Tracks swarm-wide execution state across a cycle (one scenario_id) and
  detects two things event_router.py and event_catalog.py were never
  designed to detect, because they route individual events one at a time
  and have no concept of "this scenario as a whole":

    1. GAPS - organisms the topology expects to report for this scenario
       but haven't (yet, or at all). This is "who hasn't spoken" - useful
       for knowing when a cycle is actually complete vs still in flight.

    2. CONFLICTS - two or more organisms producing materially different
       recommendations (risk_score / confidence_score) for the SAME
       scenario_id, both funneling toward the same downstream organism
       (almost always Constraint Resolution, per the topology pattern
       observed in every real coordination file so far). Today these
       would just both arrive at Constraint Resolution and nothing would
       ever look at whether they actually agree - this module is what
       notices the disagreement exists in the first place.

  This module does NOT resolve conflicts - that is
  constraint_resolution_agent.py's job. swarm_coordinator.py only detects
  and hands off.

Input:
  <event_dir>/swarm_events.jsonl
  <event_dir>/routed_events.jsonl   (optional, additional source)
  <coordination_file>                (swarm_coordination_<process>.json, for
                                       topology: which organisms exist, and
                                       which downstream organism a conflict
                                       should be handed to)

Output:
  <event_dir>/swarm_cycle_status.json
  <event_dir>/swarm_conflicts.jsonl   (append-only, one record per detected
                                        conflict, consumed by
                                        constraint_resolution_agent.py)
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONFLICT_RISK_DELTA_THRESHOLD = 0.25
CONFLICT_CONFIDENCE_DELTA_THRESHOLD = 0.25

# A high financial/service impact deserves Constraint Resolution's
# attention on its own, even when the competing organisms otherwise agree
# on risk/confidence. Without this, a quiet-but-expensive disagreement
# would never get flagged at all - constraint_resolution_agent.py's own
# "never auto-resolve critical impact" safety net only matters if a case
# actually reaches it.
CRITICAL_IMPACT_KEYS = ("financial_impact", "service_impact")
CRITICAL_IMPACT_FLAG_THRESHOLD = 0.70


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def organism_to_slug(organism_name: str) -> str:
    """Same rule as swarm_splitter.py / swarm_generator.py / event_catalog.py
    / observer.py / policy_engine.py / compliance_engine.py.
    """
    name = re.sub(r"\s*Organism\s*$", "", organism_name.strip())
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


@dataclass
class Recommendation:
    organism_slug: str
    event_type: str
    scenario_id: str
    confidence: float
    risk_score: float
    timestamp: str
    payload: dict[str, Any]


@dataclass
class ConflictCase:
    conflict_id: str
    scenario_id: str
    detected_at: str
    target_organism: str
    competing_organisms: list[str]
    recommendations: list[dict[str, Any]]
    risk_delta: float
    confidence_delta: float
    reason: str


@dataclass
class CycleStatus:
    scenario_id: str
    checked_at: str
    expected_organisms: list[str]
    reported_organisms: list[str]
    missing_organisms: list[str]
    complete: bool
    conflicts_detected: int


class SwarmCoordinator:
    def __init__(self, event_dir: str | Path, coordination_file: str | Path | None = None):
        self.event_dir = Path(event_dir)
        self.cycle_status_file = self.event_dir / "swarm_cycle_status.json"
        self.conflicts_file = self.event_dir / "swarm_conflicts.jsonl"

        self.coordination: dict[str, Any] = {}
        self.expected_slugs: set[str] = set()
        self.target_for_slug: dict[str, str] = {}

        if coordination_file:
            self.coordination = read_json(Path(coordination_file), {})
            for org in self.coordination.get("organisms", []):
                slug = organism_to_slug(org.get("organism", ""))
                if slug:
                    self.expected_slugs.add(slug)

            for route in self.coordination.get("event_routes", []):
                from_slug = organism_to_slug(route.get("from", ""))
                to_slug = organism_to_slug(route.get("to", ""))
                if from_slug:
                    # An organism may route to multiple targets; for conflict
                    # adjudication we care about the most common convergence
                    # point, so the LAST-seen target wins if there are
                    # several - in every real topology so far that target is
                    # Constraint Resolution regardless of which route is
                    # picked last, since virtually everything routes there.
                    self.target_for_slug[from_slug] = to_slug

    def _extract_recommendations(self, events: list[dict[str, Any]]) -> list[Recommendation]:
        recommendations = []
        for event in events:
            payload = event.get("payload", {})
            scenario_id = payload.get("scenario_id") or event.get("process_id", "")
            if not scenario_id:
                continue

            organism = (
                payload.get("organism")
                or payload.get("source_organism")
                or event.get("source", "")
            )
            slug = organism_to_slug(organism) if organism else ""
            if not slug:
                continue

            confidence = payload.get("confidence_score", payload.get("confidence", 0.0))
            risk_score = payload.get("risk_score", 0.0)
            try:
                confidence = float(confidence)
                risk_score = float(risk_score)
            except (TypeError, ValueError):
                continue

            recommendations.append(
                Recommendation(
                    organism_slug=slug,
                    event_type=event.get("event_type", ""),
                    scenario_id=scenario_id,
                    confidence=confidence,
                    risk_score=risk_score,
                    timestamp=event.get("timestamp", ""),
                    payload=payload,
                )
            )
        return recommendations

    def check_cycle(self, scenario_id: str) -> CycleStatus:
        events = read_jsonl(self.event_dir / "swarm_events.jsonl")
        recommendations = self._extract_recommendations(events)
        relevant = [r for r in recommendations if r.scenario_id == scenario_id]

        reported = sorted({r.organism_slug for r in relevant})
        missing = sorted(self.expected_slugs - set(reported)) if self.expected_slugs else []

        conflicts = self.detect_conflicts(scenario_id, relevant)

        status = CycleStatus(
            scenario_id=scenario_id,
            checked_at=now(),
            expected_organisms=sorted(self.expected_slugs),
            reported_organisms=reported,
            missing_organisms=missing,
            complete=not missing if self.expected_slugs else True,
            conflicts_detected=len(conflicts),
        )

        write_json(self.cycle_status_file, asdict(status))
        return status

    def detect_conflicts(
        self, scenario_id: str, recommendations: list[Recommendation] | None = None
    ) -> list[ConflictCase]:
        if recommendations is None:
            events = read_jsonl(self.event_dir / "swarm_events.jsonl")
            all_recs = self._extract_recommendations(events)
            recommendations = [r for r in all_recs if r.scenario_id == scenario_id]

        # Group by the downstream target they converge on (per topology),
        # falling back to a single shared bucket if no coordination file
        # was provided - conflicts are still detectable, just without a
        # named target organism to attribute them to.
        groups: dict[str, list[Recommendation]] = {}
        for rec in recommendations:
            target = self.target_for_slug.get(rec.organism_slug, "UNKNOWN_TARGET")
            groups.setdefault(target, []).append(rec)

        conflicts: list[ConflictCase] = []

        for target, group in groups.items():
            if len(group) < 2:
                continue

            risk_values = [r.risk_score for r in group]
            confidence_values = [r.confidence for r in group]
            risk_delta = max(risk_values) - min(risk_values)
            confidence_delta = max(confidence_values) - min(confidence_values)

            critical_hit = None
            for rec in group:
                for key in CRITICAL_IMPACT_KEYS:
                    value = rec.payload.get(key)
                    if value is None:
                        continue
                    try:
                        value = float(value)
                    except (TypeError, ValueError):
                        continue
                    if value >= CRITICAL_IMPACT_FLAG_THRESHOLD:
                        critical_hit = (rec.organism_slug, key, value)
                        break
                if critical_hit:
                    break

            is_disagreement = (
                risk_delta >= CONFLICT_RISK_DELTA_THRESHOLD
                or confidence_delta >= CONFLICT_CONFIDENCE_DELTA_THRESHOLD
            )

            if is_disagreement or critical_hit:
                competing = sorted({r.organism_slug for r in group})
                if critical_hit:
                    reason = (
                        f"Organism {critical_hit[0]} reports {critical_hit[1]}={critical_hit[2]} "
                        f">= critical-impact flag threshold {CRITICAL_IMPACT_FLAG_THRESHOLD}, "
                        f"regardless of risk/confidence agreement among {competing}."
                    )
                else:
                    reason = (
                        f"Organisms {competing} disagree on scenario '{scenario_id}': "
                        f"risk_score delta={risk_delta:.2f} (threshold {CONFLICT_RISK_DELTA_THRESHOLD}), "
                        f"confidence delta={confidence_delta:.2f} (threshold {CONFLICT_CONFIDENCE_DELTA_THRESHOLD})."
                    )

                case = ConflictCase(
                    conflict_id=f"CONFLICT-{scenario_id}-{target}",
                    scenario_id=scenario_id,
                    detected_at=now(),
                    target_organism=target,
                    competing_organisms=competing,
                    recommendations=[asdict(r) for r in group],
                    risk_delta=round(risk_delta, 4),
                    confidence_delta=round(confidence_delta, 4),
                    reason=reason,
                )
                conflicts.append(case)
                append_jsonl(self.conflicts_file, asdict(case))

        return conflicts


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Swarm Coordinator")
    parser.add_argument("--event-dir", required=True)
    parser.add_argument("--coordination-file", default="")
    parser.add_argument("--scenario-id", required=True)
    args = parser.parse_args()

    coordinator = SwarmCoordinator(
        event_dir=args.event_dir,
        coordination_file=args.coordination_file or None,
    )
    status = coordinator.check_cycle(args.scenario_id)

    print("\nSwarm Coordinator complete")
    print(f"Scenario:            {status.scenario_id}")
    print(f"Reported organisms:  {status.reported_organisms}")
    print(f"Missing organisms:   {status.missing_organisms}")
    print(f"Cycle complete:      {status.complete}")
    print(f"Conflicts detected:  {status.conflicts_detected}")
    print(f"\nOutput: {coordinator.cycle_status_file}")
    if status.conflicts_detected:
        print(f"Conflicts: {coordinator.conflicts_file}")


if __name__ == "__main__":
    run_cli()
