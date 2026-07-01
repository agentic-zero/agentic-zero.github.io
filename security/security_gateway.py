# security/security_gateway.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Optional

from security.audit_logger import AuditLogger
from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager
from security.security_policy import Decision, SecurityContext, SecurityPolicy
from security.subscription_gate import SubscriptionGate


@dataclass
class SecurityGatewayResult:
    client_id: str
    allowed: bool
    decision: str
    reason: str
    action: str
    component: str
    license_valid: bool
    subscription_allowed: bool
    policy_decision: str
    metadata: dict[str, Any]


class SecurityGateway:
    """
    Unified security gateway for Agentic Zero.

    This should be called before any runtime execution:

    - agent execution
    - swarm execution
    - connector action
    - autonomous decision
    - scheduled job
    - write operation
    - dashboard-triggered action

    It combines:

    - LicenseManager
    - EntitlementGuard
    - SubscriptionGate
    - SecurityPolicy
    - AuditLogger
    """

    def __init__(
        self,
        *,
        audit_logger: Optional[AuditLogger] = None,
        license_manager: Optional[LicenseManager] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
        subscription_gate: Optional[SubscriptionGate] = None,
        security_policy: Optional[SecurityPolicy] = None,
    ) -> None:
        self.audit_logger = audit_logger or AuditLogger()
        self.license_manager = license_manager or LicenseManager(
            audit_logger=self.audit_logger
        )
        self.entitlement_guard = entitlement_guard or EntitlementGuard()
        self.subscription_gate = subscription_gate or SubscriptionGate(
            entitlement_guard=self.entitlement_guard,
            audit_logger=self.audit_logger,
        )
        self.security_policy = security_policy or SecurityPolicy()

    def authorize(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        actor: str = "system",
        autonomy_level: int = 0,
        governance_required: bool = True,
        risk_level: str = "MEDIUM",
        metadata: Optional[dict[str, Any]] = None,
    ) -> SecurityGatewayResult:
        metadata = metadata or {}

        license_validation = self.license_manager.validate(client_id)

        if not license_validation.valid:
            return self._deny(
                client_id=client_id,
                action=action,
                component=component,
                actor=actor,
                reason=license_validation.reason,
                license_valid=False,
                subscription_allowed=False,
                policy_decision="DENY",
                metadata={
                    **metadata,
                    "stage": "license_validation",
                    "license_status": license_validation.status,
                },
            )

        subscription_result = self.subscription_gate.authorize(
            client_id=client_id,
            action=action,
            component=component,
            actor=actor,
            metadata={
                **metadata,
                "stage": "subscription_gate",
            },
        )

        if not subscription_result.allowed:
            return self._deny(
                client_id=client_id,
                action=action,
                component=component,
                actor=actor,
                reason=subscription_result.reason,
                license_valid=True,
                subscription_allowed=False,
                policy_decision="DENY",
                metadata={
                    **metadata,
                    "stage": "subscription_gate",
                    "subscription_mode": subscription_result.mode,
                    "entitlement_status": subscription_result.entitlement.get("status"),
                },
            )

        entitlement_status = subscription_result.entitlement.get("status", "UNKNOWN")

        context = SecurityContext(
            client_id=client_id,
            subscription_status=entitlement_status,
            license_valid=license_validation.valid,
            autonomy_level=autonomy_level,
            governance_required=governance_required,
            action_type=action,
            risk_level=risk_level,
        )

        policy_decision = self.security_policy.evaluate(context)

        if policy_decision.decision == Decision.DENY:
            return self._deny(
                client_id=client_id,
                action=action,
                component=component,
                actor=actor,
                reason=policy_decision.reason,
                license_valid=True,
                subscription_allowed=True,
                policy_decision=policy_decision.decision.value,
                metadata={
                    **metadata,
                    "stage": "security_policy",
                },
            )

        if policy_decision.decision == Decision.READ_ONLY:
            return self._deny(
                client_id=client_id,
                action=action,
                component=component,
                actor=actor,
                reason=policy_decision.reason,
                license_valid=True,
                subscription_allowed=True,
                policy_decision=policy_decision.decision.value,
                metadata={
                    **metadata,
                    "stage": "security_policy",
                },
            )

        if policy_decision.decision == Decision.ESCALATE:
            return self._escalate(
                client_id=client_id,
                action=action,
                component=component,
                actor=actor,
                reason=policy_decision.reason,
                metadata={
                    **metadata,
                    "stage": "security_policy",
                },
            )

        return self._allow(
            client_id=client_id,
            action=action,
            component=component,
            actor=actor,
            reason=policy_decision.reason,
            license_valid=True,
            subscription_allowed=True,
            policy_decision=policy_decision.decision.value,
            metadata={
                **metadata,
                "stage": "security_gateway",
            },
        )

    def require_authorized(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        actor: str = "system",
        autonomy_level: int = 0,
        governance_required: bool = True,
        risk_level: str = "MEDIUM",
        metadata: Optional[dict[str, Any]] = None,
    ) -> SecurityGatewayResult:
        result = self.authorize(
            client_id=client_id,
            action=action,
            component=component,
            actor=actor,
            autonomy_level=autonomy_level,
            governance_required=governance_required,
            risk_level=risk_level,
            metadata=metadata,
        )

        if not result.allowed:
            raise PermissionError(
                f"SecurityGateway denied action '{action}' "
                f"for client '{client_id}' on component '{component}'. "
                f"Reason: {result.reason}"
            )

        return result

    def _allow(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        actor: str,
        reason: str,
        license_valid: bool,
        subscription_allowed: bool,
        policy_decision: str,
        metadata: dict[str, Any],
    ) -> SecurityGatewayResult:
        result = SecurityGatewayResult(
            client_id=client_id,
            allowed=True,
            decision="ALLOW",
            reason=reason,
            action=action,
            component=component,
            license_valid=license_valid,
            subscription_allowed=subscription_allowed,
            policy_decision=policy_decision,
            metadata=metadata,
        )

        self.audit_logger.log(
            event_type="SECURITY_GATEWAY_ALLOWED",
            client_id=client_id,
            actor=actor,
            action=action,
            outcome="ALLOW",
            severity="INFO",
            reason=reason,
            metadata={
                "component": component,
                "policy_decision": policy_decision,
                **metadata,
            },
        )

        return result

    def _deny(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        actor: str,
        reason: str,
        license_valid: bool,
        subscription_allowed: bool,
        policy_decision: str,
        metadata: dict[str, Any],
    ) -> SecurityGatewayResult:
        result = SecurityGatewayResult(
            client_id=client_id,
            allowed=False,
            decision="DENY",
            reason=reason,
            action=action,
            component=component,
            license_valid=license_valid,
            subscription_allowed=subscription_allowed,
            policy_decision=policy_decision,
            metadata=metadata,
        )

        self.audit_logger.log(
            event_type="SECURITY_GATEWAY_DENIED",
            client_id=client_id,
            actor=actor,
            action=action,
            outcome="DENY",
            severity="WARNING",
            reason=reason,
            metadata={
                "component": component,
                "policy_decision": policy_decision,
                **metadata,
            },
        )

        return result

    def _escalate(
        self,
        *,
        client_id: str,
        action: str,
        component: str,
        actor: str,
        reason: str,
        metadata: dict[str, Any],
    ) -> SecurityGatewayResult:
        result = SecurityGatewayResult(
            client_id=client_id,
            allowed=False,
            decision="ESCALATE",
            reason=reason,
            action=action,
            component=component,
            license_valid=True,
            subscription_allowed=True,
            policy_decision="ESCALATE",
            metadata=metadata,
        )

        self.audit_logger.log(
            event_type="SECURITY_GATEWAY_ESCALATED",
            client_id=client_id,
            actor=actor,
            action=action,
            outcome="ESCALATE",
            severity="WARNING",
            reason=reason,
            metadata={
                "component": component,
                **metadata,
            },
        )

        return result


def main() -> None:
    audit_logger = AuditLogger()
    license_manager = LicenseManager(audit_logger=audit_logger)
    entitlement_guard = EntitlementGuard()

    # Demo license
    existing = license_manager.load_license("dis_solar")
    if existing is None:
        license_manager.create_license(
            client_id="dis_solar",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            expires_at="2099-12-31T23:59:59Z",
            metadata={"environment": "security_gateway_test"},
        )

    entitlement_guard.create_demo_entitlement("dis_solar")

    gateway = SecurityGateway(
        audit_logger=audit_logger,
        license_manager=license_manager,
        entitlement_guard=entitlement_guard,
    )

    result = gateway.authorize(
        client_id="dis_solar",
        action="execute",
        component="agentic_one_runtime",
        actor="system",
        autonomy_level=72,
        governance_required=True,
        risk_level="MEDIUM",
        metadata={
            "test": True,
            "scenario": "security_gateway_smoke_test",
        },
    )

    print("")
    print("Security Gateway")
    print("----------------")
    print(json.dumps(asdict(result), indent=2))
    print("")


if __name__ == "__main__":
    main()
