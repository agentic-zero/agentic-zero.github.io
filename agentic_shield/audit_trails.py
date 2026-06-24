"""
AGENTIC ZERO - AGENTIC SHIELD
Audit Trails v1.0

Role:
  Every other Agentic Shield module writes its own append-only log:
    policy_engine.py        -> shield_decisions.jsonl     (the verdict)
    compliance_engine.py    -> compliance_violations.jsonl (hard rule vetoes)
    approval_engine.py      -> approval_log.jsonl          (activation)
    human_accountability.py -> accountability_log.jsonl     (human decisions)

  Each log tells one part of a decision's story, but nobody could answer
  "what happened to decision SHIELD-RX-005, end to end?" without manually
  grepping four files. audit_trails.py is the consolidation layer: it joins
  all four logs by decision_id into one chronological timeline per
  decision, plus a single flat chronological feed across all decisions for
  "what did Shield do today" style queries.

  This module is read-only with respect to governance: it never changes a
  verdict or a decision. It only assembles the story that already exists
  across the four logs into something a board or an auditor can read in
  one place.

Input:
  agentic_shield/decisions/shield_decisions.jsonl
  agentic_shield/decisions/compliance_violations.jsonl
  agentic_shield/decisions/approval_log.jsonl
  agentic_shield/decisions/accountability_log.jsonl

Output:
  agentic_shield/audit/consolidated_trail.json   (one entry per decision_id, full timeline)
  agentic_shield/audit/audit_feed.jsonl          (flat chronological feed, all decisions)
  agentic_shield/state/audit_trails_state.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


# Each source log uses a different timestamp field name and decision_id key.
# This table is the only place that needs to change if a module's log
# schema changes - everything else here is generic.
SOURCE_LOGS = {
    "policy_engine": {
        "file": "shield_decisions.jsonl",
        "timestamp_field": "created_at",
        "stage": "POLICY_DECISION",
    },
    "compliance_engine": {
        "file": "compliance_violations.jsonl",
        "timestamp_field": "timestamp",
        "stage": "COMPLIANCE_OVERRIDE",
    },
    "approval_engine": {
        "file": "approval_log.jsonl",
        "timestamp_field": "activated_at",
        "stage": "APPROVAL_ACTION",
    },
    "human_accountability": {
        "file": "accountability_log.jsonl",
        "timestamp_field": "decided_at",
        "stage": "HUMAN_DECISION",
    },
}


@dataclass
class DecisionTrail:
    decision_id: str
    prescription_id: str
    pattern_name: str
    affected_organisms: list[str]
    final_status: str
    events_count: int
    timeline: list[dict[str, Any]]


class AuditTrails:
    def __init__(
        self,
        decisions_root: str | Path = "agentic_shield/decisions",
        audit_root: str | Path = "agentic_shield/audit",
        state_root: str | Path = "agentic_shield/state",
    ):
        self.decisions_root = Path(decisions_root)
        self.audit_root = Path(audit_root)
        self.state_root = Path(state_root)

        self.consolidated_trail_file = self.audit_root / "consolidated_trail.json"
        self.audit_feed_file = self.audit_root / "audit_feed.jsonl"
        self.state_file = self.state_root / "audit_trails_state.json"

    def collect_events(self) -> list[dict[str, Any]]:
        """Read all four source logs and normalize each entry into a common
        event shape: {decision_id, stage, source_module, timestamp, detail}.
        Entries missing a decision_id are skipped - they cannot be attached
        to any trail and would otherwise corrupt the grouping.
        """
        events: list[dict[str, Any]] = []

        for module_name, spec in SOURCE_LOGS.items():
            log_path = self.decisions_root / spec["file"]
            for entry in read_jsonl(log_path):
                decision_id = entry.get("decision_id", "")
                if not decision_id:
                    continue
                events.append(
                    {
                        "decision_id": decision_id,
                        "stage": spec["stage"],
                        "source_module": module_name,
                        "timestamp": entry.get(spec["timestamp_field"], ""),
                        "detail": entry,
                    }
                )

        events.sort(key=lambda e: e["timestamp"] or "")
        return events

    def determine_final_status(self, timeline: list[dict[str, Any]]) -> str:
        """The most recent event in the timeline determines the current
        status. A later stage always supersedes an earlier one for display
        purposes - e.g. a HUMAN_DECISION that overrides a REJECT means the
        decision's real-world status is whatever the human decided, not
        the original Shield verdict.
        """
        if not timeline:
            return "UNKNOWN"

        last_event = timeline[-1]
        stage = last_event["stage"]
        detail = last_event["detail"]

        if stage == "HUMAN_DECISION":
            return f"HUMAN_DECIDED:{detail.get('human_decision', 'UNKNOWN')}"
        if stage == "APPROVAL_ACTION":
            return detail.get("status", "UNKNOWN")
        if stage == "COMPLIANCE_OVERRIDE":
            return detail.get("final_verdict", "UNKNOWN")
        if stage == "POLICY_DECISION":
            return detail.get("verdict", "UNKNOWN")
        return "UNKNOWN"

    def build_trails(self) -> dict[str, DecisionTrail]:
        events = self.collect_events()

        grouped: dict[str, list[dict[str, Any]]] = {}
        for event in events:
            grouped.setdefault(event["decision_id"], []).append(event)

        trails: dict[str, DecisionTrail] = {}
        for decision_id, timeline in grouped.items():
            # Pull descriptive fields from whichever event has them - the
            # earliest (policy_engine) event normally carries the richest
            # detail, so prefer it but fall back to any event that has it.
            prescription_id = ""
            pattern_name = ""
            affected_organisms: list[str] = []
            for event in timeline:
                detail = event["detail"]
                prescription_id = prescription_id or detail.get("prescription_id", "")
                pattern_name = pattern_name or detail.get("pattern_name", "")
                if not affected_organisms:
                    affected_organisms = detail.get("affected_organisms", []) or []

            trails[decision_id] = DecisionTrail(
                decision_id=decision_id,
                prescription_id=prescription_id,
                pattern_name=pattern_name,
                affected_organisms=affected_organisms,
                final_status=self.determine_final_status(timeline),
                events_count=len(timeline),
                timeline=timeline,
            )

        return trails

    def run(self) -> dict[str, Any]:
        trails = self.build_trails()

        all_events = self.collect_events()
        self.audit_feed_file.parent.mkdir(parents=True, exist_ok=True)
        self.audit_feed_file.touch(exist_ok=True)
        for event in all_events:
            append_jsonl(self.audit_feed_file, event)

        status_counts: dict[str, int] = {}
        for trail in trails.values():
            status_counts[trail.final_status] = status_counts.get(trail.final_status, 0) + 1

        payload = {
            "generated_at": now(),
            "decisions_count": len(trails),
            "total_events": len(all_events),
            "final_status_counts": status_counts,
            "trails": {dec_id: asdict(t) for dec_id, t in trails.items()},
        }
        write_json(self.consolidated_trail_file, payload)

        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "audit_trails",
                "status": "AUDIT_TRAILS_ACTIVE",
                "decisions_tracked": len(trails),
                "total_events": len(all_events),
                "final_status_counts": status_counts,
                "next_step": "Consolidated trail ready for board review or compliance export",
            },
        )

        return payload


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Agentic Shield Audit Trails")
    parser.add_argument("--decisions-root", default="agentic_shield/decisions")
    parser.add_argument("--audit-root", default="agentic_shield/audit")
    parser.add_argument("--state-root", default="agentic_shield/state")
    parser.add_argument("--consolidate", action="store_true", help="Build the consolidated audit trail across all four Shield logs")
    parser.add_argument("--show-decision", default="", help="Print the full timeline for a single decision_id")
    args = parser.parse_args()

    engine = AuditTrails(
        decisions_root=args.decisions_root,
        audit_root=args.audit_root,
        state_root=args.state_root,
    )

    if args.show_decision:
        trails = engine.build_trails()
        trail = trails.get(args.show_decision)
        if not trail:
            print(f"No trail found for decision_id '{args.show_decision}'")
            raise SystemExit(1)
        print(json.dumps(asdict(trail), indent=2, ensure_ascii=False))
        return

    result = engine.run()

    print("\nAgentic Shield Audit Trails complete")
    print(f"Decisions tracked: {result['decisions_count']}")
    print(f"Total events:      {result['total_events']}")
    print("Final status breakdown:")
    for status, count in result["final_status_counts"].items():
        print(f"  {status}: {count}")

    print("\nOutput:")
    print(f"  consolidated_trail: {engine.consolidated_trail_file}")
    print(f"  audit_feed:         {engine.audit_feed_file}")
    print(f"  state:              {engine.state_file}")


if __name__ == "__main__":
    run_cli()
