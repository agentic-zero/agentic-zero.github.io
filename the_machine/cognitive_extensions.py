"""
AGENTIC ZERO - THE MACHINE
Cognitive Extensions v1.0

Role:
  Build the visible cognitive state of The Machine.

It connects:
  - observations
  - patterns
  - prescriptions
  - improvement proposals
  - tautology rules
  - evolution delta
  - injected knowledge
  - confidence assessment
  - memory governance

Output:
  the_machine/state/cognitive_extensions_state.json
  the_machine/state/cortex_status.json
  the_machine/state/latest_learning.json
  the_machine/state/board_brief.json

This module is designed for the demo/UI layer.
It does not apply runtime changes.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


class CognitiveExtensions:
    def __init__(
        self,
        memory_root: str | Path = "memory",
        state_root: str | Path = "the_machine/state",
    ):
        self.memory_root = Path(memory_root)
        self.state_root = Path(state_root)

        self.semantic_root = self.memory_root / "semantic"
        self.governance_root = self.memory_root / "governance"

        self.detected_patterns_file = self.semantic_root / "detected_patterns.json"
        self.prescriptions_file = self.semantic_root / "prescriptions.json"
        self.proposals_file = self.semantic_root / "improvement_proposals.json"
        self.rules_file = self.semantic_root / "tautology_rules.json"
        self.evolution_file = self.semantic_root / "evolution_delta.json"
        self.injected_knowledge_file = self.semantic_root / "injected_knowledge.json"
        self.confidence_file = self.semantic_root / "confidence_assessment.json"
        self.governance_file = self.governance_root / "memory_governance_report.json"

        self.cognitive_state_file = self.state_root / "cognitive_extensions_state.json"
        self.cortex_status_file = self.state_root / "cortex_status.json"
        self.latest_learning_file = self.state_root / "latest_learning.json"
        self.board_brief_file = self.state_root / "board_brief.json"

    def load_context(self) -> dict[str, Any]:
        return {
            "detected_patterns": read_json(
                self.detected_patterns_file, {"patterns": []}
            ),
            "prescriptions": read_json(self.prescriptions_file, {"prescriptions": []}),
            "proposals": read_json(self.proposals_file, {"proposals": []}),
            "rules": read_json(self.rules_file, {"rules": []}),
            "evolution": read_json(self.evolution_file, {}),
            "injected_knowledge": read_json(
                self.injected_knowledge_file, {"items": []}
            ),
            "confidence": read_json(self.confidence_file, {"summary": {}, "items": []}),
            "governance": read_json(self.governance_file, {"summary": {}}),
        }

    def cortex_load_sequence(self, ctx: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "extension": "Observation Cortex",
                "status": "LOADED",
                "signal": f"{len(ctx['detected_patterns'].get('patterns', []))} patterns available",
                "purpose": "Converts runtime events into learning signals.",
            },
            {
                "extension": "Prescription Cortex",
                "status": "LOADED",
                "signal": f"{len(ctx['prescriptions'].get('prescriptions', []))} prescriptions generated",
                "purpose": "Transforms detected patterns into operational recommendations.",
            },
            {
                "extension": "Governance Cortex",
                "status": "LOADED",
                "signal": f"{len(ctx['rules'].get('rules', []))} candidate rules available",
                "purpose": "Converts learning into human-validated governance candidates.",
            },
            {
                "extension": "Memory Cortex",
                "status": "LOADED",
                "signal": f"{ctx['governance'].get('summary', {}).get('total_records', 0)} governed records",
                "purpose": "Controls private memory, retention and meta-memory boundaries.",
            },
            {
                "extension": "Evolution Cortex",
                "status": "LOADED",
                "signal": ctx["evolution"].get("status", "NO_EVOLUTION"),
                "purpose": "Calculates autonomy, intelligence, resilience and governance deltas.",
            },
        ]

    def latest_learning(self, ctx: dict[str, Any]) -> dict[str, Any]:
        patterns = ctx["detected_patterns"].get("patterns", [])
        prescriptions = ctx["prescriptions"].get("prescriptions", [])
        proposals = ctx["proposals"].get("proposals", [])
        rules = ctx["rules"].get("rules", [])
        evolution = ctx["evolution"]

        top_pattern = patterns[0] if patterns else {}
        top_prescription = prescriptions[0] if prescriptions else {}
        top_proposal = proposals[0] if proposals else {}
        top_rule = rules[0] if rules else {}

        return {
            "created_at": now(),
            "learning_status": "LEARNING_ACTIVE" if patterns else "OBSERVING",
            "latest_pattern": {
                "pattern_name": top_pattern.get("pattern_name", "none"),
                "severity": top_pattern.get("severity", "none"),
                "count": top_pattern.get("count", 0),
                "affected_organisms": top_pattern.get("affected_organisms", []),
            },
            "latest_prescription": {
                "recommendation": top_prescription.get(
                    "recommendation", "No prescription generated yet."
                ),
                "expected_gain": top_prescription.get("expected_gain", ""),
                "confidence": top_prescription.get("confidence", 0.0),
            },
            "latest_improvement": {
                "title": top_proposal.get(
                    "title", "No improvement proposal generated yet."
                ),
                "status": top_proposal.get("status", "none"),
                "rollout_mode": top_proposal.get("rollout_mode", "none"),
            },
            "latest_governance_rule": {
                "rule_name": top_rule.get(
                    "rule_name", "No candidate rule generated yet."
                ),
                "condition": top_rule.get("condition", ""),
                "action": top_rule.get("action", ""),
                "status": top_rule.get("status", "none"),
            },
            "evolution_delta": {
                "status": evolution.get("status", "NO_EVOLUTION"),
                "stage": f"{evolution.get('maturity_stage_before', 'OBSERVING')} -> {evolution.get('maturity_stage_after', 'OBSERVING')}",
                "autonomy_delta": evolution.get("autonomy_delta", 0),
                "intelligence_delta": evolution.get("intelligence_delta", 0),
                "resilience_delta": evolution.get("resilience_delta", 0),
                "governance_delta": evolution.get("governance_delta", 0),
            },
        }

    def board_brief(
        self, ctx: dict[str, Any], learning: dict[str, Any]
    ) -> dict[str, Any]:
        evolution = ctx["evolution"]
        confidence_summary = ctx["confidence"].get("summary", {})
        governance_summary = ctx["governance"].get("summary", {})

        if evolution.get("status") == "EVOLUTION_CANDIDATE":
            headline = "The organization is learning how to operate better."
            message = evolution.get(
                "board_message",
                "Agentic learning has increased enterprise autonomy, intelligence and resilience.",
            )
        else:
            headline = "The organization is under observation."
            message = "The Machine is observing runtime behavior and waiting for enough evidence to recommend evolution."

        return {
            "created_at": now(),
            "headline": headline,
            "message": message,
            "machine_status": learning.get("learning_status", "OBSERVING"),
            "evolution": learning["evolution_delta"],
            "confidence": {
                "high_confidence_items": confidence_summary.get(
                    "high_confidence_items", 0
                ),
                "human_validation_required": confidence_summary.get(
                    "human_validation_required", 0
                ),
                "rule_candidates": confidence_summary.get("rule_candidates", 0),
            },
            "governance": {
                "total_records": governance_summary.get("total_records", 0),
                "high_risk_items": governance_summary.get("high_risk_items", 0),
                "meta_memory_candidates": governance_summary.get(
                    "meta_memory_candidates", 0
                ),
            },
            "final_demo_line": (
                "Agentic learning has made the enterprise more autonomous, intelligent and resilient."
                if evolution.get("status") == "EVOLUTION_CANDIDATE"
                else "The enterprise is operating while The Machine observes and learns."
            ),
        }

    def cortex_status(self, ctx: dict[str, Any]) -> dict[str, Any]:
        load_sequence = self.cortex_load_sequence(ctx)
        loaded = sum(1 for x in load_sequence if x["status"] == "LOADED")

        return {
            "created_at": now(),
            "cortex_name": "The Machine Cortex",
            "status": "ONLINE",
            "extensions_loaded": loaded,
            "extensions_total": len(load_sequence),
            "load_sequence": load_sequence,
            "visual_state": {
                "brain_activity": "PULSING",
                "memory_activity": "ACTIVE",
                "prescription_activity": "ACTIVE"
                if ctx["prescriptions"].get("prescriptions")
                else "STANDBY",
                "evolution_activity": "ACTIVE"
                if ctx["evolution"].get("status") == "EVOLUTION_CANDIDATE"
                else "STANDBY",
            },
            "ui_hint": "Render cognitive extensions sequentially during event resolution.",
        }

    def run(self) -> dict[str, Any]:
        ctx = self.load_context()

        cortex = self.cortex_status(ctx)
        learning = self.latest_learning(ctx)
        brief = self.board_brief(ctx, learning)

        cognitive_state = {
            "created_at": now(),
            "status": "COGNITIVE_EXTENSIONS_READY",
            "cortex_status": str(self.cortex_status_file),
            "latest_learning": str(self.latest_learning_file),
            "board_brief": str(self.board_brief_file),
            "summary": {
                "extensions_loaded": cortex["extensions_loaded"],
                "learning_status": learning["learning_status"],
                "evolution_status": learning["evolution_delta"]["status"],
                "final_demo_line": brief["final_demo_line"],
            },
            "next_step": "Run machine_dashboard_state.py",
        }

        write_json(self.cortex_status_file, cortex)
        write_json(self.latest_learning_file, learning)
        write_json(self.board_brief_file, brief)
        write_json(self.cognitive_state_file, cognitive_state)

        return {
            "status": cognitive_state["status"],
            "extensions_loaded": cortex["extensions_loaded"],
            "learning_status": learning["learning_status"],
            "evolution_status": learning["evolution_delta"]["status"],
            "final_demo_line": brief["final_demo_line"],
            "cortex_status": str(self.cortex_status_file),
            "latest_learning": str(self.latest_learning_file),
            "board_brief": str(self.board_brief_file),
            "state": str(self.cognitive_state_file),
        }


def run_cli():
    parser = argparse.ArgumentParser(
        description="Agentic Zero - The Machine Cognitive Extensions"
    )
    parser.add_argument("--memory-root", default="memory")
    parser.add_argument("--state-root", default="the_machine/state")
    args = parser.parse_args()

    extensions = CognitiveExtensions(
        memory_root=args.memory_root,
        state_root=args.state_root,
    )

    result = extensions.run()

    print("\nThe Machine Cognitive Extensions complete")
    print(f"Status:             {result['status']}")
    print(f"Extensions loaded:  {result['extensions_loaded']}")
    print(f"Learning status:    {result['learning_status']}")
    print(f"Evolution status:   {result['evolution_status']}")

    print("\nFinal demo line:")
    print(f"  {result['final_demo_line']}")

    print("\nOutput:")
    print(f"  cortex_status:   {result['cortex_status']}")
    print(f"  latest_learning: {result['latest_learning']}")
    print(f"  board_brief:     {result['board_brief']}")
    print(f"  state:           {result['state']}")


if __name__ == "__main__":
    run_cli()
