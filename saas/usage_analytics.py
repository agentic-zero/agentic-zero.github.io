# saas/usage_analytics.py

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class UsageEvent:
    usage_id: str
    client_id: str
    product: str
    component: str
    action: str
    quantity: float
    unit: str
    timestamp_utc: str
    metadata: dict[str, Any]


@dataclass
class UsageSummary:
    client_id: str
    total_events: int
    total_runtime_actions: int
    total_connector_actions: int
    total_audit_requests: int
    total_demo_sessions: int
    total_units: float
    generated_at: str


class UsageAnalytics:
    """
    SaaS usage analytics for Agentic Zero.

    This module does NOT touch:
    - Agentic Shield
    - The Machine
    - Runtime execution

    Responsibilities:
    - record usage events
    - summarize usage by client
    - support future billing limits
    - support customer portal usage views
    """

    def __init__(self, usage_root: str | Path = "saas/state/usage") -> None:
        self.usage_root = Path(usage_root)
        self.usage_root.mkdir(parents=True, exist_ok=True)

    def record_usage(
        self,
        *,
        client_id: str,
        product: str,
        component: str,
        action: str,
        quantity: float = 1.0,
        unit: str = "event",
        metadata: Optional[dict[str, Any]] = None,
    ) -> UsageEvent:
        event = UsageEvent(
            usage_id=f"usage-{uuid.uuid4()}",
            client_id=client_id,
            product=product,
            component=component,
            action=action,
            quantity=quantity,
            unit=unit,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )

        self._append(event)
        return event

    def summarize_client(self, client_id: str) -> UsageSummary:
        events = self.read_usage(client_id)

        total_runtime_actions = sum(
            1
            for e in events
            if e.component.lower()
            in {
                "runtime",
                "agentic_one_runtime",
                "swarm_runtime",
                "event_router",
                "event_bus",
            }
        )

        total_connector_actions = sum(
            1 for e in events if "connector" in e.component.lower()
        )

        total_audit_requests = sum(
            1
            for e in events
            if e.action.lower()
            in {
                "audit_zero_submitted",
                "advanced_audit_submitted",
                "audit_requested",
            }
        )

        total_demo_sessions = sum(
            1
            for e in events
            if e.action.lower()
            in {
                "demo_started",
                "demo_completed",
            }
        )

        total_units = sum(e.quantity for e in events)

        return UsageSummary(
            client_id=client_id,
            total_events=len(events),
            total_runtime_actions=total_runtime_actions,
            total_connector_actions=total_connector_actions,
            total_audit_requests=total_audit_requests,
            total_demo_sessions=total_demo_sessions,
            total_units=total_units,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def read_usage(
        self, client_id: str, limit: Optional[int] = None
    ) -> list[UsageEvent]:
        path = self._path(client_id)

        if not path.exists():
            return []

        lines = path.read_text(encoding="utf-8").splitlines()

        if limit is not None:
            lines = lines[-limit:]

        events: list[UsageEvent] = []

        for line in lines:
            if not line.strip():
                continue

            data = json.loads(line)

            events.append(
                UsageEvent(
                    usage_id=data["usage_id"],
                    client_id=data["client_id"],
                    product=data["product"],
                    component=data["component"],
                    action=data["action"],
                    quantity=float(data["quantity"]),
                    unit=data["unit"],
                    timestamp_utc=data["timestamp_utc"],
                    metadata=data.get("metadata", {}),
                )
            )

        return events

    def export_summary_json(self, client_id: str) -> str:
        return json.dumps(
            asdict(self.summarize_client(client_id)),
            indent=2,
        )

    def _append(self, event: UsageEvent) -> None:
        with self._path(event.client_id).open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def _path(self, client_id: str) -> Path:
        return self.usage_root / f"{client_id}.jsonl"


def main() -> None:
    analytics = UsageAnalytics()

    analytics.record_usage(
        client_id="dis_solar",
        product="AGENTIC_ONE",
        component="audit_zero",
        action="audit_zero_submitted",
        metadata={"source": "usage_analytics_test"},
    )

    analytics.record_usage(
        client_id="dis_solar",
        product="AGENTIC_ONE",
        component="agentic_one_runtime",
        action="runtime_action_authorized",
        quantity=3,
        unit="actions",
    )

    analytics.record_usage(
        client_id="dis_solar",
        product="AGENTIC_ONE",
        component="sap_connector",
        action="connector_call",
        quantity=2,
        unit="calls",
    )

    print("")
    print("Usage Analytics")
    print("---------------")
    print(analytics.export_summary_json("dis_solar"))
    print("")


if __name__ == "__main__":
    main()
