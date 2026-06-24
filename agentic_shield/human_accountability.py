"""
AGENTIC ZERO - AGENTIC SHIELD
Human Accountability v1.0

Role:
  approval_engine.py handles APPROVE/SANDBOX. ESCALATE and REJECT verdicts
  are explicitly out of scope there - they land here instead. This module
  is the other half of the approval gate: it queues every ESCALATE/REJECT
  for a named human, and it is the ONLY place a human decision about them
  gets recorded.

  Key governance principle: an automated REJECT is not final law. A human
  can override it - but only explicitly, only with a named identity, and
  only with a non-empty rationale. The override itself becomes a permanent,
  immutable accountability record. Nothing here lets a human silently
  approve something and disappear; every record is "who decided this back" 
  even when the AI's verdict gets overturned.

  Decision types a human can record:
    CONFIRM_REJECT       - agrees the action must not happen.
    CONFIRM_ESCALATION   - agrees this needed a human, action taken
                            outside the system (manual execution).
    OVERRIDE_TO_APPROVE  - human disagrees with Shield, explicitly
                            authorizes the action despite the veto/escalation.
    OVERRIDE_TO_SANDBOX  - human wants it staged for limited/test
                            execution rather than full activation or
                            outright block.

Input:
  agentic_shield/decisions/compliance_review.json   (final_verdict, from compliance_engine.py)
  agentic_shield/decisions/shield_decisions.json    (action detail, from policy_engine.py)

Output:
  agentic_shield/decisions/human_review_queue.json   (pending ESCALATE/REJECT items)
  agentic_shield/decisions/accountability_log.jsonl  (audit trail, append-only, immutable)
  agentic_shield/state/human_accountability_state.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_DECISIONS = (
    "CONFIRM_REJECT",
    "CONFIRM_ESCALATION",
    "OVERRIDE_TO_APPROVE",
    "OVERRIDE_TO_SANDBOX",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


@dataclass
class AccountabilityRecord:
    decision_id: str
    prescription_id: str
    pattern_name: str
    shield_verdict: str
    affected_organisms: list[str]
    human_decision: str
    decided_by: str
    rationale: str
    decided_at: str


class HumanAccountability:
    def __init__(
        self,
        decisions_root: str | Path = "agentic_shield/decisions",
        state_root: str | Path = "agentic_shield/state",
    ):
        self.decisions_root = Path(decisions_root)
        self.state_root = Path(state_root)

        self.compliance_review_file = self.decisions_root / "compliance_review.json"
        self.shield_decisions_file = self.decisions_root / "shield_decisions.json"
        self.queue_file = self.decisions_root / "human_review_queue.json"
        self.accountability_log = self.decisions_root / "accountability_log.jsonl"
        self.state_file = self.state_root / "human_accountability_state.json"

    def load_decision_detail(self) -> dict[str, dict[str, Any]]:
        payload = read_json(self.shield_decisions_file, {"decisions": []})
        return {d["decision_id"]: d for d in payload.get("decisions", []) if "decision_id" in d}

    def load_existing_queue(self) -> dict[str, dict[str, Any]]:
        existing = read_json(self.queue_file, {"items": {}})
        return existing.get("items", {})

    def already_decided(self) -> set[str]:
        decided = set()
        if self.accountability_log.exists():
            for line in self.accountability_log.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    decided.add(record.get("decision_id", ""))
                except json.JSONDecodeError:
                    continue
        return decided

    def queue(self) -> dict[str, Any]:
        review_payload = read_json(self.compliance_review_file, {"reviews": []})
        reviews = review_payload.get("reviews", [])
        decision_detail = self.load_decision_detail()
        existing_queue = self.load_existing_queue()
        decided = self.already_decided()

        new_items = 0
        for review in reviews:
            final_verdict = review.get("final_verdict", "")
            decision_id = review.get("decision_id", "")

            if final_verdict not in ("ESCALATE", "REJECT"):
                continue
            if decision_id in decided:
                # Already has a recorded human decision - don't re-queue.
                continue
            if decision_id in existing_queue:
                continue

            detail = decision_detail.get(decision_id, {})
            existing_queue[decision_id] = {
                "decision_id": decision_id,
                "prescription_id": review.get("prescription_id", ""),
                "pattern_name": review.get("pattern_name", ""),
                "shield_verdict": final_verdict,
                "override_reason": review.get("override_reason", ""),
                "target_component": detail.get("target_component", ""),
                "proposed_action_type": detail.get("proposed_action_type", ""),
                "affected_organisms": detail.get("affected_organisms", []),
                "confidence": detail.get("confidence", 0.0),
                "rationale": detail.get("rationale", ""),
                "queued_at": now(),
            }
            new_items += 1

        write_json(self.queue_file, {"updated_at": now(), "items": existing_queue})

        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "human_accountability",
                "status": "HUMAN_ACCOUNTABILITY_ACTIVE",
                "queue_size": len(existing_queue),
                "new_items_this_pass": new_items,
                "next_step": "Use --record-decision to attribute a human decision to each queued item",
            },
        )

        return {
            "queue_size": len(existing_queue),
            "new_items_this_pass": new_items,
            "queue_file": str(self.queue_file),
        }

    def record_decision(
        self,
        decision_id: str,
        decision: str,
        decided_by: str,
        rationale: str,
    ) -> dict[str, Any]:
        if decision not in VALID_DECISIONS:
            return {
                "status": "rejected",
                "reason": f"'{decision}' is not a valid decision type. Must be one of: {', '.join(VALID_DECISIONS)}",
            }

        if not decided_by.strip():
            return {"status": "rejected", "reason": "decided_by cannot be empty - every decision must be attributable to a named person."}

        if not rationale.strip():
            return {"status": "rejected", "reason": "rationale cannot be empty - especially for overrides of an automated REJECT/ESCALATE."}

        queue = self.load_existing_queue()
        item = queue.get(decision_id)
        if not item:
            return {"status": "not_found", "decision_id": decision_id}

        record = AccountabilityRecord(
            decision_id=decision_id,
            prescription_id=item.get("prescription_id", ""),
            pattern_name=item.get("pattern_name", ""),
            shield_verdict=item.get("shield_verdict", ""),
            affected_organisms=item.get("affected_organisms", []),
            human_decision=decision,
            decided_by=decided_by,
            rationale=rationale,
            decided_at=now(),
        )
        append_jsonl(self.accountability_log, asdict(record))

        queue.pop(decision_id, None)
        write_json(self.queue_file, {"updated_at": now(), "items": queue})

        return {
            "status": "recorded",
            "decision_id": decision_id,
            "human_decision": decision,
            "decided_by": decided_by,
        }


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Agentic Shield Human Accountability")
    parser.add_argument("--decisions-root", default="agentic_shield/decisions")
    parser.add_argument("--state-root", default="agentic_shield/state")
    parser.add_argument("--queue", action="store_true", help="Queue new ESCALATE/REJECT items from the latest compliance review")
    parser.add_argument("--record-decision", default="", help="decision_id to record a human decision for")
    parser.add_argument(
        "--decision",
        default="",
        help=f"Decision type, one of: {', '.join(VALID_DECISIONS)}",
    )
    parser.add_argument("--decided-by", default="", help="Identifier of the human making this decision")
    parser.add_argument("--rationale", default="", help="Why this decision was made (mandatory)")
    args = parser.parse_args()

    engine = HumanAccountability(decisions_root=args.decisions_root, state_root=args.state_root)

    if args.record_decision:
        result = engine.record_decision(
            args.record_decision, args.decision, args.decided_by, args.rationale
        )
        print("\nAgentic Shield Human Accountability - decision recorded")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result["status"] != "recorded":
            raise SystemExit(1)
        return

    result = engine.queue()

    print("\nAgentic Shield Human Accountability complete")
    print(f"Queue size:          {result['queue_size']}")
    print(f"New items this pass: {result['new_items_this_pass']}")

    print("\nOutput:")
    print(f"  queue: {result['queue_file']}")


if __name__ == "__main__":
    run_cli()
