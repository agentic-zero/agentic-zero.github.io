"""
AGENTIC ZERO - RUNTIME CORE
Event Catalog v1.0

Role:
  Single source of truth for the event taxonomy consumed by EventRouter.
  Builds/normalizes event_catalog.json (event_name, targets,
  shield_required) and validates real event streams against it, flagging
  event types that would otherwise route to NO_TARGET.

Input:
  event_catalog.json (existing, optional)
  swarm_events.jsonl / learning_events.jsonl / shield_events.jsonl (optional, for validation)

Output:
  event_catalog.json
  event_catalog_unknown.jsonl
  state/event_catalog_state.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Canonical event taxonomy known to be emitted by runtime_core/ and
# the_machine/. New event types should be added here as modules evolve;
# event_catalog.py is the only place this list should be edited.
CANONICAL_EVENTS: list[dict[str, Any]] = [
    {"event_name": "test_event", "category": "swarm", "targets": ["pulse_aggregator"], "shield_required": False},
    {"event_name": "heartbeat_received", "category": "runtime", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "heartbeat_unknown_organism", "category": "runtime", "targets": ["health_manager", "degradation_manager"], "shield_required": True},
    {"event_name": "heartbeat_check_ok", "category": "runtime", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "stale_organisms_detected", "category": "runtime", "targets": ["health_manager", "degradation_manager"], "shield_required": True},
    {"event_name": "heartbeat_all_completed", "category": "runtime", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "degradation_escalated", "category": "runtime", "targets": ["health_manager", "the_machine.observer"], "shield_required": True},
    {"event_name": "degradation_recovered", "category": "runtime", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "event_routed", "category": "routing", "targets": ["the_machine.observer"], "shield_required": False},
    {"event_name": "shield_validation_requested", "category": "shield", "targets": ["agentic_shield.policy_engine"], "shield_required": True},
    {"event_name": "demand_planning_updated", "category": "sop", "targets": ["swarm_coordinator", "the_machine.observer"], "shield_required": True},
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


class EventCatalog:
    def __init__(
        self,
        runtime_config_dir: str | Path,
        events_dir: str | Path | None = None,
        state_root: str | Path = "runtime_core/state",
    ):
        self.runtime_config_dir = Path(runtime_config_dir)
        self.events_dir = Path(events_dir) if events_dir else None
        self.state_root = Path(state_root)

        self.catalog_file = self.runtime_config_dir / "event_catalog.json"
        self.unknown_file = (
            (self.events_dir or self.runtime_config_dir) / "event_catalog_unknown.jsonl"
        )
        self.state_file = self.state_root / "event_catalog_state.json"

    def load_existing(self) -> dict[str, dict[str, Any]]:
        existing = read_json(self.catalog_file, {"events": []})
        return {e["event_name"]: e for e in existing.get("events", []) if "event_name" in e}

    def normalize(self) -> dict[str, Any]:
        existing_by_name = self.load_existing()

        merged: dict[str, dict[str, Any]] = {}
        for definition in CANONICAL_EVENTS:
            merged[definition["event_name"]] = dict(definition)

        # Preserve any custom targets/flags a human curator already added
        # for a known event, without losing canonical defaults for new ones.
        for name, definition in existing_by_name.items():
            if name in merged:
                merged[name].update(
                    {k: v for k, v in definition.items() if k not in ("event_name",)}
                )
            else:
                merged[name] = definition

        catalog = {
            "version": now(),
            "events": sorted(merged.values(), key=lambda e: e["event_name"]),
        }

        write_json(self.catalog_file, catalog)
        return catalog

    def validate_streams(self, catalog: dict[str, Any]) -> dict[str, Any]:
        known = {e["event_name"] for e in catalog.get("events", [])}
        unknown_seen: dict[str, int] = {}

        if self.events_dir:
            for stream_name in ["swarm_events.jsonl", "learning_events.jsonl", "shield_events.jsonl", "pulse_events.jsonl"]:
                for event in read_jsonl(self.events_dir / stream_name):
                    event_type = event.get("event_type") or event.get("event_name")
                    if event_type and event_type not in known:
                        unknown_seen[event_type] = unknown_seen.get(event_type, 0) + 1
                        append_jsonl(
                            self.unknown_file,
                            {
                                "timestamp": now(),
                                "stream": stream_name,
                                "event_type": event_type,
                                "source": event.get("source", "unknown"),
                            },
                        )

        return {
            "known_event_types": len(known),
            "unknown_event_types": list(unknown_seen.keys()),
            "unknown_occurrences": sum(unknown_seen.values()),
        }

    def run(self) -> dict[str, Any]:
        catalog = self.normalize()
        validation = self.validate_streams(catalog)

        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "event_catalog",
                "status": "EVENT_CATALOG_NORMALIZED",
                "event_types_cataloged": len(catalog.get("events", [])),
                **validation,
            },
        )

        return {"catalog": catalog, "validation": validation}


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Event Catalog")
    parser.add_argument(
        "--runtime-config-dir",
        required=True,
        help="Directory where event_catalog.json lives (e.g. <client>/10_swarm/runtime)",
    )
    parser.add_argument("--events-dir", default="", help="Optional events dir to validate streams against the catalog")
    parser.add_argument("--state-root", default="runtime_core/state")
    parser.add_argument("--normalize", action="store_true", help="Build/normalize the catalog")
    args = parser.parse_args()

    catalog = EventCatalog(
        runtime_config_dir=args.runtime_config_dir,
        events_dir=args.events_dir or None,
        state_root=args.state_root,
    )

    result = catalog.run()
    events = result["catalog"]["events"]
    validation = result["validation"]

    print("\nAgentic Zero Event Catalog complete")
    print(f"Event types cataloged:   {len(events)}")
    print(f"Known event types:       {validation['known_event_types']}")
    print(f"Unknown event types seen:{len(validation['unknown_event_types'])}")
    if validation["unknown_event_types"]:
        for et in validation["unknown_event_types"]:
            print(f"  - {et}")
    print("\nOutput:")
    print(f"  event_catalog: {catalog.catalog_file}")
    print(f"  unknown_log:   {catalog.unknown_file}")
    print(f"  state:         {catalog.state_file}")


if __name__ == "__main__":
    run_cli()
