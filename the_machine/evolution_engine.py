"""
AGENTIC ZERO - THE MACHINE
Evolution Engine v1.0

Role:
  Convert candidate tautology rules into an evolution delta.
  It does not apply changes automatically.

Input:
  memory/semantic/tautology_rules.json
  memory/semantic/detected_patterns.json
  memory/semantic/prescriptions.json
  memory/semantic/improvement_proposals.json

Output:
  memory/semantic/evolution_delta.json
  the_machine/state/evolution_engine_state.json
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


@dataclass
class EvolutionMetricDelta:
    metric: str
    previous_status: str
    new_status: str
    delta: str
    rationale: str


@dataclass
class EvolutionDelta:
    evolution_id: str
    created_at: str
    source_rules_count: int
    maturity_stage_before: str
    maturity_stage_after: str
    autonomy_delta: int
    intelligence_delta: int
    resilience_delta: int
    governance_delta: int
    metric_deltas: list[EvolutionMetricDelta]
    narrative: str
    board_message: str
    human_validation_required: bool
    status: str
    next_step: str


class EvolutionEngine:
    def __init__(
        self,
        memory_root: str | Path = "memory",
        state_root: str | Path = "the_machine/state",
    ):
        self.memory_root = Path(memory_root)
        self.state_root = Path(state_root)

        self.rules_file = self.memory_root / "semantic" / "tautology_rules.json"
        self.patterns_file = self.memory_root / "semantic" / "detected_patterns.json"
        self.prescriptions_file = self.memory_root / "semantic" / "prescriptions.json"
        self.proposals_file = (
            self.memory_root / "semantic" / "improvement_proposals.json"
        )

        self.evolution_file = self.memory_root / "semantic" / "evolution_delta.json"
        self.state_file = self.state_root / "evolution_engine_state.json"

    def maturity_stage(self, rules_count: int, critical_count: int) -> tuple[str, str]:
        before = "OBSERVING"

        if rules_count == 0:
            return before, "OBSERVING"

        if critical_count > 0:
            return before, "PROTECTED_LEARNING"

        if rules_count >= 5:
            return before, "ADAPTIVE_ENTERPRISE"

        return before, "LEARNING_ENTERPRISE"

    def build_metric_deltas(
        self, rules: list[dict[str, Any]]
    ) -> list[EvolutionMetricDelta]:
        if not rules:
            return [
                EvolutionMetricDelta(
                    metric="Autonomy",
                    previous_status="No validated learning loop",
                    new_status="Observation only",
                    delta="+0%",
                    rationale="No candidate rules were generated.",
                )
            ]

        high_or_critical = [
            r for r in rules if r.get("severity") in ["HIGH", "CRITICAL"]
        ]

        shield_rules = [r for r in rules if r.get("shield_enforceable")]

        return [
            EvolutionMetricDelta(
                metric="Autonomy",
                previous_status="Manual intervention patterns observed",
                new_status="Candidate autonomy rules created",
                delta=f"+{min(12, 3 * len(rules))}%",
                rationale="Repeated interventions can now become validated autonomy rules.",
            ),
            EvolutionMetricDelta(
                metric="Intelligence",
                previous_status="Events observed as isolated signals",
                new_status="Patterns converted into prescriptions",
                delta=f"+{min(15, 4 * len(rules))}%",
                rationale="The Machine converted runtime observations into structured improvement logic.",
            ),
            EvolutionMetricDelta(
                metric="Resilience",
                previous_status="Failures handled reactively",
                new_status="Failure patterns converted into preventive rules",
                delta=f"+{min(18, 5 * len(high_or_critical))}%",
                rationale="High-severity patterns can now be handled earlier in the runtime flow.",
            ),
            EvolutionMetricDelta(
                metric="Governance",
                previous_status="Shield policies static",
                new_status="Shield candidate rules generated",
                delta=f"+{min(16, 4 * len(shield_rules))}%",
                rationale="Governance can evolve from observed runtime evidence while preserving human validation.",
            ),
        ]

    def compute_delta(self) -> EvolutionDelta:
        rules_payload = read_json(self.rules_file, {"rules": []})
        rules = rules_payload.get("rules", [])

        critical_count = sum(1 for r in rules if r.get("severity") == "CRITICAL")
        high_count = sum(1 for r in rules if r.get("severity") == "HIGH")
        shield_count = sum(1 for r in rules if r.get("shield_enforceable"))

        before, after = self.maturity_stage(len(rules), critical_count)

        autonomy_delta = min(20, 3 * len(rules))
        intelligence_delta = min(25, 4 * len(rules))
        resilience_delta = min(25, 6 * critical_count + 4 * high_count)
        governance_delta = min(20, 4 * shield_count)

        metric_deltas = self.build_metric_deltas(rules)

        if not rules:
            narrative = (
                "The Machine is observing the enterprise, but no repeated pattern has "
                "yet reached the threshold required to propose evolution."
            )
            board_message = "The enterprise is being observed. No autonomous evolution is recommended yet."
            status = "NO_EVOLUTION"
            next_step = "Continue observation."
        else:
            narrative = (
                "The Machine has converted observed runtime patterns into candidate "
                "governance and autonomy rules. The organization can now evolve through "
                "human-validated learning rather than static configuration."
            )
            board_message = (
                "Agentic learning has increased enterprise autonomy, intelligence and resilience. "
                "The organization is no longer only operating - it is learning how to operate better."
            )
            status = "EVOLUTION_CANDIDATE"
            next_step = "Review evolution delta and validate candidate rules before Shield enforcement."

        return EvolutionDelta(
            evolution_id=f"EVO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            created_at=now(),
            source_rules_count=len(rules),
            maturity_stage_before=before,
            maturity_stage_after=after,
            autonomy_delta=autonomy_delta,
            intelligence_delta=intelligence_delta,
            resilience_delta=resilience_delta,
            governance_delta=governance_delta,
            metric_deltas=metric_deltas,
            narrative=narrative,
            board_message=board_message,
            human_validation_required=bool(rules),
            status=status,
            next_step=next_step,
        )

    def run(self) -> dict[str, Any]:
        delta = self.compute_delta()

        payload = asdict(delta)

        write_json(self.evolution_file, payload)

        state = {
            "updated_at": now(),
            "status": delta.status,
            "source_rules_count": delta.source_rules_count,
            "maturity_stage_before": delta.maturity_stage_before,
            "maturity_stage_after": delta.maturity_stage_after,
            "autonomy_delta": delta.autonomy_delta,
            "intelligence_delta": delta.intelligence_delta,
            "resilience_delta": delta.resilience_delta,
            "governance_delta": delta.governance_delta,
            "human_validation_required": delta.human_validation_required,
            "evolution_delta": str(self.evolution_file),
            "next_step": delta.next_step,
        }

        write_json(self.state_file, state)

        return {
            "status": delta.status,
            "rules": delta.source_rules_count,
            "stage": f"{delta.maturity_stage_before} -> {delta.maturity_stage_after}",
            "autonomy_delta": delta.autonomy_delta,
            "intelligence_delta": delta.intelligence_delta,
            "resilience_delta": delta.resilience_delta,
            "governance_delta": delta.governance_delta,
            "output": str(self.evolution_file),
            "state": str(self.state_file),
            "board_message": delta.board_message,
        }


def run_cli():
    parser = argparse.ArgumentParser(
        description="Agentic Zero - The Machine Evolution Engine"
    )
    parser.add_argument("--memory-root", default="memory")
    parser.add_argument("--state-root", default="the_machine/state")
    args = parser.parse_args()

    engine = EvolutionEngine(
        memory_root=args.memory_root,
        state_root=args.state_root,
    )

    result = engine.run()

    print("\nThe Machine Evolution Engine complete")
    print(f"Status:              {result['status']}")
    print(f"Rules:               {result['rules']}")
    print(f"Stage:               {result['stage']}")
    print(f"Autonomy delta:      +{result['autonomy_delta']}%")
    print(f"Intelligence delta:  +{result['intelligence_delta']}%")
    print(f"Resilience delta:    +{result['resilience_delta']}%")
    print(f"Governance delta:    +{result['governance_delta']}%")

    print("\nBoard message:")
    print(f"  {result['board_message']}")

    print("\nOutput:")
    print(f"  evolution_delta: {result['output']}")
    print(f"  state:           {result['state']}")


if __name__ == "__main__":
    run_cli()
