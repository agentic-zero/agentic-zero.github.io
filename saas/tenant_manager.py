# saas/tenant_manager.py

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class TenantStatus(str, Enum):
    ACTIVE = "ACTIVE"
    GRACE_PERIOD = "GRACE_PERIOD"
    READ_ONLY = "READ_ONLY"
    LOCKED = "LOCKED"
    DECOMMISSIONED = "DECOMMISSIONED"


@dataclass
class TenantRecord:
    tenant_id: str
    client_id: str
    company_name: str
    product: str
    plan: str
    status: TenantStatus
    package_path: str
    environment: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]


class TenantManager:
    """
    SaaS tenant registry for Agentic Zero.

    This module does NOT touch Shield or The Machine.

    Responsibilities:
    - create tenant
    - read tenant
    - update tenant status
    - locate client package
    - expose tenant metadata for billing/security/deployment
    """

    def __init__(self, tenant_root: str | Path = "saas/state/tenants") -> None:
        self.tenant_root = Path(tenant_root)
        self.tenant_root.mkdir(parents=True, exist_ok=True)

    def create_tenant(
        self,
        *,
        client_id: str,
        company_name: str,
        product: str,
        plan: str,
        package_path: str,
        environment: str = "production",
        metadata: Optional[dict[str, Any]] = None,
    ) -> TenantRecord:
        now = datetime.now(timezone.utc).isoformat()

        record = TenantRecord(
            tenant_id=f"tenant-{uuid.uuid4()}",
            client_id=client_id,
            company_name=company_name,
            product=product,
            plan=plan,
            status=TenantStatus.ACTIVE,
            package_path=package_path,
            environment=environment,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        self._write(record)
        return record

    def get_tenant(self, client_id: str) -> Optional[TenantRecord]:
        path = self._path(client_id)

        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            try:
                status = TenantStatus(data["status"])
            except ValueError:
                # Corrupted/hand-edited status. Fail CLOSED to LOCKED -
                # same principle as security/entitlement_guard.py.
                status = TenantStatus.LOCKED

            return TenantRecord(
                tenant_id=data["tenant_id"],
                client_id=data["client_id"],
                company_name=data["company_name"],
                product=data["product"],
                plan=data["plan"],
                status=status,
                package_path=data["package_path"],
                environment=data["environment"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError):
            return None

    def update_status(
        self,
        *,
        client_id: str,
        status: TenantStatus,
        reason: str,
    ) -> TenantRecord:
        record = self._require(client_id)
        record.status = status
        record.updated_at = datetime.now(timezone.utc).isoformat()
        record.metadata["last_status_reason"] = reason

        self._write(record)
        return record

    def list_tenants(self) -> list[TenantRecord]:
        tenants: list[TenantRecord] = []

        for file in sorted(self.tenant_root.glob("*.json")):
            record = self.get_tenant(file.stem)
            if record:
                tenants.append(record)

        return tenants

    def tenant_exists(self, client_id: str) -> bool:
        return self._path(client_id).exists()

    def _require(self, client_id: str) -> TenantRecord:
        record = self.get_tenant(client_id)

        if record is None:
            raise FileNotFoundError(f"Tenant not found for client_id='{client_id}'")

        return record

    def _write(self, record: TenantRecord) -> None:
        data = asdict(record)
        data["status"] = record.status.value
        self._path(record.client_id).write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def _path(self, client_id: str) -> Path:
        return self.tenant_root / f"{client_id}.json"


def main() -> None:
    manager = TenantManager()

    if not manager.tenant_exists("dis_solar"):
        tenant = manager.create_tenant(
            client_id="dis_solar",
            company_name="DIS Solar Europe",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            package_path="clients/dis_solar/agentic_one/essential_package",
            environment="production",
            metadata={
                "industry": "Renewable Energy Distribution",
                "countries": 14,
                "source": "synthetic_fixture",
            },
        )
    else:
        tenant = manager.get_tenant("dis_solar")

    print("")
    print("Tenant Manager")
    print("--------------")
    print(json.dumps(asdict(tenant), indent=2))
    print("")


if __name__ == "__main__":
    main()
