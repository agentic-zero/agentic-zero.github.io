"""
AGENTIC ZERO - RUNTIME CORE
Degradation Manager v1.0

Role:
  Detect, track and escalate degradation of runtime organisms over time.
  Distinguishes a transient blip from a persistent degradation pattern,
  and raises escalation flags for human accountability when an organism
  remains degraded across multiple consecutive checks.

Input:
  runtime_registry.json

Output:
  degradation_status.json
  degradation_history.jsonl
  state/degradation_manager_state.json
"""

from __future__ import annotations

import argparse
import json
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


class DegradationManager:
    def __init__(
        self,
        runtime_dir: str | Path,
        state_root: str | Path = "runtime_core/state",
        escalate_after_strikes: int = 3,
    ):
        self.runtime_dir = Path(runtime_dir)
        self.registry_file = self.runtime_dir / "runtime_registry.json"

        self.status_file = self.runtime_dir / "degradation_status.json"
        self.history_file = self.runtime_dir / "degradation_history.jsonl"
        self.state_root = Path(state_root)
        self.state_file = self.state_root / "degradation_manager_state.json"
        self.tracker_file = self.state_root / "degradation_tracker.json"

        self.escalate_after_strikes = escalate_after_strikes
        self.registry = read_json(self.registry_file, {})
        self.tracker = read_json(self.tracker_file, {})

    def detect(self) -> dict[str, Any]:
        degraded_now = []
        recovered = []
        escalated = []

        for organism_id, record in self.registry.items():
            state = record.get("state", "UNKNOWN")
            entry = self.tracker.get(organism_id, {"strikes": 0, "first_seen": "", "escalated": False})

            if state == "DEGRADED":
                entry["strikes"] = int(entry.get("strikes", 0)) + 1
                if not entry.get("first_seen"):
                    entry["first_seen"] = now()
                entry["last_seen"] = now()
                degraded_now.append(organism_id)

                append_jsonl(
                    self.history_file,
                    {
                        "timestamp": now(),
                        "organism_id": organism_id,
                        "organism_name": record.get("organism_name", organism_id),
                        "state": state,
                        "strikes": entry["strikes"],
                        "health": record.get("health"),
                    },
                )

                if entry["strikes"] >= self.escalate_after_strikes and not entry.get("escalated"):
                    entry["escalated"] = True
                    record["human_intervention_required"] = True
                    escalated.append(organism_id)
                    append_jsonl(
                        self.history_file,
                        {
                            "timestamp": now(),
                            "organism_id": organism_id,
                            "organism_name": record.get("organism_name", organism_id),
                            "event_type": "degradation_escalated",
                            "strikes": entry["strikes"],
                            "escalate_after_strikes": self.escalate_after_strikes,
                        },
                    )
            else:
                if entry.get("strikes", 0) > 0:
                    recovered.append(organism_id)
                    append_jsonl(
                        self.history_file,
                        {
                            "timestamp": now(),
                            "organism_id": organism_id,
                            "organism_name": record.get("organism_name", organism_id),
                            "event_type": "degradation_recovered",
                            "strikes_before_recovery": entry.get("strikes", 0),
                        },
                    )
                entry = {"strikes": 0, "first_seen": "", "escalated": False}

            self.tracker[organism_id] = entry

        write_json(self.tracker_file, self.tracker)
        write_json(self.registry_file, self.registry)

        status = {
            "timestamp": now(),
            "total_organisms": len(self.registry),
            "currently_degraded": degraded_now,
            "recovered_this_pass": recovered,
            "escalated_this_pass": escalated,
            "escalate_after_strikes": self.escalate_after_strikes,
        }

        write_json(self.status_file, status)
        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "degradation_manager",
                "status": "DEGRADATION_DETECTION_ACTIVE",
                "degraded_count": len(degraded_now),
                "escalated_count": len(escalated),
            },
        )

        return status


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Degradation Manager")
    parser.add_argument("--root-dir", required=True, help="Runtime directory")
    parser.add_argument("--state-root", default="runtime_core/state")
    parser.add_argument("--escalate-after-strikes", type=int, default=3)
    parser.add_argument("--detect", action="store_true", help="Run a degradation detection pass")
    args = parser.parse_args()

    manager = DegradationManager(
        runtime_dir=args.root_dir,
        state_root=args.state_root,
        escalate_after_strikes=args.escalate_after_strikes,
    )

    status = manager.detect()

    print("\nAgentic Zero Degradation Manager complete")
    print(f"Currently degraded: {len(status['currently_degraded'])}")
    print(f"Recovered:          {len(status['recovered_this_pass'])}")
    print(f"Escalated:          {len(status['escalated_this_pass'])}")
    print("\nOutput:")
    print(f"  degradation_status:  {manager.status_file}")
    print(f"  degradation_history: {manager.history_file}")
    print(f"  state:               {manager.state_file}")


if __name__ == "__main__":
    run_cli()
