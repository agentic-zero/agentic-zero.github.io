# security/audit_logger.py

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AuditEvent:
    event_id: str
    timestamp_utc: str
    event_type: str
    severity: str
    client_id: str
    actor: str
    action: str
    outcome: str
    reason: Optional[str]
    metadata: Dict[str, Any]


class AuditLogger:
    """
    Security audit logger for Agentic Zero.

    Writes immutable JSONL audit events.

    Intended for:
    - subscription checks
    - license validation
    - entitlement decisions
    - security denials
    - read-only transitions
    - locked/decommissioned states
    """

    VALID_SEVERITIES = {"INFO", "WARNING", "ERROR", "CRITICAL"}

    def __init__(self, audit_root: str | Path = "security/state/audit_logs") -> None:
        self.audit_root = Path(audit_root)
        self.audit_root.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        event_type: str,
        client_id: str,
        actor: str,
        action: str,
        outcome: str,
        severity: str = "INFO",
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        severity = severity.upper()

        if severity not in self.VALID_SEVERITIES:
            raise ValueError(
                f"Invalid severity '{severity}'. "
                f"Expected one of {sorted(self.VALID_SEVERITIES)}"
            )

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            severity=severity,
            client_id=client_id,
            actor=actor,
            action=action,
            outcome=outcome,
            reason=reason,
            metadata=metadata or {},
        )

        self._write_event(event)
        return event

    def _write_event(self, event: AuditEvent) -> None:
        client_file = self.audit_root / f"{event.client_id}.jsonl"

        with client_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def read_events(self, client_id: str, limit: int = 100) -> list[Dict[str, Any]]:
        client_file = self.audit_root / f"{client_id}.jsonl"

        if not client_file.exists():
            return []

        with client_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        selected = lines[-limit:]

        return [json.loads(line) for line in selected if line.strip()]


def main() -> None:
    logger = AuditLogger()

    event = logger.log(
        event_type="SECURITY_LAYER_INITIALIZED",
        client_id="dis_solar",
        actor="system",
        action="initialize_security_audit_logger",
        outcome="SUCCESS",
        severity="INFO",
        reason="Security audit logger smoke test",
        metadata={
            "component": "audit_logger",
            "version": "1.0.0",
        },
    )

    print("Audit event written:")
    print(json.dumps(asdict(event), indent=2))


if __name__ == "__main__":
    main()
