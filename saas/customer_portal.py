# saas/customer_portal.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from saas.billing_manager import BillingManager
from saas.subscription_sync import SubscriptionSync
from saas.tenant_manager import TenantManager
from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager
from security.audit_logger import AuditLogger


@dataclass
class CustomerPortalView:
    client_id: str
    company_name: str
    product: str
    plan: str
    tenant_status: str
    billing_status: str
    entitlement_status: str
    license_status: str
    monthly_amount: float
    currency: str
    current_period_end: Optional[str]
    package_path: str
    environment: str
    runtime_access: str
    generated_at: str
    metadata: dict[str, Any]


class CustomerPortal:
    """
    Read-oriented customer portal backend for Agentic Zero.

    This module does NOT touch:
    - Agentic Shield
    - The Machine
    - Runtime execution

    Responsibilities:
    - expose tenant status
    - expose billing status
    - expose entitlement status
    - expose license status
    - expose runtime access summary
    - support future UI/API
    """

    def __init__(
        self,
        *,
        tenant_manager: Optional[TenantManager] = None,
        billing_manager: Optional[BillingManager] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
        license_manager: Optional[LicenseManager] = None,
        subscription_sync: Optional[SubscriptionSync] = None,
    ) -> None:
        self.tenant_manager = tenant_manager or TenantManager()
        self.billing_manager = billing_manager or BillingManager()
        self.entitlement_guard = entitlement_guard or EntitlementGuard()
        self.license_manager = license_manager or LicenseManager(
            audit_logger=AuditLogger()
        )
        self.subscription_sync = subscription_sync or SubscriptionSync(
            billing_manager=self.billing_manager,
            tenant_manager=self.tenant_manager,
        )

    def get_customer_view(
        self, client_id: str, sync_subscription: bool = True
    ) -> CustomerPortalView:
        if sync_subscription:
            self.subscription_sync.sync_client(client_id)

        tenant = self.tenant_manager.get_tenant(client_id)
        billing = self.billing_manager.get_billing(client_id)
        entitlement = self.entitlement_guard.check(client_id)
        license_validation = self.license_manager.validate(client_id)

        if tenant is None:
            raise FileNotFoundError(f"Tenant not found for client_id='{client_id}'")

        runtime_access = self._runtime_access_label(
            execution_allowed=entitlement.execution_allowed,
            write_allowed=entitlement.write_allowed,
            read_allowed=entitlement.read_allowed,
        )

        return CustomerPortalView(
            client_id=client_id,
            company_name=tenant.company_name,
            product=tenant.product,
            plan=tenant.plan,
            tenant_status=tenant.status.value,
            billing_status=billing.status.value if billing else "MISSING",
            entitlement_status=entitlement.status.value,
            license_status=license_validation.status,
            monthly_amount=billing.monthly_amount if billing else 0.0,
            currency=billing.currency if billing else "N/A",
            current_period_end=billing.current_period_end if billing else None,
            package_path=tenant.package_path,
            environment=tenant.environment,
            runtime_access=runtime_access,
            generated_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "license_valid": license_validation.valid,
                "entitlement_reason": entitlement.reason,
                "subscription_required": True,
            },
        )

    def export_customer_view_json(self, client_id: str) -> str:
        view = self.get_customer_view(client_id)
        return json.dumps(asdict(view), indent=2)

    def _runtime_access_label(
        self,
        *,
        execution_allowed: bool,
        write_allowed: bool,
        read_allowed: bool,
    ) -> str:
        if execution_allowed and write_allowed and read_allowed:
            return "FULL_ACCESS"

        if read_allowed and not execution_allowed:
            return "READ_ONLY"

        if not read_allowed and not execution_allowed:
            return "LOCKED"

        return "LIMITED"


def main() -> None:
    tenant_manager = TenantManager()
    billing_manager = BillingManager()
    license_manager = LicenseManager()

    if not tenant_manager.tenant_exists("dis_solar"):
        tenant_manager.create_tenant(
            client_id="dis_solar",
            company_name="DIS Solar Europe",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            package_path="clients/dis_solar/agentic_one/essential_package",
            environment="production",
        )

    if billing_manager.get_billing("dis_solar") is None:
        billing_manager.create_billing(
            client_id="dis_solar",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
        )

    if license_manager.load_license("dis_solar") is None:
        license_manager.create_license(
            client_id="dis_solar",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            expires_at="2099-12-31T23:59:59Z",
        )

    portal = CustomerPortal(
        tenant_manager=tenant_manager,
        billing_manager=billing_manager,
        license_manager=license_manager,
    )

    print("")
    print("Customer Portal")
    print("---------------")
    print(portal.export_customer_view_json("dis_solar"))
    print("")


if __name__ == "__main__":
    main()
