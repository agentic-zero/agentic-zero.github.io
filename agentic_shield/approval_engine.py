"""
AGENTIC ZERO - AGENTIC SHIELD
Approval Engine v1.0

Role:
  policy_engine.py and compliance_engine.py together produce a
  final_verdict per decision (APPROVE / SANDBOX / ESCALATE / REJECT), but
  a verdict is still just a classification - nothing has actually
  happened yet. approval_engine.py is what turns an APPROVE/SANDBOX
  verdict into something The Machine or a human can act on:

    APPROVE  -> ACTIVATED immediately. No further human gate; the
                organism-level autonomous_actions or swarm-level
                autonomous_allowed match already established trust for
                this exact action.
    SANDBOX  -> STAGED_PENDING_APPROVAL. Written to a queue, NOT
                activated. A human must explicitly promote it via
                --approve-staged <decision_id> before it ever runs live.
                This is the actual approval gate the roadmap's Phase 3
                goal describes ("approve / reject / sandbox / escalate")
                - sandbox isn't a verdict that sits there forever, it's
                a verdict that requires one specific human action to
                leave the sandbox.

  ESCALATE and REJECT are explicitly OUT OF SCOPE here - they are not
  approval/activation concerns, they are human_accountability.py's job
  (who they go to, how the human's decision gets recorded).

Input:
  agentic_shield/decisions/compliance_review.json   (final_verdict, from compliance_engine.py)
  agentic_shield/decisions/shield_decisions.json    (action detail, from policy_engine.py)

Output:
  agentic_shield/decisions/approval_log.json
  agentic_shield/decisions/approval_log.jsonl       (audit trail, append-only)
  agentic_shield/decisions/sandbox_queue.json        (pending human promotion)
  agentic_shield/state/approval_engine_state.json
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
class ApprovalRecord:
    decision_id: str
    prescription_id: str
    pattern_name: str
    final_verdict: str
    status: str
    target_component: str
    proposed_action_type: str
    affected_organisms: list[str]
    confidence: float
    activated_at: str
    activated_by: str


class ApprovalEngine:
    def __init__(
        self,
        decisions_root: str | Path = "agentic_shield/decisions",
        state_root: str | Path = "agentic_shield/state",
    ):
        self.decisions_root = Path(decisions_root)
        self.state_root = Path(state_root)

        self.compliance_review_file = self.decisions_root / "compliance_review.json"
        self.shield_decisions_file = self.decisions_root / "shield_decisions.json"
        self.approval_log_file = self.decisions_root / "approval_log.json"
        self.approval_log_jsonl = self.decisions_root / "approval_log.jsonl"
        self.sandbox_queue_file = self.decisions_root / "sandbox_queue.json"
        self.state_file = self.state_root / "approval_engine_state.json"

    def load_decision_detail(self) -> dict[str, dict[str, Any]]:
        payload = read_json(self.shield_decisions_file, {"decisions": []})
        return {d["decision_id"]: d for d in payload.get("decisions", []) if "decision_id" in d}

    def load_existing_sandbox_queue(self) -> dict[str, dict[str, Any]]:
        existing = read_json(self.sandbox_queue_file, {"items": {}})
        return existing.get("items", {})

    def process(self) -> dict[str, Any]:
        review_payload = read_json(self.compliance_review_file, {"reviews": []})
        reviews = review_payload.get("reviews", [])
        decision_detail = self.load_decision_detail()
        sandbox_queue = self.load_existing_sandbox_queue()

        records: list[ApprovalRecord] = []
        skipped_out_of_scope = 0

        for review in reviews:
            final_verdict = review.get("final_verdict", "")
            decision_id = review.get("decision_id", "")
            detail = decision_detail.get(decision_id, {})

            if final_verdict == "APPROVE":
                record = ApprovalRecord(
                    decision_id=decision_id,
                    prescription_id=review.get("prescription_id", ""),
                    pattern_name=review.get("pattern_name", ""),
                    final_verdict=final_verdict,
                    status="ACTIVATED",
                    target_component=detail.get("target_component", ""),
                    proposed_action_type=detail.get("proposed_action_type", ""),
                    affected_organisms=detail.get("affected_organisms", []),
                    confidence=detail.get("confidence", 0.0),
                    activated_at=now(),
                    activated_by="approval_engine.auto",
                )
                records.append(record)
                append_jsonl(self.approval_log_jsonl, asdict(record))
                # An activated item that was previously staged is resolved
                # and leaves the sandbox queue.
                sandbox_queue.pop(decision_id, None)

            elif final_verdict == "SANDBOX":
                if decision_id not in sandbox_queue:
                    sandbox_queue[decision_id] = {
                        "decision_id": decision_id,
                        "prescription_id": review.get("prescription_id", ""),
                        "pattern_name": review.get("pattern_name", ""),
                        "status": "STAGED_PENDING_APPROVAL",
                        "target_component": detail.get("target_component", ""),
                        "proposed_action_type": detail.get("proposed_action_type", ""),
                        "affected_organisms": detail.get("affected_organisms", []),
                        "confidence": detail.get("confidence", 0.0),
                        "staged_at": now(),
                    }
                record = ApprovalRecord(
                    decision_id=decision_id,
                    prescription_id=review.get("prescription_id", ""),
                    pattern_name=review.get("pattern_name", ""),
                    final_verdict=final_verdict,
                    status="STAGED_PENDING_APPROVAL",
                    target_component=detail.get("target_component", ""),
                    proposed_action_type=detail.get("proposed_action_type", ""),
                    affected_organisms=detail.get("affected_organisms", []),
                    confidence=detail.get("confidence", 0.0),
                    activated_at="",
                    activated_by="",
                )
                records.append(record)

            else:
                # ESCALATE / REJECT - out of scope for this module
                skipped_out_of_scope += 1

        write_json(self.sandbox_queue_file, {"updated_at": now(), "items": sandbox_queue})

        status_counts: dict[str, int] = {}
        for r in records:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1

        payload = {
            "generated_at": now(),
            "records_count": len(records),
            "status_counts": status_counts,
            "skipped_out_of_scope": skipped_out_of_scope,
            "sandbox_queue_size": len(sandbox_queue),
            "records": [asdict(r) for r in records],
        }
        write_json(self.approval_log_file, payload)

        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "approval_engine",
                "status": "APPROVAL_ENGINE_ACTIVE",
                "activated_count": status_counts.get("ACTIVATED", 0),
                "staged_count": status_counts.get("STAGED_PENDING_APPROVAL", 0),
                "sandbox_queue_size": len(sandbox_queue),
                "skipped_out_of_scope": skipped_out_of_scope,
                "next_step": "Use --approve-staged <decision_id> to promote a SANDBOX item, or run human_accountability.py for ESCALATE/REJECT",
            },
        )

        return payload

    def approve_staged(self, decision_id: str, approved_by: str) -> dict[str, Any]:
        """The actual human approval gate: explicitly promote one staged
        (SANDBOX) item to ACTIVATED. This is the only way a SANDBOX
        verdict ever becomes live - there is no automatic promotion path.
        """
        sandbox_queue = self.load_existing_sandbox_queue()
        item = sandbox_queue.get(decision_id)

        if not item:
            return {"status": "not_found", "decision_id": decision_id}

        record = ApprovalRecord(
            decision_id=decision_id,
            prescription_id=item.get("prescription_id", ""),
            pattern_name=item.get("pattern_name", ""),
            final_verdict="SANDBOX",
            status="ACTIVATED",
            target_component=item.get("target_component", ""),
            proposed_action_type=item.get("proposed_action_type", ""),
            affected_organisms=item.get("affected_organisms", []),
            confidence=item.get("confidence", 0.0),
            activated_at=now(),
            activated_by=approved_by,
        )
        append_jsonl(self.approval_log_jsonl, asdict(record))

        sandbox_queue.pop(decision_id, None)
        write_json(self.sandbox_queue_file, {"updated_at": now(), "items": sandbox_queue})

        return {"status": "activated", "decision_id": decision_id, "approved_by": approved_by}


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Agentic Shield Approval Engine")
    parser.add_argument("--decisions-root", default="agentic_shield/decisions")
    parser.add_argument("--state-root", default="agentic_shield/state")
    parser.add_argument("--process", action="store_true", help="Run an approval pass over current compliance reviews")
    parser.add_argument("--approve-staged", default="", help="decision_id of a SANDBOX item to explicitly promote to ACTIVATED")
    parser.add_argument("--approved-by", default="", help="Identifier of the human approving a staged item (required with --approve-staged)")
    args = parser.parse_args()

    engine = ApprovalEngine(decisions_root=args.decisions_root, state_root=args.state_root)

    if args.approve_staged:
        if not args.approved_by:
            print("ERROR: --approved-by is required when using --approve-staged (every activation must be attributable to a person).")
            raise SystemExit(1)
        result = engine.approve_staged(args.approve_staged, args.approved_by)
        print("\nAgentic Shield Approval Engine - manual promotion")
        print(json.dumps(result, indent=2))
        return

    result = engine.process()

    print("\nAgentic Shield Approval Engine complete")
    print(f"Records processed:    {result['records_count']}")
    print(f"Skipped (out of scope, ESCALATE/REJECT): {result['skipped_out_of_scope']}")
    print(f"Sandbox queue size:   {result['sandbox_queue_size']}")
    print("Status breakdown:")
    for status, count in result["status_counts"].items():
        print(f"  {status}: {count}")

    print("\nOutput:")
    print(f"  approval_log:   {engine.approval_log_file}")
    print(f"  sandbox_queue:  {engine.sandbox_queue_file}")
    print(f"  state:          {engine.state_file}")


if __name__ == "__main__":
    run_cli()
