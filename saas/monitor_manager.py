# saas/monitoring_manager.py

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from saas.billing_manager import BillingManager
from saas.tenant_manager import TenantManager
from saas.usage_analytics import UsageAnalytics
from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass
class MonitoringCheck:
    check_id: str
    client_id: str
    check_name: str
    status: HealthStatus
    message: str
    timestamp_utc: str
    metadata: dict[str, Any]


@dataclass
class MonitoringSnapshot:
    client_id: str
    overall_status: HealthStatus
    checks: list[MonitoringCheck]
    generated_at: str


class MonitoringManager:
    """
    SaaS monitoring manager for Agentic Zero.

    This module does NOT touch:
    - Agentic Shield
    - The Machine
    - Runtime execution

    Responsibilities:
    - monitor tenant existence
    - monitor billing state
    - monitor entitlement state
    - monitor license state
    - monitor usage availability
    - produce SaaS-level health snapshots
    """

    def __init__(
        self,
        *,
        tenant_manager: Optional[TenantManager] = None,
        billing_manager: Optional[BillingManager] = None,
        usage_analytics: Optional[UsageAnalytics] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
        license_manager: Optional[LicenseManager] = None,
        monitoring_root: str | Path = "saas/state/monitoring",
    ) -> None:
        self.tenant_manager = tenant_manager or TenantManager()
        self.billing_manager = billing_manager or BillingManager()
        self.usage_analytics = usage_analytics or UsageAnalytics()
        self.entitlement_guard = entitlement_guard or EntitlementGuard()
        self.license_manager = license_manager or LicenseManager()
        self.monitoring_root = Path(monitoring_root)
        self.monitoring_root.mkdir(parents=True, exist_ok=True)

    def run_checks(self, client_id: str) -> MonitoringSnapshot:
        checks = [
            self._check_tenant(client_id),
            self._check_billing(client_id),
            self._check_entitlement(client_id),
            self._check_license(client_id),
            self._check_usage(client_id),
        ]

        overall = self._overall_status(checks)

        snapshot = MonitoringSnapshot(
            client_id=client_id,
            overall_status=overall,
            checks=checks,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        self._write_snapshot(snapshot)
        return snapshot

    def _check_tenant(self, client_id: str) -> MonitoringCheck:
        tenant = self.tenant_manager.get_tenant(client_id)

        if tenant is None:
            return self._check(
                client_id=client_id,
                name="tenant",
                status=HealthStatus.CRITICAL,
                message="Tenant missing",
            )

        return self._check(
            client_id=client_id,
            name="tenant",
            status=HealthStatus.HEALTHY,
            message="Tenant found",
            metadata={
                "tenant_id": tenant.tenant_id,
                "status": tenant.status.value,
                "environment": tenant.environment,
            },
        )

    def _check_billing(self, client_id: str) -> MonitoringCheck:
        billing = self.billing_manager.get_billing(client_id)

        if billing is None:
            return self._check(
                client_id=client_id,
                name="billing",
                status=HealthStatus.CRITICAL,
                message="Billing record missing",
            )

        if billing.status.value in {"PAST_DUE", "SUSPENDED", "CANCELLED"}:
            return self._check(
                client_id=client_id,
                name="billing",
                status=HealthStatus.WARNING,
                message=f"Billing status is {billing.status.value}",
                metadata={"status": billing.status.value},
            )

        return self._check(
            client_id=client_id,
            name="billing",
            status=HealthStatus.HEALTHY,
            message="Billing healthy",
            metadata={
                "status": billing.status.value,
                "period_end": billing.current_period_end,
            },
        )

    def _check_entitlement(self, client_id: str) -> MonitoringCheck:
        entitlement = self.entitlement_guard.check(client_id)

        if entitlement.status.value in {"LOCKED", "DECOMMISSIONED"}:
            return self._check(
                client_id=client_id,
                name="entitlement",
                status=HealthStatus.CRITICAL,
                message=entitlement.reason,
                metadata=asdict(entitlement),
            )

        if entitlement.status.value == "READ_ONLY":
            return self._check(
                client_id=client_id,
                name="entitlement",
                status=HealthStatus.WARNING,
                message=entitlement.reason,
                metadata=asdict(entitlement),
            )

        return self._check(
            client_id=client_id,
            name="entitlement",
            status=HealthStatus.HEALTHY,
            message=entitlement.reason,
            metadata=asdict(entitlement),
        )

    def _check_license(self, client_id: str) -> MonitoringCheck:
        validation = self.license_manager.validate(client_id)

        if not validation.valid:
            return self._check(
                client_id=client_id,
                name="license",
                status=HealthStatus.CRITICAL,
                message=validation.reason,
                metadata=asdict(validation),
            )

        return self._check(
            client_id=client_id,
            name="license",
            status=HealthStatus.HEALTHY,
            message=validation.reason,
            metadata=asdict(validation),
        )

    def _check_usage(self, client_id: str) -> MonitoringCheck:
        summary = self.usage_analytics.summarize_client(client_id)

        return self._check(
            client_id=client_id,
            name="usage",
            status=HealthStatus.HEALTHY,
            message="Usage summary available",
            metadata=asdict(summary),
        )

    def _check(
        self,
        *,
        client_id: str,
        name: str,
        status: HealthStatus,
        message: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> MonitoringCheck:
        return MonitoringCheck(
            check_id=f"check-{uuid.uuid4()}",
            client_id=client_id,
            check_name=name,
            status=status,
            message=message,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )

    def _overall_status(self, checks: list[MonitoringCheck]) -> HealthStatus:
        statuses = {check.status for check in checks}

        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL

        if HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING

        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY

        return HealthStatus.UNKNOWN

    def _write_snapshot(self, snapshot: MonitoringSnapshot) -> None:
        path = self.monitoring_root / f"{snapshot.client_id}.json"
        data = asdict(snapshot)
        data["overall_status"] = snapshot.overall_status.value

        for check in data["checks"]:
            check["status"] = (
                check["status"].value
                if hasattr(check["status"], "value")
                else check["status"]
            )

        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    manager = MonitoringManager()

    snapshot = manager.run_checks("dis_solar")

    print("")
    print("Monitoring Manager")
    print("------------------")
    print(json.dumps(asdict(snapshot), indent=2, default=str))
    print("")


if __name__ == "__main__":
    main()
