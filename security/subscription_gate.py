# security/subscription_gate.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger
from security.entitlement_guard import EntitlementGuard, EntitlementDecision


@dataclass
class GateResult:
    client_id: str
    allowed: bool
    mode: str
    reason: str
    action: str
    component: str
    entitlement: dict[str, Any]


class SubscriptionGate:
    """
    Runtime subscription gate for Agentic Zero.

    This must be called before executing:
    - autonomous agents
    - Agentic Swarm
    - Agentic One
    - connectors
    - scheduled jobs
    - write operations
    - runtime actions

    It prevents customers from continuing to use the system
    after subscription expiration, cancellation or decommissioning.
    """

    WRITE_ACTIONS = {
        "execute",
        "create",
        "update",
        "delete",
        "send",
        "post",
        "approve",
        "trigger",
        "dispatch",
        "reroute",
        "replan",
        "commit",
    }

    READ_ACTIONS = {
        "read",
        "view",
        "list",
        "export",
        "inspect",
        "report",
    }

    def __init__(
        self,
        entitlement_guard: Optional[EntitlementGuard] = None,
        audit_logger: Optional[AuditLogger] = None,
    ) -> None:
        self.entitlement_guard = entitlement_guard or EntitlementGuard()
        self.audit_logger = audit_logger or AuditLogger()

    def authorize(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        actor: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ) -> GateResult:
        entitlement = self.entitlement_guard.check(client_id)
        action_normalized = action.lower().strip()

        if self._is_read_action(action_normalized):
            allowed = entitlement.read_allowed
            mode = "READ"
            reason = entitlement.reason
        elif self._is_write_action(action_normalized):
            allowed = entitlement.execution_allowed and entitlement.write_allowed
            mode = "WRITE"
            reason = entitlement.reason
        else:
            allowed = entitlement.execution_allowed
            mode = "EXECUTION"
            reason = entitlement.reason

        result = GateResult(
            client_id=client_id,
            allowed=allowed,
            mode=mode,
            reason=reason,
            action=action,
            component=component,
            entitlement=asdict(entitlement),
        )

        self._log_result(
            result=result,
            actor=actor,
            metadata=metadata or {},
        )

        return result

    def require_authorized(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        actor: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ) -> GateResult:
        result = self.authorize(
            client_id=client_id,
            action=action,
            component=component,
            actor=actor,
            metadata=metadata,
        )

        if not result.allowed:
            raise PermissionError(
                f"SubscriptionGate denied action '{action}' "
                f"for client '{client_id}' on component '{component}'. "
                f"Reason: {result.reason}"
            )

        return result

    def _is_write_action(self, action: str) -> bool:
        return action in self.WRITE_ACTIONS

    def _is_read_action(self, action: str) -> bool:
        return action in self.READ_ACTIONS

    def _log_result(
        self,
        *,
        result: GateResult,
        actor: str,
        metadata: dict[str, Any],
    ) -> None:
        event_type = (
            "SUBSCRIPTION_GATE_ALLOWED"
            if result.allowed
            else "SUBSCRIPTION_GATE_DENIED"
        )

        severity = "INFO" if result.allowed else "WARNING"

        self.audit_logger.log(
            event_type=event_type,
            client_id=result.client_id,
            actor=actor,
            action=result.action,
            outcome="ALLOW" if result.allowed else "DENY",
            severity=severity,
            reason=result.reason,
            metadata={
                "component": result.component,
                "mode": result.mode,
                "entitlement_status": result.entitlement.get("status"),
                **metadata,
            },
        )


def main() -> None:
    guard = EntitlementGuard()
    guard.create_demo_entitlement("dis_solar")

    gate = SubscriptionGate(entitlement_guard=guard)

    result = gate.authorize(
        client_id="dis_solar",
        action="execute",
        component="agentic_one_runtime",
        actor="system",
        metadata={
            "test": True,
            "scenario": "active_subscription",
        },
    )

    print("")
    print("Subscription Gate")
    print("-----------------")
    print(json.dumps(asdict(result), indent=2))
    print("")


if __name__ == "__main__":
    main()
