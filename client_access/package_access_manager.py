# client_access/package_access_manager.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from client_access.access_boundary import AccessBoundary, AccessDecision
from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager
from security.audit_logger import AuditLogger


class PackageAccessMode(str, Enum):
    FULL = "FULL"
    READ_ONLY = "READ_ONLY"
    LOCKED = "LOCKED"


@dataclass
class PackageAccessDecision:
    client_id: str
    resource: str
    allowed: bool
    mode: PackageAccessMode
    reason: str
    license_valid: bool
    entitlement_status: str
    boundary_decision: str
    metadata: dict[str, Any]


class PackageAccessManager:
    """
    Controls access to customer-facing packages.

    This module protects the commercial boundary:

    Customer may access:
    - delivered package
    - customer reports
    - allowed exports
    - customer documentation

    Customer may not access:
    - Agentic Zero internal engines
    - The Machine
    - Agentic Shield
    - Runtime Core
    - security/
    - saas/
    - prompts
    - internal logs

    Payment status controls execution/download/update rights.
    """

    def __init__(
        self,
        *,
        access_boundary: Optional[AccessBoundary] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
        license_manager: Optional[LicenseManager] = None,
        audit_logger: Optional[AuditLogger] = None,
    ) -> None:
        self.access_boundary = access_boundary or AccessBoundary()
        self.entitlement_guard = entitlement_guard or EntitlementGuard()
        self.license_manager = license_manager or LicenseManager()
        self.audit_logger = audit_logger or AuditLogger()

    def authorize_package_access(
        self,
        *,
        client_id: str,
        resource: str,
        action: str = "download",
        metadata: Optional[dict[str, Any]] = None,
    ) -> PackageAccessDecision:
        metadata = metadata or {}

        boundary = self.access_boundary.authorize_resource_access(
            client_id=client_id,
            resource=resource,
            metadata=metadata,
        )

        if boundary.decision == AccessDecision.DENY:
            return self._deny(
                client_id=client_id,
                resource=resource,
                reason=boundary.reason,
                license_valid=False,
                entitlement_status="N/A",
                boundary_decision=boundary.decision.value,
                metadata={
                    **metadata,
                    "stage": "access_boundary",
                    "resource_class": boundary.resource_class.value,
                    "action": action,
                },
            )

        license_validation = self.license_manager.validate(client_id)

        if not license_validation.valid:
            return self._deny(
                client_id=client_id,
                resource=resource,
                reason=license_validation.reason,
                license_valid=False,
                entitlement_status="N/A",
                boundary_decision=boundary.decision.value,
                metadata={
                    **metadata,
                    "stage": "license_validation",
                    "license_status": license_validation.status,
                    "action": action,
                },
            )

        entitlement = self.entitlement_guard.check(client_id)

        if entitlement.status.value in {"ACTIVE", "GRACE_PERIOD"}:
            return self._allow(
                client_id=client_id,
                resource=resource,
                mode=PackageAccessMode.FULL,
                reason=entitlement.reason,
                license_valid=True,
                entitlement_status=entitlement.status.value,
                boundary_decision=boundary.decision.value,
                metadata={
                    **metadata,
                    "action": action,
                },
            )

        if entitlement.status.value == "READ_ONLY":
            if action.lower() in {"view", "read", "export_existing"}:
                return self._allow(
                    client_id=client_id,
                    resource=resource,
                    mode=PackageAccessMode.READ_ONLY,
                    reason="Read-only access allowed for existing customer artifacts",
                    license_valid=True,
                    entitlement_status=entitlement.status.value,
                    boundary_decision=boundary.decision.value,
                    metadata={
                        **metadata,
                        "action": action,
                    },
                )

            return self._deny(
                client_id=client_id,
                resource=resource,
                reason="Read-only subscription state blocks new downloads or execution",
                license_valid=True,
                entitlement_status=entitlement.status.value,
                boundary_decision=boundary.decision.value,
                metadata={
                    **metadata,
                    "action": action,
                },
            )

        return self._deny(
            client_id=client_id,
            resource=resource,
            reason=f"Entitlement status {entitlement.status.value} blocks package access",
            license_valid=True,
            entitlement_status=entitlement.status.value,
            boundary_decision=boundary.decision.value,
            metadata={
                **metadata,
                "action": action,
            },
        )

    def _allow(
        self,
        *,
        client_id: str,
        resource: str,
        mode: PackageAccessMode,
        reason: str,
        license_valid: bool,
        entitlement_status: str,
        boundary_decision: str,
        metadata: dict[str, Any],
    ) -> PackageAccessDecision:
        decision = PackageAccessDecision(
            client_id=client_id,
            resource=resource,
            allowed=True,
            mode=mode,
            reason=reason,
            license_valid=license_valid,
            entitlement_status=entitlement_status,
            boundary_decision=boundary_decision,
            metadata=metadata,
        )

        self.audit_logger.log(
            event_type="PACKAGE_ACCESS_ALLOWED",
            client_id=client_id,
            actor="system",
            action="authorize_package_access",
            outcome="ALLOW",
            severity="INFO",
            reason=reason,
            metadata={
                "resource": resource,
                "mode": mode.value,
                "entitlement_status": entitlement_status,
                **metadata,
            },
        )

        return decision

    def _deny(
        self,
        *,
        client_id: str,
        resource: str,
        reason: str,
        license_valid: bool,
        entitlement_status: str,
        boundary_decision: str,
        metadata: dict[str, Any],
    ) -> PackageAccessDecision:
        decision = PackageAccessDecision(
            client_id=client_id,
            resource=resource,
            allowed=False,
            mode=PackageAccessMode.LOCKED,
            reason=reason,
            license_valid=license_valid,
            entitlement_status=entitlement_status,
            boundary_decision=boundary_decision,
            metadata=metadata,
        )

        self.audit_logger.log(
            event_type="PACKAGE_ACCESS_DENIED",
            client_id=client_id,
            actor="system",
            action="authorize_package_access",
            outcome="DENY",
            severity="WARNING",
            reason=reason,
            metadata={
                "resource": resource,
                "entitlement_status": entitlement_status,
                **metadata,
            },
        )

        return decision


def main() -> None:
    manager = PackageAccessManager()

    tests = [
        {
            "client_id": "dis_solar",
            "resource": "customer_packages/dis_solar/package.zip",
            "action": "download",
        },
        {
            "client_id": "dis_solar",
            "resource": "reports/dis_solar/roi_report.pdf",
            "action": "view",
        },
        {
            "client_id": "dis_solar",
            "resource": "the_machine/evolution_engine.py",
            "action": "download",
        },
        {
            "client_id": "dis_solar",
            "resource": "security/license_manager.py",
            "action": "download",
        },
    ]

    results = [asdict(manager.authorize_package_access(**item)) for item in tests]

    output = Path("client_access/state/package_access_test_result.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")

    print("")
    print("Package Access Manager")
    print("----------------------")

    for result in results:
        print(
            "ALLOW" if result["allowed"] else "DENY",
            "|",
            result["mode"],
            "|",
            result["resource"],
        )

    print("")
    print(f"Output: {output}")
    print("")


if __name__ == "__main__":
    main()
