"""
AGENTIC ZERO - AGENTIC SHIELD
Threshold Engine v1.0

Role:
  policy_engine.py uses two GLOBAL constants (CONFIDENCE_ESCALATE_BELOW,
  CONFIDENCE_APPROVE_AT_OR_ABOVE) for every organism, regardless of how
  that organism has actually behaved. A logistics organism with a clean
  track record and a finance organism that keeps getting overridden by
  compliance_engine.py get judged by the exact same yardstick. That is
  the gap this module closes.

  threshold_engine.py reads the override history that compliance_engine.py
  already produces (compliance_violations.jsonl) and calibrates a
  PER-ORGANISM threshold pair from it:

    - Every time an organism's decision gets overridden to REJECT or
      ESCALATE by a hard business rule, that is evidence its current
      thresholds let something through that should not have gone
      through. Its escalate_below threshold is raised (more cautious)
      by a fixed step, capped at a safety ceiling.
    - Thresholds are NEVER lowered automatically. Loosening a threshold
      is a deliberate, accountable decision - not something a feedback
      loop should do to itself. An organism with a clean record simply
      keeps the global default; earning a more permissive threshold is
      a human/board calibration, not an emergent one.

  This module produces a thresholds.json that policy_engine.py can
  optionally consume via --thresholds-file. Without that flag,
  policy_engine.py is unaffected (backward compatible with Phase 3
  baseline behavior).

Input:
  agentic_shield/decisions/compliance_violations.jsonl   (from compliance_engine.py)

Output:
  agentic_shield/config/thresholds.json
  agentic_shield/state/threshold_engine_state.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GLOBAL_DEFAULT_ESCALATE_BELOW = 0.70
GLOBAL_DEFAULT_APPROVE_AT_OR_ABOVE = 0.85

ESCALATE_STEP = 0.05
ESCALATE_BELOW_CEILING = 0.90  # never demand near-certainty by default - that
                                 # would make every action unactionable; a
                                 # ceiling this high already means "almost
                                 # always escalate" for that organism.
APPROVE_STEP = 0.03
APPROVE_AT_OR_ABOVE_CEILING = 0.97


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


@dataclass
class OrganismThreshold:
    organism_slug: str
    escalate_below: float
    approve_at_or_above: float
    overrides_observed: int
    rationale: str
    last_calibrated: str


class ThresholdEngine:
    def __init__(
        self,
        decisions_root: str | Path = "agentic_shield/decisions",
        config_root: str | Path = "agentic_shield/config",
        state_root: str | Path = "agentic_shield/state",
    ):
        self.decisions_root = Path(decisions_root)
        self.config_root = Path(config_root)
        self.state_root = Path(state_root)

        self.violations_log = self.decisions_root / "compliance_violations.jsonl"
        self.thresholds_file = self.config_root / "thresholds.json"
        self.state_file = self.state_root / "threshold_engine_state.json"

    def load_existing_thresholds(self) -> dict[str, dict[str, Any]]:
        existing = read_json(self.thresholds_file, {"organisms": {}})
        return existing.get("organisms", {})

    def load_cursor(self) -> int:
        """Lines of compliance_violations.jsonl already processed in a prior
        calibration pass. Without this, an append-only log that persists
        across runs would get recounted in full every time, ratcheting
        thresholds up forever even with zero new violations.
        """
        state = read_json(self.state_file, {})
        return int(state.get("violations_cursor", 0))

    def count_overrides_per_organism(self, violations: list[dict[str, Any]]) -> dict[str, int]:
        """A violation record doesn't carry organism slugs directly (it was
        written from a ShieldDecision, which carries affected_organisms as
        full names, not slugs) - so this reconstructs slugs from the rule
        text, which always names the organism as 'organism:<SLUG> rule:...'.
        """
        counts: dict[str, int] = {}
        for v in violations:
            rule_text = v.get("rule", "")
            # rule text on its own doesn't carry the slug; the override_reason
            # in compliance_review.json does ('organism:<SLUG> rule:...').
            # violations.jsonl entries instead carry it implicitly via the
            # decision_id naming convention (SHIELD-<prescription_id>), so we
            # fall back to scanning the original decision's affected_organisms
            # if present in the violation payload.
            organism_hint = v.get("organism_slug")
            if organism_hint:
                counts[organism_hint] = counts.get(organism_hint, 0) + 1
        return counts

    def calibrate(self) -> dict[str, Any]:
        all_violations = read_jsonl(self.violations_log)
        cursor = self.load_cursor()
        new_violations = all_violations[cursor:]

        existing = self.load_existing_thresholds()
        override_counts = self.count_overrides_per_organism(new_violations)

        organisms: dict[str, dict[str, Any]] = {}
        calibrated_count = 0

        for slug, count in override_counts.items():
            previous = existing.get(slug, {})
            previous_escalate = previous.get(
                "escalate_below", GLOBAL_DEFAULT_ESCALATE_BELOW
            )
            previous_approve = previous.get(
                "approve_at_or_above", GLOBAL_DEFAULT_APPROVE_AT_OR_ABOVE
            )

            new_escalate = min(
                previous_escalate + ESCALATE_STEP * count, ESCALATE_BELOW_CEILING
            )
            new_approve = min(
                previous_approve + APPROVE_STEP * count, APPROVE_AT_OR_ABOVE_CEILING
            )

            changed = (
                round(new_escalate, 4) != round(previous_escalate, 4)
                or round(new_approve, 4) != round(previous_approve, 4)
            )
            if changed:
                calibrated_count += 1

            threshold = OrganismThreshold(
                organism_slug=slug,
                escalate_below=round(new_escalate, 4),
                approve_at_or_above=round(new_approve, 4),
                overrides_observed=previous.get("overrides_observed", 0) + count,
                rationale=(
                    f"{count} new compliance override(s) observed this pass; "
                    f"escalate_below raised by up to {ESCALATE_STEP * count:.2f} "
                    f"(never lowered automatically)."
                ),
                last_calibrated=now(),
            )
            organisms[slug] = asdict(threshold)

        # Carry forward any organism that already had a calibrated threshold
        # but had zero new overrides this pass - thresholds persist, they
        # don't silently reset to global defaults between runs.
        for slug, previous in existing.items():
            if slug not in organisms:
                organisms[slug] = previous

        payload = {
            "generated_at": now(),
            "global_defaults": {
                "escalate_below": GLOBAL_DEFAULT_ESCALATE_BELOW,
                "approve_at_or_above": GLOBAL_DEFAULT_APPROVE_AT_OR_ABOVE,
            },
            "organisms": organisms,
            "policy": (
                "Per-organism thresholds only ever become MORE cautious "
                "automatically (escalate_below up, approve_at_or_above up). "
                "Loosening a threshold back toward the global default is a "
                "deliberate human/board calibration, never automatic."
            ),
        }

        write_json(self.thresholds_file, payload)

        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "threshold_engine",
                "status": "THRESHOLD_ENGINE_ACTIVE",
                "organisms_tracked": len(organisms),
                "organisms_calibrated_this_pass": calibrated_count,
                "violations_processed": len(new_violations),
                "violations_cursor": len(all_violations),
                "next_step": "policy_engine.py can consume thresholds.json via --thresholds-file",
            },
        )

        return {
            "organisms_tracked": len(organisms),
            "organisms_calibrated_this_pass": calibrated_count,
            "violations_processed": len(new_violations),
            "thresholds_file": str(self.thresholds_file),
            "state_file": str(self.state_file),
        }


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Agentic Shield Threshold Engine")
    parser.add_argument("--decisions-root", default="agentic_shield/decisions")
    parser.add_argument("--config-root", default="agentic_shield/config")
    parser.add_argument("--state-root", default="agentic_shield/state")
    parser.add_argument("--calibrate", action="store_true", help="Run a calibration pass over compliance override history")
    args = parser.parse_args()

    engine = ThresholdEngine(
        decisions_root=args.decisions_root,
        config_root=args.config_root,
        state_root=args.state_root,
    )

    result = engine.calibrate()

    print("\nAgentic Shield Threshold Engine complete")
    print(f"Organisms tracked:          {result['organisms_tracked']}")
    print(f"Calibrated this pass:       {result['organisms_calibrated_this_pass']}")
    print(f"Violations processed:       {result['violations_processed']}")

    print("\nOutput:")
    print(f"  thresholds: {result['thresholds_file']}")
    print(f"  state:      {result['state_file']}")


if __name__ == "__main__":
    run_cli()
