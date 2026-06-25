# security/secure_client_offboarding.py

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger
from security.contract_activation import ContractActivation
from security.entitlement_guard import EntitlementGuard, EntitlementStatus
from security.license_manager import LicenseManager
from security.security_gateway import SecurityGateway


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PostCondition:
    check: str
    expected: Any
    actual: Any
    passed: bool


@dataclass
class OffboardingReport:
    client_id: str
    offboarded_at: str
    target_status: str
    activated_by: str
    contract_reference: str
    license_revoked: bool
    post_conditions: list[dict[str, Any]]
    all_checks_passed: bool
    audit_history_preserved: bool


class SecureClientOffboarding:
    """
    The blueprint's Priority 5: when a customer stops paying or churns,
    actually verify that every privilege got revoked - not just trust
    that calling deactivate() worked.

    This module does NOT duplicate contract_activation.py's lifecycle
    logic. ContractActivation.deactivate() already does the real work
    (flips entitlement status, optionally revokes the license, logs a
    CRITICAL audit event with mandatory attribution). What this module
    adds is the verification step the blueprint specifically calls out:

      - disable runtime    -> verify execution_allowed is now False
      - disable connectors -> verify connectors_enabled is now False
      - disable swarm      -> verify swarm_enabled is now False
      - revoke license     -> verify LicenseManager.validate() now
                               reports invalid (if revocation was requested)
      - preserve audit history -> verify the client's audit log file
                                   still exists and did not shrink
                                   relative to its size before offboarding
                                   started (the same append-only guarantee
                                   tamper_detection.py polices generally,
                                   checked explicitly here for this one
                                   high-stakes operation)

    If ANY post-condition fails, this is reported clearly rather than
    silently assumed - an offboarding that "ran" but left a connector
    enabled is worse than one that visibly failed.
    """

    def __init__(
        self,
        *,
        audit_logger: Optional[AuditLogger] = None,
        license_manager: Optional[LicenseManager] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
        security_gateway: Optional[SecurityGateway] = None,
        activation: Optional[ContractActivation] = None,
    ) -> None:
        self.audit_logger = audit_logger or AuditLogger()
        self.license_manager = license_manager or LicenseManager(audit_logger=self.audit_logger)
        self.entitlement_guard = entitlement_guard or EntitlementGuard()
        self.security_gateway = security_gateway or SecurityGateway(
            audit_logger=self.audit_logger,
            license_manager=self.license_manager,
            entitlement_guard=self.entitlement_guard,
        )
        self.activation = activation or ContractActivation(
            audit_logger=self.audit_logger,
            license_manager=self.license_manager,
            entitlement_guard=self.entitlement_guard,
        )

    def _audit_log_path(self, client_id: str) -> Path:
        return self.audit_logger.audit_root / f"{client_id}.jsonl"

    def offboard(
        self,
        *,
        client_id: str,
        activated_by: str,
        contract_reference: str,
        target_status: EntitlementStatus = EntitlementStatus.DECOMMISSIONED,
        revoke_license: bool = True,
    ) -> OffboardingReport:
        audit_path = self._audit_log_path(client_id)
        audit_size_before = audit_path.stat().st_size if audit_path.exists() else 0

        self.activation.deactivate(
            client_id=client_id,
            activated_by=activated_by,
            contract_reference=contract_reference,
            target_status=target_status,
            revoke_license=revoke_license,
        )

        post_conditions: list[PostCondition] = []

        entitlement_decision = self.entitlement_guard.check(client_id)
        post_conditions.append(
            PostCondition(
                check="runtime_execution_blocked",
                expected=False,
                actual=entitlement_decision.execution_allowed,
                passed=entitlement_decision.execution_allowed is False,
            )
        )
        post_conditions.append(
            PostCondition(
                check="writes_blocked",
                expected=False,
                actual=entitlement_decision.write_allowed,
                passed=entitlement_decision.write_allowed is False,
            )
        )

        entitlement_raw = self.entitlement_guard._load_entitlement(client_id)
        post_conditions.append(
            PostCondition(
                check="connectors_disabled",
                expected=False,
                actual=entitlement_raw.get("connectors_enabled"),
                passed=entitlement_raw.get("connectors_enabled") is False,
            )
        )
        post_conditions.append(
            PostCondition(
                check="swarm_disabled",
                expected=False,
                actual=entitlement_raw.get("swarm_enabled"),
                passed=entitlement_raw.get("swarm_enabled") is False,
            )
        )

        gateway_result = self.security_gateway.authorize(
            client_id=client_id,
            action="execute",
            component="offboarding_verification_probe",
            actor="secure_client_offboarding",
        )
        post_conditions.append(
            PostCondition(
                check="security_gateway_denies_execution",
                expected=False,
                actual=gateway_result.allowed,
                passed=gateway_result.allowed is False,
            )
        )

        if revoke_license:
            license_validation = self.license_manager.validate(client_id)
            post_conditions.append(
                PostCondition(
                    check="license_invalid_after_revocation",
                    expected=False,
                    actual=license_validation.valid,
                    passed=license_validation.valid is False,
                )
            )

        audit_size_after = audit_path.stat().st_size if audit_path.exists() else 0
        audit_history_preserved = audit_path.exists() and audit_size_after >= audit_size_before
        post_conditions.append(
            PostCondition(
                check="audit_history_preserved",
                expected=True,
                actual=audit_history_preserved,
                passed=audit_history_preserved,
            )
        )

        all_passed = all(p.passed for p in post_conditions)

        self.audit_logger.log(
            event_type="OFFBOARDING_VERIFIED" if all_passed else "OFFBOARDING_VERIFICATION_FAILED",
            client_id=client_id,
            actor=activated_by,
            action="offboard",
            outcome="SUCCESS" if all_passed else "INCOMPLETE",
            severity="CRITICAL" if all_passed else "ERROR",
            reason=(
                "All offboarding post-conditions verified."
                if all_passed
                else f"{sum(1 for p in post_conditions if not p.passed)} post-condition(s) failed - "
                f"client may still retain access. Manual review required."
            ),
            metadata={"post_conditions": [asdict(p) for p in post_conditions]},
        )

        return OffboardingReport(
            client_id=client_id,
            offboarded_at=now(),
            target_status=target_status.value,
            activated_by=activated_by,
            contract_reference=contract_reference,
            license_revoked=revoke_license,
            post_conditions=[asdict(p) for p in post_conditions],
            all_checks_passed=all_passed,
            audit_history_preserved=audit_history_preserved,
        )


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Secure Client Offboarding")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--activated-by", required=True)
    parser.add_argument("--contract-reference", required=True)
    parser.add_argument(
        "--target-status",
        choices=["LOCKED", "DECOMMISSIONED"],
        default="DECOMMISSIONED",
    )
    parser.add_argument("--no-revoke-license", action="store_true")
    args = parser.parse_args()

    offboarding = SecureClientOffboarding()

    try:
        report = offboarding.offboard(
            client_id=args.client_id,
            activated_by=args.activated_by,
            contract_reference=args.contract_reference,
            target_status=EntitlementStatus(args.target_status),
            revoke_license=not args.no_revoke_license,
        )
    except ValueError as e:
        print(f"\nREJECTED: {e}\n")
        raise SystemExit(1)

    print("\nSecure Client Offboarding")
    print("-------------------------")
    print(f"Client:        {report.client_id}")
    print(f"Target status: {report.target_status}")
    print(f"All checks passed: {report.all_checks_passed}")
    print("\nPost-conditions:")
    for pc in report.post_conditions:
        marker = "OK" if pc["passed"] else "!!"
        print(f"  [{marker}] {pc['check']}: expected={pc['expected']} actual={pc['actual']}")

    if not report.all_checks_passed:
        print("\nWARNING: offboarding completed with unverified post-conditions. Manual review required.")
        raise SystemExit(1)

    print("\nOffboarding verified clean.")


if __name__ == "__main__":
    run_cli()
