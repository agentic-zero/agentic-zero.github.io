"""
AGENTIC ZERO - THE MACHINE
Pattern Detector v1.0

Role:
  Read episodic memory and observed patterns.
  Detect repeated runtime/factory patterns that may require prescription.

Input:
  memory/episodic/episodic_memory.jsonl
  memory/semantic/observed_patterns.json

Output:
  memory/semantic/detected_patterns.json
  the_machine/state/pattern_detector_state.json
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


def append_jsonl(path: Path, payload: dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


@dataclass
class DetectedPattern:
    pattern_id: str
    pattern_name: str
    count: int
    severity: str
    avg_risk: float
    avg_confidence: float
    affected_organisms: list[str]
    affected_streams: list[str]
    first_seen: str
    last_seen: str
    prescription_required: bool
    recommended_next_step: str


class PatternDetector:
    def __init__(
        self,
        memory_root: str | Path = "memory",
        state_root: str | Path = "the_machine/state",
        min_count: int = 2,
    ):
        self.memory_root = Path(memory_root)
        self.state_root = Path(state_root)
        self.min_count = min_count

        self.episodic_file = self.memory_root / "episodic" / "episodic_memory.jsonl"
        self.observed_patterns_file = (
            self.memory_root / "semantic" / "observed_patterns.json"
        )
        self.detected_patterns_file = (
            self.memory_root / "semantic" / "detected_patterns.json"
        )
        self.state_file = self.state_root / "pattern_detector_state.json"

    def emit_test_episode(self) -> dict[str, Any]:
        """Inject ONE synthetic episode directly into episodic_memory.jsonl,
        in the same shape observer.py would produce for a real
        missing_context failure on Demand Planning. This exists so the
        smoke test can exercise the full downstream chain (detect ->
        prescribe -> Shield decide/comply/calibrate/approve/escalate/audit)
        with real code paths end to end, instead of Shield always seeing
        zero prescriptions in a clean run and nobody noticing if it breaks.

        Uses pattern_candidate='missing_context' because it is one of the
        few patterns requires_prescription() treats as prescription-worthy
        even at count=1 (matching the smoke test's --min-count 1).
        """
        episode = {
            "episode_id": f"EP-TEST-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now(),
            "source_stream": "swarm",
            "source": "PatternDetectorSmokeTest",
            "event_type": "demand_planning_agent_exception",
            "organism": "Demand Planning Organism",
            "process_id": "TEST-SCENARIO",
            "outcome": "negative",
            "confidence": 0.62,
            "risk_score": 0.35,
            "requires_human": False,
            "requires_shield": False,
            "learning_relevant": True,
            "pattern_candidate": "missing_context",
            "grounded": False,
            "matched_observation_point": False,
            "payload": {
                "note": "Synthetic smoke-test episode: incomplete upstream context on Demand Planning."
            },
        }
        append_jsonl(self.episodic_file, episode)
        return episode

    def severity_for(
        self, pattern_name: str, count: int, avg_risk: float, avg_confidence: float
    ) -> str:
        critical_patterns = {
            "shield_blocked_action",
            "high_risk",
            "human_intervention",
            "stale_organism",
        }

        high_patterns = {
            "missing_context",
            "organism_conflict",
            "unrouted_event",
            "low_confidence",
        }

        if pattern_name in critical_patterns and count >= 2:
            return "CRITICAL"

        if pattern_name in high_patterns and count >= 3:
            return "HIGH"

        if avg_risk >= 0.70:
            return "CRITICAL"

        if avg_risk >= 0.45 or avg_confidence < 0.70:
            return "HIGH"

        if count >= 5:
            return "MEDIUM"

        return "LOW"

    def requires_prescription(
        self, pattern_name: str, severity: str, count: int
    ) -> bool:
        if pattern_name == "normal_operation":
            return False
        if severity in ["CRITICAL", "HIGH"]:
            return True
        if count >= self.min_count and pattern_name in [
            "missing_context",
            "organism_conflict",
            "unrouted_event",
            "low_confidence",
            "human_intervention",
            "stale_organism",
        ]:
            return True
        return False

    def detect(self) -> dict[str, Any]:
        episodes = read_jsonl(self.episodic_file)
        observed = read_json(self.observed_patterns_file, {"patterns": {}})

        grouped: dict[str, list[dict[str, Any]]] = {}

        for ep in episodes:
            name = ep.get("pattern_candidate", "unknown")
            grouped.setdefault(name, []).append(ep)

        detected: list[DetectedPattern] = []

        for pattern_name, items in grouped.items():
            count = len(items)
            if count < self.min_count and pattern_name != "normal_operation":
                continue

            risks = [float(x.get("risk_score", 0.0)) for x in items]
            confs = [float(x.get("confidence", 0.88)) for x in items]

            avg_risk = round(sum(risks) / max(len(risks), 1), 4)
            avg_confidence = round(sum(confs) / max(len(confs), 1), 4)

            organisms = sorted(set(x.get("organism", "unknown") for x in items))
            streams = sorted(set(x.get("source_stream", "unknown") for x in items))

            times = [x.get("created_at", "") for x in items if x.get("created_at")]
            first_seen = min(times) if times else ""
            last_seen = max(times) if times else ""

            severity = self.severity_for(pattern_name, count, avg_risk, avg_confidence)
            prescription_required = self.requires_prescription(
                pattern_name, severity, count
            )

            detected.append(
                DetectedPattern(
                    pattern_id=f"PAT-{pattern_name.upper().replace('-', '_')}-{count}",
                    pattern_name=pattern_name,
                    count=count,
                    severity=severity,
                    avg_risk=avg_risk,
                    avg_confidence=avg_confidence,
                    affected_organisms=organisms,
                    affected_streams=streams,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    prescription_required=prescription_required,
                    recommended_next_step=(
                        "Run prescriptor.py"
                        if prescription_required
                        else "Continue observation"
                    ),
                )
            )

        detected.sort(
            key=lambda x: (
                {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(x.severity, 0),
                x.count,
            ),
            reverse=True,
        )

        payload = {
            "detected_at": now(),
            "episodes_read": len(episodes),
            "observed_patterns_source": str(self.observed_patterns_file),
            "min_count": self.min_count,
            "patterns": [asdict(x) for x in detected],
            "prescription_required": any(x.prescription_required for x in detected),
            "next_step": "Run prescriptor.py"
            if any(x.prescription_required for x in detected)
            else "Continue observation",
        }

        write_json(self.detected_patterns_file, payload)

        state = {
            "updated_at": now(),
            "status": "patterns_detected",
            "episodes_read": len(episodes),
            "patterns_detected": len(detected),
            "prescription_required": payload["prescription_required"],
            "detected_patterns": str(self.detected_patterns_file),
            "next_step": payload["next_step"],
        }

        write_json(self.state_file, state)

        return {
            "patterns_detected": len(detected),
            "prescription_required": payload["prescription_required"],
            "output": str(self.detected_patterns_file),
            "state": str(self.state_file),
            "top_patterns": [asdict(x) for x in detected[:5]],
        }


def run_cli():
    parser = argparse.ArgumentParser(
        description="Agentic Zero - The Machine Pattern Detector"
    )
    parser.add_argument("--memory-root", default="memory")
    parser.add_argument("--state-root", default="the_machine/state")
    parser.add_argument("--min-count", type=int, default=2)
    parser.add_argument(
        "--emit-test",
        action="store_true",
        help="Inject one synthetic missing_context episode before detecting, so downstream prescriptor.py/Shield have a real case to process",
    )
    args = parser.parse_args()

    detector = PatternDetector(
        memory_root=args.memory_root,
        state_root=args.state_root,
        min_count=args.min_count,
    )

    if args.emit_test:
        test_episode = detector.emit_test_episode()
        print(f"\nSynthetic test episode emitted: {test_episode['episode_id']} (pattern_candidate=missing_context)")

    result = detector.detect()

    print("\nThe Machine Pattern Detector complete")
    print(f"Patterns detected:      {result['patterns_detected']}")
    print(f"Prescription required:  {result['prescription_required']}")

    print("\nTop patterns:")
    for p in result["top_patterns"]:
        print(f"  - {p['pattern_name']} | {p['severity']} | count={p['count']}")

    print("\nOutput:")
    print(f"  detected_patterns: {result['output']}")
    print(f"  state:             {result['state']}")


if __name__ == "__main__":
    run_cli()
