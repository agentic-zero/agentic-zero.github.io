# security/security_policy.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    READ_ONLY = "READ_ONLY"


@dataclass
class SecurityContext:
    client_id: str
    subscription_status: str
    license_valid: bool
    autonomy_level: int
    governance_required: bool
    action_type: str
    risk_level: str


@dataclass
class PolicyDecision:
    decision: Decision
    reason: str


class SecurityPolicy:
    """
    Central security decision engine.

    Every execution request should pass here first.
    """

    def evaluate(self, context: SecurityContext) -> PolicyDecision:

        # Subscription expired
        if context.subscription_status == "LOCKED":
            return PolicyDecision(decision=Decision.DENY, reason="Subscription locked")

        if context.subscription_status == "READ_ONLY":
            return PolicyDecision(
                decision=Decision.READ_ONLY, reason="Subscription in read-only mode"
            )

        # License invalid
        if not context.license_valid:
            return PolicyDecision(decision=Decision.DENY, reason="Invalid license")

        # Critical actions
        if context.risk_level == "CRITICAL" and context.governance_required:
            return PolicyDecision(
                decision=Decision.ESCALATE,
                reason="Critical action requires governance approval",
            )

        return PolicyDecision(decision=Decision.ALLOW, reason="Policy checks passed")


def main() -> None:

    policy = SecurityPolicy()

    context = SecurityContext(
        client_id="dis_solar",
        subscription_status="ACTIVE",
        license_valid=True,
        autonomy_level=72,
        governance_required=True,
        action_type="supplier_rerouting",
        risk_level="MEDIUM",
    )

    decision = policy.evaluate(context)

    print("")
    print("Security Policy Decision")
    print("------------------------")
    print(f"Decision : {decision.decision}")
    print(f"Reason   : {decision.reason}")
    print("")


if __name__ == "__main__":
    main()
