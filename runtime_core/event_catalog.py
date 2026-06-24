"""
AGENTIC ZERO - RUNTIME CORE
Event Catalog v2.0

Role:
  Single source of truth for the event taxonomy consumed by EventRouter.
  Builds/normalizes event_catalog.json by DERIVING it from the real swarm
  topology (coordination/swarm_coordination_<process>.json), instead of a
  hand-maintained list. Falls back to a small seed of runtime-infra events
  (heartbeat/degradation/shield) that are not part of any client topology.

  Organism name -> target slug rule (matches 10_swarm/organisms/<SLUG>):
    "Demand Planning Organism" -> "DEMAND_PLANNING"

Input:
  coordination/swarm_coordination_<process>.json (organisms + event_routes)
  event_catalog.json (existing, optional - human overrides are preserved)

Output:
  event_catalog.json
  event_catalog_unknown.jsonl
  state/event_catalog_state.json
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Seed: runtime-infrastructure events emitted by runtime_core/ itself.
# These are NOT part of any client's business topology, so they can't be
# derived from a coordination file - they have to be seeded here once.
INFRA_EVENT_SEED: list[dict[str, Any]] = [
    {"event_name": "test_event", "category": "infra", "targets": ["pulse_aggregator"], "shield_required": False},
    {"event_name": "heartbeat_received", "category": "infra", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "heartbeat_unknown_organism", "category": "infra", "targets": ["health_manager", "degradation_manager"], "shield_required": True},
    {"event_name": "heartbeat_check_ok", "category": "infra", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "stale_organisms_detected", "category": "infra", "targets": ["health_manager", "degradation_manager"], "shield_required": True},
    {"event_name": "heartbeat_all_completed", "category": "infra", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "degradation_escalated", "category": "infra", "targets": ["health_manager", "the_machine.observer"], "shield_required": True},
    {"event_name": "degradation_recovered", "category": "infra", "targets": ["health_manager"], "shield_required": False},
    {"event_name": "event_routed", "category": "infra", "targets": ["the_machine.observer"], "shield_required": False},
    {"event_name": "shield_validation_requested", "category": "infra", "targets": ["agentic_shield.policy_engine"], "shield_required": True},
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


def organism_to_slug(organism_name: str) -> str:
    """'Demand Planning Organism' -> 'DEMAND_PLANNING' (matches 10_swarm/organisms/<SLUG>)."""
    name = re.sub(r"\s*Organism\s*$", "", organism_name.strip())
    slug = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()
    return slug


def derive_from_coordination(coordination: dict[str, Any]) -> list[dict[str, Any]]:
    """Build event definitions from a swarm_coordination_<process>.json file.

    Groups all event_routes sharing the same event_name and unions their
    'to' organisms into a single target list, since one upstream organism
    typically fans out to several downstream organisms under one event type.
    """
    shield_required_globally = bool(
        coordination.get("coordination_model", {}).get("shield_arbitration_required", True)
    )

    by_event: dict[str, dict[str, Any]] = {}
    for route in coordination.get("event_routes", []):
        event_name = route.get("event")
        if not event_name:
            continue
        target_slug = organism_to_slug(route.get("to", ""))
        origin_slug = organism_to_slug(route.get("from", ""))

        entry = by_event.setdefault(
            event_name,
            {
                "event_name": event_name,
                "category": "business",
                "origin": origin_slug,
                "targets": [],
                "shield_required": shield_required_globally,
            },
        )
        if target_slug and target_slug not in entry["targets"]:
            entry["targets"].append(target_slug)

    return sorted(by_event.values(), key=lambda e: e["event_name"])


class EventCatalog:
    def __init__(
        self,
        runtime_config_dir: str | Path,
        coordination_file: str | Path | None = None,
        events_dir: str | Path | None = None,
        state_root: str | Path = "runtime_core/state",
    ):
        self.runtime_config_dir = Path(runtime_config_dir)
        self.coordination_file = Path(coordination_file) if coordination_file else None
        self.events_dir = Path(events_dir) if events_dir else None
        self.state_root = Path(state_root)

        self.catalog_file = self.runtime_config_dir / "event_catalog.json"
        self.unknown_file = (
            (self.events_dir or self.runtime_config_dir) / "event_catalog_unknown.jsonl"
        )
        self.state_file = self.state_root / "event_catalog_state.json"

    def load_existing_overrides(self) -> dict[str, dict[str, Any]]:
        """Human-curated overrides already present in event_catalog.json.

        Only fields a curator is likely to hand-tune (targets, shield_required)
        are preserved; structural fields (category/origin) always come from
        the live topology so the catalog never drifts from reality.
        """
        existing = read_json(self.catalog_file, {"events": []})
        overrides = {}
        for e in existing.get("events", []):
            if e.get("source") == "human_override" and "event_name" in e:
                overrides[e["event_name"]] = e
        return overrides

    def normalize(self) -> dict[str, Any]:
        derived: list[dict[str, Any]] = list(INFRA_EVENT_SEED)
        topology_source = None

        if self.coordination_file and self.coordination_file.exists():
            coordination = read_json(self.coordination_file, {})
            derived = derived + derive_from_coordination(coordination)
            topology_source = coordination.get("coordination_siop_id") or str(self.coordination_file.name)

        overrides = self.load_existing_overrides()
        merged: dict[str, dict[str, Any]] = {}
        for definition in derived:
            merged[definition["event_name"]] = dict(definition)
        for name, override in overrides.items():
            if name in merged:
                merged[name].update(
                    {k: v for k, v in override.items() if k in ("targets", "shield_required")}
                )
                merged[name]["source"] = "human_override"

        catalog = {
            "version": now(),
            "derived_from": topology_source,
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
                "derived_from": catalog.get("derived_from"),
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
    parser.add_argument(
        "--coordination-file",
        default="",
        help="Path to coordination/swarm_coordination_<process>.json to derive the catalog from",
    )
    parser.add_argument("--events-dir", default="", help="Optional events dir to validate streams against the catalog")
    parser.add_argument("--state-root", default="runtime_core/state")
    parser.add_argument("--normalize", action="store_true", help="Build/normalize the catalog")
    args = parser.parse_args()

    catalog = EventCatalog(
        runtime_config_dir=args.runtime_config_dir,
        coordination_file=args.coordination_file or None,
        events_dir=args.events_dir or None,
        state_root=args.state_root,
    )

    result = catalog.run()
    events = result["catalog"]["events"]
    validation = result["validation"]

    print("\nAgentic Zero Event Catalog complete")
    print(f"Derived from:             {result['catalog'].get('derived_from')}")
    print(f"Event types cataloged:    {len(events)}")
    print(f"Known event types:        {validation['known_event_types']}")
    print(f"Unknown event types seen: {len(validation['unknown_event_types'])}")
    if validation["unknown_event_types"]:
        for et in validation["unknown_event_types"]:
            print(f"  - {et}")
    print("\nOutput:")
    print(f"  event_catalog: {catalog.catalog_file}")
    print(f"  unknown_log:   {catalog.unknown_file}")
    print(f"  state:         {catalog.state_file}")


if __name__ == "__main__":
    run_cli()
