# security/runtime_entrypoint.py

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from security.audit_logger import AuditLogger
from security.security_gateway import SecurityGateway

# runtime_core lives outside security/ - imported lazily inside execute() so
# this module can still be imported/tested in isolation if runtime_core is
# not on the path for a given test.


@dataclass
class RuntimeExecutionResult:
    client_id: str
    action: str
    component: str
    decision: str
    authorized: bool
    executed: bool
    reason: str
    result: Any
    error: Optional[str]
    event_id: Optional[str]


class RuntimeEntrypoint:
    """
    The single execution gate for Agentic Zero.

    IMPORTANT - what this module is, and is not:

    This is the kernel. It must stay thin forever. It contains NO business
    logic, no Shield logic, no Machine logic - it only orchestrates two
    things, in order:

      1. SecurityGateway.authorize() - SYNCHRONOUS. License, entitlement,
         subscription and risk-level policy are all checked in real time,
         before anything runs. This is the only gate that blocks execution.

      2. Fire-and-forget event emission to runtime_core's EventBus. This is
         NOT a second authorization gate - it is how the action becomes
         visible to the BATCH learning/governance loop (observer.py ->
         pattern_detector.py -> prescriptor.py -> agentic_shield/*) on its
         own cadence. That loop already exists, is already validated
         end-to-end, and runs asynchronously relative to this call.

    Why Agentic Shield is NOT called inline here (deliberate, not an
    oversight): policy_engine.py decides on PRESCRIPTIONS that
    prescriptor.py wrote from PAST episodes - it has no synchronous
    "authorize this one action right now" API today. Wiring it in here
    would mean either faking a call that doesn't really exist, or building
    a brand new synchronous Shield API - which is itself "creating a new
    component" instead of "connecting what exists", the opposite of the
    stated goal for this layer. If a synchronous per-action Shield gate is
    ever wanted, that is a deliberate, separate, explicit addition to
    policy_engine.py - not something this kernel should quietly assume.

    Usage:
        entrypoint = RuntimeEntrypoint()

        result = entrypoint.execute(
            client_id="inmaculada_sierra",
            action="execute",
            component="order_to_cash_agent",
            event_dir="clients/inmaculada/otc/essential_package/13_swarm_runtime/events",
            risk_level="MEDIUM",
            run=lambda: do_the_real_agent_work(),
        )

        if not result.authorized:
            ... handle denial/escalation using result.decision/result.reason ...
    """

    def __init__(
        self,
        *,
        audit_logger: Optional[AuditLogger] = None,
        security_gateway: Optional[SecurityGateway] = None,
    ) -> None:
        self.audit_logger = audit_logger or AuditLogger()
        self.security_gateway = security_gateway or SecurityGateway(
            audit_logger=self.audit_logger
        )

    def execute(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        event_dir: str | Path,
        run: Callable[[], Any],
        actor: str = "system",
        autonomy_level: int = 0,
        governance_required: bool = True,
        risk_level: str = "MEDIUM",
        metadata: Optional[dict[str, Any]] = None,
    ) -> RuntimeExecutionResult:
        metadata = metadata or {}

        gateway_result = self.security_gateway.authorize(
            client_id=client_id,
            action=action,
            component=component,
            actor=actor,
            autonomy_level=autonomy_level,
            governance_required=governance_required,
            risk_level=risk_level,
            metadata=metadata,
        )

        if not gateway_result.allowed:
            event_id = self._emit_event(
                event_dir=event_dir,
                client_id=client_id,
                action=action,
                component=component,
                actor=actor,
                event_type="execution_blocked",
                outcome="negative",
                risk_level=risk_level,
                extra_payload={
                    "decision": gateway_result.decision,
                    "reason": gateway_result.reason,
                },
            )

            return RuntimeExecutionResult(
                client_id=client_id,
                action=action,
                component=component,
                decision=gateway_result.decision,
                authorized=False,
                executed=False,
                reason=gateway_result.reason,
                result=None,
                error=None,
                event_id=event_id,
            )

        # Authorized - run the real business logic. This is the ONLY line
        # in this entire module that touches actual execution; everything
        # else is gate-checking and event emission.
        try:
            outcome = run()
        except Exception as exc:  # noqa: BLE001 - intentionally broad: this
            # is the kernel boundary, it must never let a business-logic
            # exception propagate raw. It is captured and returned in
            # result.error instead of re-raised, matching how every other
            # module in this codebase signals failure (a returned result
            # object, not an exception) - callers check result.error rather
            # than wrapping every execute() call in their own try/except.
            event_id = self._emit_event(
                event_dir=event_dir,
                client_id=client_id,
                action=action,
                component=component,
                actor=actor,
                event_type="execution_failed",
                outcome="negative",
                risk_level=risk_level,
                extra_payload={
                    "decision": gateway_result.decision,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )

            self.audit_logger.log(
                event_type="RUNTIME_EXECUTION_FAILED",
                client_id=client_id,
                actor=actor,
                action=action,
                outcome="ERROR",
                severity="ERROR",
                reason=str(exc),
                metadata={"component": component, "event_id": event_id},
            )

            return RuntimeExecutionResult(
                client_id=client_id,
                action=action,
                component=component,
                decision=gateway_result.decision,
                authorized=True,
                executed=True,
                reason=f"Authorized but execution raised: {exc}",
                result=None,
                error=str(exc),
                event_id=event_id,
            )

        event_id = self._emit_event(
            event_dir=event_dir,
            client_id=client_id,
            action=action,
            component=component,
            actor=actor,
            event_type="execution_completed",
            outcome="positive",
            risk_level=risk_level,
            extra_payload={"decision": gateway_result.decision},
        )

        return RuntimeExecutionResult(
            client_id=client_id,
            action=action,
            component=component,
            decision=gateway_result.decision,
            authorized=True,
            executed=True,
            reason=gateway_result.reason,
            result=outcome,
            error=None,
            event_id=event_id,
        )

    def _emit_event(
        self,
        *,
        event_dir: str | Path,
        client_id: str,
        action: str,
        component: str,
        actor: str,
        event_type: str,
        outcome: str,
        risk_level: str,
        extra_payload: dict[str, Any],
    ) -> Optional[str]:
        """Fire-and-forget emission to the existing EventBus. If this fails
        for any reason (e.g. runtime_core not importable from this context,
        or a disk error), the caller's execution result is NOT affected -
        the SecurityGateway decision already happened and already stands.
        Losing a learning-loop event is a degraded-observability problem,
        never a reason to fail an already-authorized/already-executed
        action.
        """
        try:
            from runtime_core.event_bus import EventBus

            bus = EventBus(root_dir=event_dir)
            event = bus.emit(
                stream="swarm",
                source=f"runtime_entrypoint:{component}",
                event_type=event_type,
                payload={
                    "client_id": client_id,
                    "action": action,
                    "component": component,
                    "actor": actor,
                    "organism": component,
                    **extra_payload,
                },
                requires_learning=True,
                requires_shield=risk_level in ("HIGH", "CRITICAL"),
                risk_score=self._risk_score(risk_level),
            )
            return event.event_id
        except Exception:
            # Deliberately swallowed - see docstring. Observability gap,
            # not an execution-blocking failure.
            return None

    @staticmethod
    def _risk_score(risk_level: str) -> float:
        return {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 0.95}.get(
            risk_level.upper(), 0.5
        )


def main() -> None:
    """Smoke test: ALLOW path executes the real callable, DENY path does not."""
    import tempfile
    import uuid

    from security.contract_activation import ContractActivation

    # A unique client_id per run, not a fixed one - otherwise a second run
    # of this smoke test finds the client already ACTIVE from a PRIOR run
    # (entitlement state persists on disk) and the "still provisioning"
    # DENY case silently turns into a false ALLOW, hiding a real kernel
    # regression behind stale fixture state.
    client_id = f"runtime_entrypoint_smoke_test_{uuid.uuid4().hex[:8]}"
    event_dir = Path(tempfile.mkdtemp()) / "events"

    activation = ContractActivation()
    if activation.license_manager.load_license(client_id) is None:
        activation.provision_from_contract(
            client_id=client_id,
            product="AGENTIC_ZERO_ESSENTIAL",
            plan="ESSENTIAL",
            expires_at=None,
            activated_by="smoke_test",
            contract_reference="runtime_entrypoint_smoke_test",
        )

    entrypoint = RuntimeEntrypoint()

    calls: list[str] = []

    def real_work() -> str:
        calls.append("executed")
        return "business logic ran"

    # 1. Still PROVISIONING (read-only) -> must DENY, must NOT call real_work
    denied = entrypoint.execute(
        client_id=client_id,
        action="execute",
        component="smoke_test_agent",
        event_dir=event_dir,
        run=real_work,
        risk_level="MEDIUM",
    )

    # 2. Go-live -> must ALLOW, must call real_work
    activation.go_live(
        client_id=client_id,
        activated_by="smoke_test",
        contract_reference="runtime_entrypoint_smoke_test_go_live",
    )

    allowed = entrypoint.execute(
        client_id=client_id,
        action="execute",
        component="smoke_test_agent",
        event_dir=event_dir,
        run=real_work,
        risk_level="MEDIUM",
    )

    print("\nRuntime Entrypoint Smoke Test")
    print("------------------------------")
    print(f"Denied  (provisioning) : authorized={denied.authorized} executed={denied.executed} decision={denied.decision}")
    print(f"Allowed (active)       : authorized={allowed.authorized} executed={allowed.executed} decision={allowed.decision} result={allowed.result!r}")
    print(f"real_work() call count : {len(calls)} (must be exactly 1)")

    passed = (
        denied.authorized is False
        and denied.executed is False
        and allowed.authorized is True
        and allowed.executed is True
        and allowed.result == "business logic ran"
        and len(calls) == 1
    )

    print(f"\nPASS: {passed}")

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
