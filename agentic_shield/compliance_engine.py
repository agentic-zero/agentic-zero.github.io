"""
AGENTIC ZERO - AGENTIC SHIELD
Compliance Engine v1.0

Role:
  policy_engine.py issues APPROVE / SANDBOX / ESCALATE, but it never issues
  REJECT - it has no concept of a hard governance veto, only confidence and
  severity thresholds. compliance_engine.py is that veto layer.

  Every organism's siop_internal.json carries business_rules written in
  natural language (e.g. "Do not act on incomplete upstream context.",
  "Escalate low-confidence or conflicting recommendations."). These are not
  decoration - they are hard constraints nobody was enforcing. This module
  parses them into two rule classes and re-checks every Shield decision
  against the affected organism's own rules:

    REJECT-class rules   ("Do not...", "Never...")
      -> if the decision's pattern_name matches the rule's subject,
         the final verdict is forced to REJECT regardless of what
         policy_engine said (even an APPROVE gets overridden).

    ESCALATE-class rules ("Escalate...", "Always escalate...")
      -> if the decision's pattern_name matches and the current verdict
         is APPROVE or SANDBOX, it is raised to ESCALATE. This rule class
         never weakens a verdict, it only strengthens it.

  This module is intentionally conservative: it can only make a verdict
  MORE restrictive (APPROVE -> ESCALATE -> REJECT direction), never less.
  policy_engine.py remains the only source of an APPROVE.

Input:
  agentic_shield/decisions/shield_decisions.json   (from policy_engine.py)
  10_swarm/organisms/<SLUG>/siop_internal.json     (business_rules)

Output:
  agentic_shield/decisions/compliance_review.json
  agentic_shield/decisions/compliance_violations.jsonl   (audit trail, append-only)
  agentic_shield/state/compliance_engine_state.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Maps a pattern_name (as produced by the_machine/pattern_detector.py) to the
# natural-language subjects a business_rule is likely to use when talking
# about that failure mode. Matching is substring-based on the rule text.
PATTERN_SUBJECT_KEYWORDS: dict[str, list[str]] = {
    "missing_context": ["incomplete upstream context", "missing context", "missing input"],
    "organism_conflict": ["conflicting recommendation", "conflict"],
    "low_confidence": ["low-confidence", "low confidence"],
    "stale_organism": ["stale", "heartbeat"],
    "shield_blocked_action": ["blocked action", "policy boundary"],
    "high_risk": ["high risk", "risk threshold"],
    "unrouted_event": ["unrouted", "no target"],
    "human_intervention": ["human override", "manual intervention"],
}

REJECT_PREFIXES = ("do not", "never", "must not")
ESCALATE_PREFIXES = ("escalate", "always escalate")


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


def organism_to_slug(organism_name: str) -> str:
    name = re.sub(r"\s*Organism\s*$", "", organism_name.strip())
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


def classify_rule(rule_text: str) -> str | None:
    """Classify a single business_rule string as REJECT, ESCALATE, or None
    (informational rule, e.g. 'Emit audit events...' - not a verdict gate).
    """
    lowered = rule_text.strip().lower()
    if lowered.startswith(REJECT_PREFIXES):
        return "REJECT"
    if lowered.startswith(ESCALATE_PREFIXES):
        return "ESCALATE"
    return None


class OrganismRulebook:
    """Loads business_rules per organism and classifies them once, so the
    engine can ask 'does pattern X violate a hard rule for organism Y'.
    """

    def __init__(self, client_root: str | Path | None):
        self.rules_by_slug: dict[str, list[dict[str, str]]] = {}

        if not client_root:
            return

        organisms_dir = Path(client_root) / "10_swarm" / "organisms"
        if not organisms_dir.exists():
            return

        for organism_dir in sorted(organisms_dir.iterdir()):
            profile_file = organism_dir / "siop_internal.json"
            if not profile_file.exists():
                continue
            profile = read_json(profile_file, {})
            rules = profile.get("business_rules", [])

            classified = []
            for rule_text in rules:
                rule_class = classify_rule(rule_text)
                if rule_class:
                    classified.append({"text": rule_text, "class": rule_class})

            if classified:
                self.rules_by_slug[organism_dir.name] = classified

    @property
    def loaded(self) -> bool:
        return bool(self.rules_by_slug)

    def check(self, pattern_name: str, organism_slugs: list[str]) -> tuple[str, str] | None:
        """Returns (rule_class, matched_rule_text) for the first hard rule
        whose subject keywords match this pattern_name, across all affected
        organisms. REJECT-class rules are checked before ESCALATE-class so
        the strongest applicable veto wins.
        """
        keywords = PATTERN_SUBJECT_KEYWORDS.get(pattern_name, [])
        if not keywords:
            return None

        candidates: list[tuple[str, str, str]] = []  # (slug, class, text)
        for slug in organism_slugs:
            for rule in self.rules_by_slug.get(slug, []):
                rule_lower = rule["text"].lower()
                if any(kw in rule_lower for kw in keywords):
                    candidates.append((slug, rule["class"], rule["text"]))

        for slug, rule_class, text in candidates:
            if rule_class == "REJECT":
                return ("REJECT", f"organism:{slug} rule:'{text}'")
        for slug, rule_class, text in candidates:
            if rule_class == "ESCALATE":
                return ("ESCALATE", f"organism:{slug} rule:'{text}'")
        return None


@dataclass
class ComplianceReview:
    decision_id: str
    prescription_id: str
    pattern_name: str
    original_verdict: str
    final_verdict: str
    overridden: bool
    override_reason: str
    reviewed_at: str


class ComplianceEngine:
    def __init__(
        self,
        decisions_root: str | Path = "agentic_shield/decisions",
        state_root: str | Path = "agentic_shield/state",
        client_root: str | Path | None = None,
    ):
        self.decisions_root = Path(decisions_root)
        self.state_root = Path(state_root)

        self.shield_decisions_file = self.decisions_root / "shield_decisions.json"
        self.compliance_review_file = self.decisions_root / "compliance_review.json"
        self.violations_log = self.decisions_root / "compliance_violations.jsonl"
        self.state_file = self.state_root / "compliance_engine_state.json"

        self.rulebook = OrganismRulebook(client_root)

    # Verdicts ordered by how restrictive they are; a review can only move
    # a decision rightward (more restrictive), never left.
    VERDICT_ORDER = ["APPROVE", "SANDBOX", "ESCALATE", "REJECT"]

    def more_restrictive(self, candidate: str, current: str) -> bool:
        return self.VERDICT_ORDER.index(candidate) > self.VERDICT_ORDER.index(current)

    def review(self, decision: dict[str, Any]) -> ComplianceReview:
        pattern_name = decision.get("pattern_name", "")
        original_verdict = decision.get("verdict", "SANDBOX")
        affected = decision.get("affected_organisms", []) or []
        organism_slugs = [organism_to_slug(o) for o in affected]

        final_verdict = original_verdict
        overridden = False
        override_reason = ""

        match = self.rulebook.check(pattern_name, organism_slugs)
        if match:
            rule_class, rule_text = match
            if self.more_restrictive(rule_class, original_verdict):
                final_verdict = rule_class
                overridden = True
                override_reason = f"Hard business rule veto: {rule_text}"

                # rule_text carries 'organism:<SLUG> rule:...' as produced by
                # OrganismRulebook.check(); extract the slug that actually
                # matched so downstream consumers (threshold_engine.py) don't
                # have to re-parse free text to know which organism this was.
                matched_slug = ""
                if rule_text.startswith("organism:"):
                    matched_slug = rule_text.split(" ", 1)[0].split(":", 1)[1]

                append_jsonl(
                    self.violations_log,
                    {
                        "timestamp": now(),
                        "decision_id": decision.get("decision_id", ""),
                        "prescription_id": decision.get("prescription_id", ""),
                        "pattern_name": pattern_name,
                        "organism_slug": matched_slug,
                        "original_verdict": original_verdict,
                        "final_verdict": final_verdict,
                        "rule": rule_text,
                    },
                )

        return ComplianceReview(
            decision_id=decision.get("decision_id", ""),
            prescription_id=decision.get("prescription_id", ""),
            pattern_name=pattern_name,
            original_verdict=original_verdict,
            final_verdict=final_verdict,
            overridden=overridden,
            override_reason=override_reason,
            reviewed_at=now(),
        )

    def run(self) -> dict[str, Any]:
        shield_payload = read_json(self.shield_decisions_file, {"decisions": []})
        decisions = shield_payload.get("decisions", [])

        reviews: list[ComplianceReview] = []
        for decision in decisions:
            reviews.append(self.review(decision))

        overridden_count = sum(1 for r in reviews if r.overridden)
        final_verdict_counts: dict[str, int] = {}
        for r in reviews:
            final_verdict_counts[r.final_verdict] = final_verdict_counts.get(r.final_verdict, 0) + 1

        payload = {
            "reviewed_at": now(),
            "decisions_reviewed": len(reviews),
            "overridden_count": overridden_count,
            "final_verdict_counts": final_verdict_counts,
            "rulebook_loaded": self.rulebook.loaded,
            "reviews": [asdict(r) for r in reviews],
        }
        write_json(self.compliance_review_file, payload)

        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "compliance_engine",
                "status": "COMPLIANCE_ENGINE_ACTIVE",
                "decisions_reviewed": len(reviews),
                "overridden_count": overridden_count,
                "final_verdict_counts": final_verdict_counts,
                "rulebook_loaded": self.rulebook.loaded,
                "next_step": "Run approval_engine.py for APPROVE/SANDBOX, human_accountability.py for ESCALATE/REJECT",
            },
        )

        return payload


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Agentic Shield Compliance Engine")
    parser.add_argument("--decisions-root", default="agentic_shield/decisions")
    parser.add_argument("--state-root", default="agentic_shield/state")
    parser.add_argument("--client-root", default="", help="Client package root, for organism-level business_rules")
    parser.add_argument("--review", action="store_true", help="Run a compliance review pass over current shield decisions")
    args = parser.parse_args()

    engine = ComplianceEngine(
        decisions_root=args.decisions_root,
        state_root=args.state_root,
        client_root=args.client_root or None,
    )

    result = engine.run()

    print("\nAgentic Shield Compliance Engine complete")
    print(f"Decisions reviewed: {result['decisions_reviewed']}")
    print(f"Overridden:         {result['overridden_count']}")
    print(f"Rulebook loaded:    {result['rulebook_loaded']}")
    print("Final verdicts:")
    for verdict, count in result["final_verdict_counts"].items():
        print(f"  {verdict}: {count}")

    print("\nOutput:")
    print(f"  compliance_review: {engine.compliance_review_file}")
    print(f"  violations_log:    {engine.violations_log}")
    print(f"  state:             {engine.state_file}")


if __name__ == "__main__":
    run_cli()
