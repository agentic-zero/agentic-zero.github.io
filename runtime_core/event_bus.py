"""
AGENTIC ZERO - RUNTIME CORE
Event Bus v1.0

Role:
  Central JSONL event bus for agents, swarms, Shield, Pulse and The Machine.

Streams:
  swarm_events.jsonl
  audit_events.jsonl
  learning_events.jsonl
  shield_events.jsonl
  pulse_events.jsonl
"""

from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class BusEvent:
    event_id: str
    timestamp: str
    stream: str
    source: str
    event_type: str
    payload: dict[str, Any]
    correlation_id: str = ""
    causation_id: str = ""
    confidence: float = 1.0
    risk_score: float = 0.0
    requires_audit: bool = True
    requires_learning: bool = False
    requires_shield: bool = False
    tags: list[str] = field(default_factory=list)


class EventBus:
    def __init__(self, root_dir: str | Path = "."):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

        self.streams = {
            "swarm": self.root_dir / "swarm_events.jsonl",
            "audit": self.root_dir / "audit_events.jsonl",
            "learning": self.root_dir / "learning_events.jsonl",
            "shield": self.root_dir / "shield_events.jsonl",
            "pulse": self.root_dir / "pulse_events.jsonl",
        }

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    def emit(
        self,
        stream: str,
        source: str,
        event_type: str,
        payload: dict[str, Any],
        correlation_id: str = "",
        causation_id: str = "",
        confidence: float = 1.0,
        risk_score: float = 0.0,
        requires_audit: bool = True,
        requires_learning: bool = False,
        requires_shield: bool = False,
        tags: Optional[list[str]] = None,
    ) -> BusEvent:
        if stream not in self.streams:
            raise ValueError(
                f"Unknown stream: {stream}. Valid streams: {list(self.streams)}"
            )

        event = BusEvent(
            event_id=self.new_id(),
            timestamp=self.now(),
            stream=stream,
            source=source,
            event_type=event_type,
            payload=payload,
            correlation_id=correlation_id or self.new_id(),
            causation_id=causation_id,
            confidence=confidence,
            risk_score=risk_score,
            requires_audit=requires_audit,
            requires_learning=requires_learning,
            requires_shield=requires_shield,
            tags=tags or [],
        )

        self._append(self.streams[stream], asdict(event))

        if requires_audit and stream != "audit":
            self._append(self.streams["audit"], asdict(event))

        if requires_learning and stream != "learning":
            learning_event = asdict(event)
            learning_event["stream"] = "learning"
            self._append(self.streams["learning"], learning_event)

        if requires_shield and stream != "shield":
            shield_event = asdict(event)
            shield_event["stream"] = "shield"
            self._append(self.streams["shield"], shield_event)

        self._emit_pulse_projection(event)

        return event

    def _append(self, path: Path, payload: dict[str, Any]):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _emit_pulse_projection(self, event: BusEvent):
        pulse_payload = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "source": event.source,
            "event_type": event.event_type,
            "confidence": event.confidence,
            "risk_score": event.risk_score,
            "requires_shield": event.requires_shield,
            "requires_learning": event.requires_learning,
            "tags": event.tags,
        }
        self._append(self.streams["pulse"], pulse_payload)

    def read_stream(self, stream: str, limit: int = 100) -> list[dict[str, Any]]:
        if stream not in self.streams:
            raise ValueError(f"Unknown stream: {stream}")

        path = self.streams[stream]
        if not path.exists():
            return []

        lines = path.read_text(encoding="utf-8").splitlines()
        selected = lines[-limit:]
        events = []
        for line in selected:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def status(self) -> dict[str, Any]:
        return {
            "root_dir": str(self.root_dir),
            "streams": {
                name: {
                    "path": str(path),
                    "exists": path.exists(),
                    "size_bytes": path.stat().st_size if path.exists() else 0,
                }
                for name, path in self.streams.items()
            },
        }


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Event Bus")
    parser.add_argument(
        "--root-dir", default="runtime_events", help="Event bus root directory"
    )
    parser.add_argument("--emit-test", action="store_true", help="Emit a test event")
    parser.add_argument("--status", action="store_true", help="Show bus status")
    args = parser.parse_args()

    bus = EventBus(args.root_dir)

    if args.emit_test:
        event = bus.emit(
            stream="swarm",
            source="EventBusSmokeTest",
            event_type="test_event",
            payload={"message": "Event bus is alive"},
            confidence=0.99,
            risk_score=0.01,
            requires_learning=True,
            requires_shield=False,
            tags=["smoke_test"],
        )
        print(json.dumps(asdict(event), indent=2, ensure_ascii=False))

    if args.status:
        print(json.dumps(bus.status(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_cli()
