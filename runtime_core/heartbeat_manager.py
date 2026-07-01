"""
AGENTIC ZERO - RUNTIME CORE
Heartbeat Manager v1.0

Role:
  Keep runtime organisms alive by updating heartbeat status,
  detecting stale organisms, and emitting health events.

Input:
  runtime_registry.json

Output:
  runtime_registry.json
  runtime_status.json
  heartbeat_events.jsonl
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STATES = ["RUNNING", "WAITING", "DEGRADED", "STOPPED"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def read_json(path: Path, default: Any):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


class HeartbeatManager:
    def __init__(self, root_dir: str | Path, stale_seconds: int = 300):
        self.root_dir = Path(root_dir)
        self.registry_file = self.root_dir / "runtime_registry.json"
        self.status_file = self.root_dir / "runtime_status.json"
        self.events_file = self.root_dir / "heartbeat_events.jsonl"
        self.stale_seconds = stale_seconds
        self.registry = read_json(self.registry_file, {})

    def save(self):
        write_json(self.registry_file, self.registry)
        write_json(self.status_file, self.build_status())

    def emit(self, event_type: str, payload: dict[str, Any]):
        append_jsonl(
            self.events_file,
            {
                "timestamp": now(),
                "source": "HeartbeatManager",
                "event_type": event_type,
                "payload": payload,
            },
        )

    def heartbeat(self, organism_id: str):
        if organism_id not in self.registry:
            self.emit("heartbeat_unknown_organism", {"organism_id": organism_id})
            return False

        record = self.registry[organism_id]
        record["last_heartbeat"] = now()
        record["events_processed"] = int(record.get("events_processed", 0)) + 1

        if record.get("state") in ["STOPPED", "DEGRADED"]:
            record["state"] = "RUNNING"

        self.emit(
            "heartbeat_received",
            {
                "organism_id": organism_id,
                "organism_name": record.get("organism_name", organism_id),
                "state": record.get("state"),
            },
        )

        self.save()
        return True

    def check_stale(self):
        current = datetime.now(timezone.utc)
        stale = []

        for organism_id, record in self.registry.items():
            last = parse_time(record.get("last_heartbeat", ""))
            if not last:
                record["state"] = "DEGRADED"
                record["health"] = 50
                stale.append(organism_id)
                continue

            age = (current - last).total_seconds()

            if age > self.stale_seconds:
                record["state"] = "DEGRADED"
                record["health"] = max(30, int(record.get("health", 100)) - 20)
                record["human_intervention_required"] = True
                stale.append(organism_id)

        if stale:
            self.emit(
                "stale_organisms_detected",
                {
                    "stale_count": len(stale),
                    "organisms": stale,
                    "stale_seconds": self.stale_seconds,
                },
            )
        else:
            self.emit(
                "heartbeat_check_ok",
                {
                    "organisms_checked": len(self.registry),
                    "stale_seconds": self.stale_seconds,
                },
            )

        self.save()
        return stale

    def build_status(self):
        total = len(self.registry)
        running = sum(1 for x in self.registry.values() if x.get("state") == "RUNNING")
        waiting = sum(1 for x in self.registry.values() if x.get("state") == "WAITING")
        degraded = sum(
            1 for x in self.registry.values() if x.get("state") == "DEGRADED"
        )
        stopped = sum(1 for x in self.registry.values() if x.get("state") == "STOPPED")
        human = sum(
            1 for x in self.registry.values() if x.get("human_intervention_required")
        )

        runtime_health = round(
            ((running * 1.0) + (waiting * 0.8) + (degraded * 0.4))
            / max(total, 1)
            * 100,
            0,
        )

        return {
            "timestamp": now(),
            "total_organisms": total,
            "running": running,
            "waiting": waiting,
            "degraded": degraded,
            "stopped": stopped,
            "human_intervention_required": human,
            "runtime_health": runtime_health,
        }

    def heartbeat_all(self):
        for organism_id in list(self.registry.keys()):
            self.heartbeat(organism_id)

        self.emit(
            "heartbeat_all_completed",
            {
                "organisms": len(self.registry),
            },
        )

        self.save()


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Heartbeat Manager")
    parser.add_argument("--root-dir", required=True)
    parser.add_argument("--stale-seconds", type=int, default=300)
    parser.add_argument("--heartbeat", default="")
    parser.add_argument("--heartbeat-all", action="store_true")
    parser.add_argument("--check-stale", action="store_true")
    args = parser.parse_args()

    manager = HeartbeatManager(args.root_dir, args.stale_seconds)

    if args.heartbeat:
        ok = manager.heartbeat(args.heartbeat)
        print(f"Heartbeat {'OK' if ok else 'FAILED'}: {args.heartbeat}")

    if args.heartbeat_all:
        manager.heartbeat_all()
        print("Heartbeat all completed")

    if args.check_stale:
        stale = manager.check_stale()
        print(f"Stale organisms: {len(stale)}")
        for item in stale:
            print(f"  - {item}")

    print(f"Registry: {manager.registry_file}")
    print(f"Status:   {manager.status_file}")
    print(f"Events:   {manager.events_file}")


if __name__ == "__main__":
    run_cli()
