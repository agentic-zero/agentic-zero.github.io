"""
AGENTIC ZERO - RUNTIME CORE
Pulse Aggregator v1.0

Role:
  Aggregate runtime event streams into an enterprise health snapshot.

Input:
  swarm_events.jsonl
  audit_events.jsonl
  learning_events.jsonl
  shield_events.jsonl
  pulse_events.jsonl

Output:
  enterprise_health.json
  pulse_summary.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class PulseSnapshot:
    snapshot_id: str
    created_at: str
    event_dir: str
    health: int
    risk: int
    autonomy: int
    confidence: int
    active_events: int
    learning_events: int
    shield_blocks: int
    human_interventions: int
    status: str
    recommendation: str
    outputs: dict[str, str]
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def event_confidence(events: list[dict[str, Any]]) -> int:
    values = []
    for e in events:
        if isinstance(e.get("confidence"), (int, float)):
            values.append(float(e["confidence"]))
        elif isinstance(e.get("payload"), dict) and isinstance(
            e["payload"].get("confidence"), (int, float)
        ):
            values.append(float(e["payload"]["confidence"]))
    if not values:
        return 88
    avg = sum(values) / len(values)
    if avg <= 1:
        avg *= 100
    return clamp(avg)


def event_risk(events: list[dict[str, Any]]) -> int:
    values = []
    for e in events:
        if isinstance(e.get("risk_score"), (int, float)):
            values.append(float(e["risk_score"]))
        elif isinstance(e.get("payload"), dict) and isinstance(
            e["payload"].get("risk_score"), (int, float)
        ):
            values.append(float(e["payload"]["risk_score"]))
    if not values:
        return 18
    avg = sum(values) / len(values)
    if avg <= 1:
        avg *= 100
    return clamp(avg)


def count_contains(events: list[dict[str, Any]], terms: list[str]) -> int:
    total = 0
    for e in events:
        raw = json.dumps(e, ensure_ascii=False).lower()
        if any(t.lower() in raw for t in terms):
            total += 1
    return total


def build_snapshot(event_dir: str | Path) -> PulseSnapshot:
    event_dir = Path(event_dir)

    swarm_events = read_jsonl(event_dir / "swarm_events.jsonl")
    audit_events = read_jsonl(event_dir / "audit_events.jsonl")
    learning_events = read_jsonl(event_dir / "learning_events.jsonl")
    shield_events = read_jsonl(event_dir / "shield_events.jsonl")
    pulse_events = read_jsonl(event_dir / "pulse_events.jsonl")

    all_events = (
        swarm_events + audit_events + learning_events + shield_events + pulse_events
    )

    active_events = len(swarm_events)
    learning_count = len(learning_events)
    shield_blocks = count_contains(
        shield_events + all_events, ["blocked", "shield_blocked", "blocked_action"]
    )
    human_interventions = count_contains(
        all_events, ["human", "approval_required", "human_override", "manual"]
    )

    confidence = event_confidence(all_events)
    risk = event_risk(all_events)

    # Autonomy falls with human intervention and shield blocks,
    # but rises when learning is present and events are flowing.
    autonomy = 84
    autonomy -= human_interventions * 4
    autonomy -= shield_blocks * 5
    autonomy += min(learning_count, 5)
    autonomy = clamp(autonomy)

    # Health is a combined operational pulse.
    health = 96
    health -= risk * 0.35
    health -= shield_blocks * 5
    health -= human_interventions * 3
    health += min(learning_count, 4)
    health = clamp(health)

    if health >= 90 and risk <= 25:
        status = "NORMAL"
        recommendation = "Enterprise pulse is stable. Continue monitoring."
    elif health >= 75:
        status = "DEGRADED"
        recommendation = "Monitor active risks and validate pending recommendations."
    else:
        status = "ATTENTION_REQUIRED"
        recommendation = (
            "Review Shield events, human interventions and high-risk signals."
        )

    output_health = event_dir / "enterprise_health.json"
    output_summary = event_dir / "pulse_summary.json"

    snapshot = PulseSnapshot(
        snapshot_id=f"PULSE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        event_dir=str(event_dir),
        health=health,
        risk=risk,
        autonomy=autonomy,
        confidence=confidence,
        active_events=active_events,
        learning_events=learning_count,
        shield_blocks=shield_blocks,
        human_interventions=human_interventions,
        status=status,
        recommendation=recommendation,
        outputs={
            "enterprise_health": str(output_health),
            "pulse_summary": str(output_summary),
        },
    )

    write_json(output_health, asdict(snapshot))
    write_json(
        output_summary,
        {
            "status": status,
            "health": health,
            "risk": risk,
            "autonomy": autonomy,
            "confidence": confidence,
            "signals": {
                "active_events": active_events,
                "learning_events": learning_count,
                "shield_blocks": shield_blocks,
                "human_interventions": human_interventions,
            },
            "recommendation": recommendation,
            "updated_at": snapshot.created_at,
        },
    )

    return snapshot


def run_cli(event_dir: str):
    snapshot = build_snapshot(event_dir)

    print("\nPulse Aggregator complete")
    print(f"Status:     {snapshot.status}")
    print(f"Health:     {snapshot.health}%")
    print(f"Risk:       {snapshot.risk}%")
    print(f"Autonomy:   {snapshot.autonomy}%")
    print(f"Confidence: {snapshot.confidence}%")

    print("\nSignals:")
    print(f"  Active events:       {snapshot.active_events}")
    print(f"  Learning events:     {snapshot.learning_events}")
    print(f"  Shield blocks:       {snapshot.shield_blocks}")
    print(f"  Human interventions: {snapshot.human_interventions}")

    print("\nOutput:")
    for k, v in snapshot.outputs.items():
        print(f"  {k}: {v}")

    return snapshot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Pulse Aggregator")
    parser.add_argument(
        "--event-dir", required=True, help="Directory containing runtime event streams"
    )
    args = parser.parse_args()

    run_cli(args.event_dir)
