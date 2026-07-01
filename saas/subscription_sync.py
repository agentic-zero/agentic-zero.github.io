# saas/subscription_sync.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from saas.billing_manager import BillingManager
from saas.tenant_manager import TenantManager
from security.audit_logger import AuditLogger


@dataclass
class SubscriptionSyncResult:
    client_id: str
    billing_status: str
    entitlement_status: str
    synced: bool
    reason: str
    entitlement_path: str
    synced_at: str


class SubscriptionSync:
    """
    Synchronizes SaaS billing state into Security entitlement state.

    This module does NOT touch:
    - Agentic Shield
    - The Machine
    - Runtime execution

    It only writes entitlement files consumed later by SecurityGateway.
    """

    def __init__(
        self,
        *,
        billing_manager: Optional[BillingManager] = None,
        tenant_manager: Optional[TenantManager] = None,
        audit_logger: Optional[AuditLogger] = None,
        entitlement_root: str | Path = "security/state/entitlements",
    ) -> None:
        self.billing_manager = billing_manager or BillingManager()
        self.tenant_manager = tenant_manager or TenantManager()
        self.audit_logger = audit_logger or AuditLogger()
        self.entitlement_root = Path(entitlement_root)
        self.entitlement_root.mkdir(parents=True, exist_ok=True)

    def sync_client(self, client_id: str) -> SubscriptionSyncResult:
        billing = self.billing_manager.get_billing(client_id)
        tenant = self.tenant_manager.get_tenant(client_id)

        if billing is None:
            result = self._result(
                client_id=client_id,
                billing_status="MISSING",
                entitlement_status="LOCKED",
                synced=False,
                reason="Billing record missing",
            )
            self._log(result)
            return result

        entitlement_status = self.billing_manager.map_to_entitlement_status(client_id)

        entitlement = {
            "client_id": client_id,
            "status": entitlement_status,
            "plan": billing.plan,
            "product": billing.product,
            "expires_at": billing.current_period_end,
            "monthly_subscription_required": True,
            "runtime_execution_enabled": entitlement_status
            in {"ACTIVE", "GRACE_PERIOD"},
            "connectors_enabled": entitlement_status in {"ACTIVE", "GRACE_PERIOD"},
            "swarm_enabled": entitlement_status in {"ACTIVE", "GRACE_PERIOD"},
            "read_only": entitlement_status == "READ_ONLY",
            "environment": tenant.environment if tenant else "unknown",
            "tenant_id": tenant.tenant_id if tenant else None,
            "updated_from": "billing_manager",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        path = self._entitlement_path(client_id)
        path.write_text(json.dumps(entitlement, indent=2), encoding="utf-8")

        result = self._result(
            client_id=client_id,
            billing_status=billing.status.value,
            entitlement_status=entitlement_status,
            synced=True,
            reason="Billing state synchronized to entitlement state",
        )

        self._log(result)

        return result

    def sync_all(self) -> list[SubscriptionSyncResult]:
        results: list[SubscriptionSyncResult] = []

        for billing in self.billing_manager.list_billing_records():
            results.append(self.sync_client(billing.client_id))

        return results

    def _entitlement_path(self, client_id: str) -> Path:
        return self.entitlement_root / f"{client_id}.json"

    def _result(
        self,
        *,
        client_id: str,
        billing_status: str,
        entitlement_status: str,
        synced: bool,
        reason: str,
    ) -> SubscriptionSyncResult:
        return SubscriptionSyncResult(
            client_id=client_id,
            billing_status=billing_status,
            entitlement_status=entitlement_status,
            synced=synced,
            reason=reason,
            entitlement_path=str(self._entitlement_path(client_id)),
            synced_at=datetime.now(timezone.utc).isoformat(),
        )

    def _log(self, result: SubscriptionSyncResult) -> None:
        self.audit_logger.log(
            event_type="SUBSCRIPTION_SYNC",
            client_id=result.client_id,
            actor="system",
            action="sync_billing_to_entitlement",
            outcome="SUCCESS" if result.synced else "FAILED",
            severity="INFO" if result.synced else "WARNING",
            reason=result.reason,
            metadata={
                "billing_status": result.billing_status,
                "entitlement_status": result.entitlement_status,
                "entitlement_path": result.entitlement_path,
            },
        )


def main() -> None:
    tenant_manager = TenantManager()
    billing_manager = BillingManager()

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

    sync = SubscriptionSync(
        billing_manager=billing_manager,
        tenant_manager=tenant_manager,
    )

    result = sync.sync_client("dis_solar")

    print("")
    print("Subscription Sync")
    print("-----------------")
    print(json.dumps(asdict(result), indent=2))
    print("")


if __name__ == "__main__":
    main()
