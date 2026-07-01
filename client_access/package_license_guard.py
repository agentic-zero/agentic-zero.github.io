# client_access/package_license_guard.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger
from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager


class PackageRuntimeMode(str, Enum):
    ACTIVE = "ACTIVE"
    GRACE_PERIOD = "GRACE_PERIOD"
    READ_ONLY = "READ_ONLY"
    LOCKED = "LOCKED"
    DECOMMISSIONED = "DECOMMISSIONED"


@dataclass
class PackageRuntimeDecision:
    client_id: str
    package_id: str
    execution_allowed: bool
    read_allowed: bool
    update_allowed: bool
    connector_allowed: bool
    swarm_allowed: bool
    mode: PackageRuntimeMode
    reason: str
    license_valid: bool
    metadata: dict[str, Any]


class PackageLicenseGuard:
    """
    Runtime license guard for delivered customer packages.

    This module is intended to be embedded/called by the delivered package,
    without exposing Agentic Zero internal engines.

    It checks:
    - license validity
    - entitlement status
    - execution rights
    - connector rights
    - swarm rights
    - update rights

    It does NOT expose:
    - The Machine
    - Agentic Shield
    - runtime_core
    - security source code
    - internal prompts
    - memory
    """

    def __init__(
        self,
        *,
        license_manager: Optional[LicenseManager] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
        audit_logger: Optional[AuditLogger] = None,
    ) -> None:
        self.license_manager = license_manager or LicenseManager()
        self.entitlement_guard = entitlement_guard or EntitlementGuard()
        self.audit_logger = audit_logger or AuditLogger()

    def check_package_runtime(
        self,
        *,
        client_id: str,
        package_id: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> PackageRuntimeDecision:
        metadata = metadata or {}

        license_validation = self.license_manager.validate(client_id)

        if not license_validation.valid:
            return self._decision(
                client_id=client_id,
                package_id=package_id,
                execution_allowed=False,
                read_allowed=False,
                update_allowed=False,
                connector_allowed=False,
                swarm_allowed=False,
                mode=PackageRuntimeMode.LOCKED,
                reason=license_validation.reason,
                license_valid=False,
                metadata={
                    **metadata,
                    "stage": "license_validation",
                    "license_status": license_validation.status,
                },
            )

        entitlement = self.entitlement_guard.check(client_id)

        if entitlement.status.value == "ACTIVE":
            return self._decision(
                client_id=client_id,
                package_id=package_id,
                execution_allowed=True,
                read_allowed=True,
                update_allowed=True,
                connector_allowed=True,
                swarm_allowed=True,
                mode=PackageRuntimeMode.ACTIVE,
                reason=entitlement.reason,
                license_valid=True,
                metadata=metadata,
            )

        if entitlement.status.value == "GRACE_PERIOD":
            return self._decision(
                client_id=client_id,
                package_id=package_id,
                execution_allowed=True,
                read_allowed=True,
                update_allowed=False,
                connector_allowed=True,
                swarm_allowed=True,
                mode=PackageRuntimeMode.GRACE_PERIOD,
                reason="Grace period active. Runtime allowed, updates disabled.",
                license_valid=True,
                metadata=metadata,
            )

        if entitlement.status.value == "READ_ONLY":
            return self._decision(
                client_id=client_id,
                package_id=package_id,
                execution_allowed=False,
                read_allowed=True,
                update_allowed=False,
                connector_allowed=False,
                swarm_allowed=False,
                mode=PackageRuntimeMode.READ_ONLY,
                reason="Read-only mode. Historical access allowed, runtime execution blocked.",
                license_valid=True,
                metadata=metadata,
            )

        if entitlement.status.value == "LOCKED":
            return self._decision(
                client_id=client_id,
                package_id=package_id,
                execution_allowed=False,
                read_allowed=False,
                update_allowed=False,
                connector_allowed=False,
                swarm_allowed=False,
                mode=PackageRuntimeMode.LOCKED,
                reason="Subscription locked. Package runtime disabled.",
                license_valid=True,
                metadata=metadata,
            )

        if entitlement.status.value == "DECOMMISSIONED":
            return self._decision(
                client_id=client_id,
                package_id=package_id,
                execution_allowed=False,
                read_allowed=False,
                update_allowed=False,
                connector_allowed=False,
                swarm_allowed=False,
                mode=PackageRuntimeMode.DECOMMISSIONED,
                reason="Client environment decommissioned.",
                license_valid=True,
                metadata=metadata,
            )

        return self._decision(
            client_id=client_id,
            package_id=package_id,
            execution_allowed=False,
            read_allowed=False,
            update_allowed=False,
            connector_allowed=False,
            swarm_allowed=False,
            mode=PackageRuntimeMode.LOCKED,
            reason=f"Unknown entitlement status: {entitlement.status.value}",
            license_valid=True,
            metadata=metadata,
        )

    def require_execution_allowed(
        self,
        *,
        client_id: str,
        package_id: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> PackageRuntimeDecision:
        decision = self.check_package_runtime(
            client_id=client_id,
            package_id=package_id,
            metadata=metadata,
        )

        if not decision.execution_allowed:
            raise PermissionError(
                f"Package runtime execution denied for client '{client_id}', "
                f"package '{package_id}'. Reason: {decision.reason}"
            )

        return decision

    def _decision(
        self,
        *,
        client_id: str,
        package_id: str,
        execution_allowed: bool,
        read_allowed: bool,
        update_allowed: bool,
        connector_allowed: bool,
        swarm_allowed: bool,
        mode: PackageRuntimeMode,
        reason: str,
        license_valid: bool,
        metadata: dict[str, Any],
    ) -> PackageRuntimeDecision:
        decision = PackageRuntimeDecision(
            client_id=client_id,
            package_id=package_id,
            execution_allowed=execution_allowed,
            read_allowed=read_allowed,
            update_allowed=update_allowed,
            connector_allowed=connector_allowed,
            swarm_allowed=swarm_allowed,
            mode=mode,
            reason=reason,
            license_valid=license_valid,
            metadata=metadata,
        )

        self.audit_logger.log(
            event_type="PACKAGE_RUNTIME_LICENSE_CHECK",
            client_id=client_id,
            actor="package_runtime",
            action="check_package_runtime",
            outcome="ALLOW" if execution_allowed else "DENY",
            severity="INFO" if execution_allowed else "WARNING",
            reason=reason,
            metadata={
                "package_id": package_id,
                "mode": mode.value,
                "license_valid": license_valid,
                "execution_allowed": execution_allowed,
                "read_allowed": read_allowed,
                "update_allowed": update_allowed,
                "connector_allowed": connector_allowed,
                "swarm_allowed": swarm_allowed,
                **metadata,
            },
        )

        return decision


def main() -> None:
    guard = PackageLicenseGuard()

    decision = guard.check_package_runtime(
        client_id="dis_solar",
        package_id="agentic_one_enterprise_package",
        metadata={"test": True},
    )

    output = Path("client_access/state/package_license_guard_test_result.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(decision), indent=2, default=str),
        encoding="utf-8",
    )

    print("")
    print("Package License Guard")
    print("---------------------")
    print(f"Mode              : {decision.mode.value}")
    print(f"Execution allowed : {decision.execution_allowed}")
    print(f"Read allowed      : {decision.read_allowed}")
    print(f"Update allowed    : {decision.update_allowed}")
    print(f"Connector allowed : {decision.connector_allowed}")
    print(f"Swarm allowed     : {decision.swarm_allowed}")
    print(f"Output            : {output}")
    print("")


if __name__ == "__main__":
    main()
