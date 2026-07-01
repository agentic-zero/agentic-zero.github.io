"""
AGENTIC ZERO - RUNTIME CORE
Event Router v1.0

Role:
  Route events between organisms, coordinator, Shield, Pulse and The Machine.

Input:
  event_bus streams
  swarm_topology_runtime.json
  event_catalog.json
  escalation_routes.json

Output:
  routed_events.jsonl
  routing_status.json
  routing_errors.jsonl
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
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def write_json(path: Path, payload: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


class EventRouter:
    def __init__(self, runtime_dir: str | Path):
        self.runtime_dir = Path(runtime_dir)

        self.events_dir = self.runtime_dir / "events"
        self.runtime_config_dir = self.runtime_dir.parent / "10_swarm" / "runtime"

        self.topology_file = self.runtime_config_dir / "swarm_topology_runtime.json"
        self.event_catalog_file = self.runtime_config_dir / "event_catalog.json"
        self.escalation_file = self.runtime_config_dir / "escalation_routes.json"

        self.swarm_events_file = self.events_dir / "swarm_events.jsonl"
        self.learning_events_file = self.events_dir / "learning_events.jsonl"
        self.shield_events_file = self.events_dir / "shield_events.jsonl"

        self.routed_events_file = self.events_dir / "routed_events.jsonl"
        self.routing_errors_file = self.events_dir / "routing_errors.jsonl"
        self.routing_status_file = self.events_dir / "routing_status.json"

        self.topology = read_json(self.topology_file, {})
        self.event_catalog = read_json(self.event_catalog_file, {})
        self.escalations = read_json(self.escalation_file, {})

    def event_definitions(self) -> list[dict[str, Any]]:
        return self.event_catalog.get("events", [])

    def find_targets(self, event_type: str) -> list[str]:
        for event in self.event_definitions():
            if event.get("event_name") == event_type:
                return event.get("targets", [])
        return []

    def requires_shield(self, event_type: str) -> bool:
        for event in self.event_definitions():
            if event.get("event_name") == event_type:
                return bool(event.get("shield_required", True))
        return False

    def route_event(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        event_type = event.get("event_type") or event.get("event_name")
        source = event.get("source", "unknown")
        payload = event.get("payload", {})

        targets = self.find_targets(event_type)

        routed = []

        if not targets:
            route = {
                "timestamp": now(),
                "route_status": "NO_TARGET",
                "source": source,
                "event_type": event_type,
                "target": None,
                "payload": payload,
                "original_event": event,
            }
            append_jsonl(self.routed_events_file, route)
            routed.append(route)
            return routed

        for target in targets:
            route = {
                "timestamp": now(),
                "route_status": "ROUTED",
                "source": source,
                "event_type": event_type,
                "target": target,
                "requires_shield": self.requires_shield(event_type),
                "payload": payload,
                "original_event": event,
            }

            append_jsonl(self.routed_events_file, route)
            routed.append(route)

            if route["requires_shield"]:
                append_jsonl(
                    self.shield_events_file,
                    {
                        "timestamp": now(),
                        "source": "EventRouter",
                        "event_type": "shield_validation_requested",
                        "payload": route,
                    },
                )

            append_jsonl(
                self.learning_events_file,
                {
                    "timestamp": now(),
                    "source": "EventRouter",
                    "event_type": "event_routed",
                    "payload": {
                        "source": source,
                        "target": target,
                        "event_type": event_type,
                    },
                },
            )

        return routed

    def route_all_unrouted(self) -> dict[str, Any]:
        events = read_jsonl(self.swarm_events_file)
        already = read_jsonl(self.routed_events_file)

        routed_ids = set()
        for r in already:
            original = r.get("original_event", {})
            if original.get("event_id"):
                routed_ids.add(original.get("event_id"))

        total = 0
        errors = 0
        routed_count = 0

        for event in events:
            total += 1

            if event.get("event_id") and event.get("event_id") in routed_ids:
                continue

            try:
                routes = self.route_event(event)
                routed_count += len(routes)
            except Exception as exc:
                errors += 1
                append_jsonl(
                    self.routing_errors_file,
                    {
                        "timestamp": now(),
                        "event": event,
                        "error": str(exc),
                    },
                )

        status = {
            "timestamp": now(),
            "events_seen": total,
            "routes_created": routed_count,
            "errors": errors,
            "topology_loaded": bool(self.topology),
            "event_catalog_loaded": bool(self.event_catalog),
            "status": "OK" if errors == 0 else "DEGRADED",
        }

        write_json(self.routing_status_file, status)
        return status

    def emit_test_event(self):
        event = {
            "event_id": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": now(),
            "source": "EventRouterSmokeTest",
            "event_type": "demand_planning_updated",
            "payload": {
                "scenario_id": "TEST-SCENARIO",
                "confidence_score": 0.91,
                "risk_score": 0.18,
            },
        }
        append_jsonl(self.swarm_events_file, event)
        return event


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Event Router")
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--emit-test", action="store_true")
    parser.add_argument("--route-all", action="store_true")
    args = parser.parse_args()

    router = EventRouter(args.runtime_dir)

    if args.emit_test:
        event = router.emit_test_event()
        print("Test event emitted:")
        print(json.dumps(event, indent=2, ensure_ascii=False))

    if args.route_all:
        status = router.route_all_unrouted()
        print("\nEvent Router complete")
        print(f"Status:        {status['status']}")
        print(f"Events seen:   {status['events_seen']}")
        print(f"Routes created:{status['routes_created']}")
        print(f"Errors:        {status['errors']}")
        print(f"\nOutput: {router.routing_status_file}")


if __name__ == "__main__":
    run_cli()
