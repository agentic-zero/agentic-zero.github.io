"""
AGENTIC ZERO - RUNTIME CORE
Runtime Registry v1.0

Role:
    Maintain the state of all active organisms in a swarm.

Outputs:
    runtime_registry.json
    runtime_status.json

States:
    RUNNING
    WAITING
    DEGRADED
    STOPPED
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path


VALID_STATES = ["RUNNING", "WAITING", "DEGRADED", "STOPPED"]


def now():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class OrganismRecord:
    organism_id: str
    organism_name: str
    state: str = "WAITING"
    last_heartbeat: str = ""
    dependencies: list[str] = field(default_factory=list)
    health: int = 100
    confidence: int = 95
    events_processed: int = 0
    human_intervention_required: bool = False


class RuntimeRegistry:
    def __init__(self, root_dir):

        self.root_dir = Path(root_dir)

        self.registry_file = self.root_dir / "runtime_registry.json"

        self.status_file = self.root_dir / "runtime_status.json"

        self.registry = {}

        self.load()

    def load(self):

        if self.registry_file.exists():
            self.registry = json.loads(self.registry_file.read_text(encoding="utf-8"))

    def save(self):

        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

        self.registry_file.write_text(
            json.dumps(self.registry, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        self.write_status()

    def add_organism(self, organism_name, dependencies=None):

        dependencies = dependencies or []

        record = OrganismRecord(
            organism_id=organism_name.lower().replace(" ", "_"),
            organism_name=organism_name,
            state="WAITING",
            last_heartbeat=now(),
            dependencies=dependencies,
        )

        self.registry[record.organism_id] = asdict(record)

    def update_state(self, organism_name, state):

        if state not in VALID_STATES:
            raise ValueError(f"Invalid state {state}")

        organism_id = organism_name.lower().replace(" ", "_")

        if organism_id not in self.registry:
            return

        self.registry[organism_id]["state"] = state

        self.registry[organism_id]["last_heartbeat"] = now()

    def heartbeat(self, organism_name):

        organism_id = organism_name.lower().replace(" ", "_")

        if organism_id not in self.registry:
            return

        self.registry[organism_id]["last_heartbeat"] = now()

        self.registry[organism_id]["events_processed"] += 1

    def write_status(self):

        total = len(self.registry)

        running = sum(1 for x in self.registry.values() if x["state"] == "RUNNING")

        degraded = sum(1 for x in self.registry.values() if x["state"] == "DEGRADED")

        waiting = sum(1 for x in self.registry.values() if x["state"] == "WAITING")

        stopped = sum(1 for x in self.registry.values() if x["state"] == "STOPPED")

        payload = {
            "timestamp": now(),
            "total_organisms": total,
            "running": running,
            "waiting": waiting,
            "degraded": degraded,
            "stopped": stopped,
            "runtime_health": round(
                (running + waiting * 0.8 + degraded * 0.4) / max(total, 1) * 100, 0
            ),
        }

        self.status_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def initialize_demo_registry(registry):

    registry.add_organism("Demand Planning Organism")

    registry.add_organism("Inventory Organism")

    registry.add_organism("Supply Organism")

    registry.add_organism("Capacity Organism")

    registry.add_organism("Finance Reconciliation Organism")

    registry.add_organism("Swarm Coordinator")

    registry.update_state("Demand Planning Organism", "RUNNING")

    registry.update_state("Inventory Organism", "RUNNING")

    registry.update_state("Supply Organism", "RUNNING")

    registry.update_state("Capacity Organism", "WAITING")

    registry.update_state("Finance Reconciliation Organism", "RUNNING")

    registry.update_state("Swarm Coordinator", "RUNNING")

    registry.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--root-dir", required=True)

    parser.add_argument("--init-demo", action="store_true")

    args = parser.parse_args()

    registry = RuntimeRegistry(args.root_dir)

    if args.init_demo:
        initialize_demo_registry(registry)

        print()

        print("Runtime Registry initialized")

        print(f"Registry: {registry.registry_file}")

        print(f"Status:   {registry.status_file}")
