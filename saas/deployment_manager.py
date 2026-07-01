# saas/deployment_manager.py

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from saas.tenant_manager import TenantManager


class DeploymentStatus(str, Enum):
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    DEPLOYED = "DEPLOYED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class DeploymentRecord:
    deployment_id: str
    client_id: str
    product: str
    plan: str
    environment: str
    package_path: str
    status: DeploymentStatus
    deployed_version: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]


class DeploymentManager:
    """
    SaaS deployment manager for Agentic Zero.

    This module does NOT execute Shield, The Machine or runtime actions.

    Responsibilities:
    - create deployment record
    - mark deployment lifecycle
    - track deployed version
    - support rollback metadata
    - expose deployment state for monitoring/customer portal
    """

    def __init__(
        self,
        *,
        tenant_manager: Optional[TenantManager] = None,
        deployment_root: str | Path = "saas/state/deployments",
    ) -> None:
        self.tenant_manager = tenant_manager or TenantManager()
        self.deployment_root = Path(deployment_root)
        self.deployment_root.mkdir(parents=True, exist_ok=True)

    def create_deployment(
        self,
        *,
        client_id: str,
        deployed_version: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> DeploymentRecord:
        tenant = self.tenant_manager.get_tenant(client_id)

        if tenant is None:
            raise FileNotFoundError(f"Tenant not found for client_id='{client_id}'")

        now = datetime.now(timezone.utc).isoformat()

        record = DeploymentRecord(
            deployment_id=f"deploy-{uuid.uuid4()}",
            client_id=client_id,
            product=tenant.product,
            plan=tenant.plan,
            environment=tenant.environment,
            package_path=tenant.package_path,
            status=DeploymentStatus.PENDING,
            deployed_version=deployed_version,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        self._write(record)
        return record

    def mark_deploying(
        self, client_id: str, reason: str = "Deployment started"
    ) -> DeploymentRecord:
        return self._update_status(
            client_id=client_id,
            status=DeploymentStatus.DEPLOYING,
            reason=reason,
        )

    def mark_deployed(
        self, client_id: str, reason: str = "Deployment completed"
    ) -> DeploymentRecord:
        return self._update_status(
            client_id=client_id,
            status=DeploymentStatus.DEPLOYED,
            reason=reason,
        )

    def mark_failed(self, client_id: str, reason: str) -> DeploymentRecord:
        return self._update_status(
            client_id=client_id,
            status=DeploymentStatus.FAILED,
            reason=reason,
        )

    def mark_rolled_back(
        self, client_id: str, reason: str = "Deployment rolled back"
    ) -> DeploymentRecord:
        return self._update_status(
            client_id=client_id,
            status=DeploymentStatus.ROLLED_BACK,
            reason=reason,
        )

    def get_deployment(self, client_id: str) -> Optional[DeploymentRecord]:
        path = self._path(client_id)

        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            try:
                status = DeploymentStatus(data["status"])
            except ValueError:
                # Corrupted/hand-edited status. Fail CLOSED to FAILED -
                # a deployment of unknown status must never be reported
                # as DEPLOYED/healthy by default.
                status = DeploymentStatus.FAILED

            return DeploymentRecord(
                deployment_id=data["deployment_id"],
                client_id=data["client_id"],
                product=data["product"],
                plan=data["plan"],
                environment=data["environment"],
                package_path=data["package_path"],
                status=status,
                deployed_version=data["deployed_version"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError):
            return None

    def list_deployments(self) -> list[DeploymentRecord]:
        deployments: list[DeploymentRecord] = []

        for file in sorted(self.deployment_root.glob("*.json")):
            record = self.get_deployment(file.stem)
            if record:
                deployments.append(record)

        return deployments

    def _update_status(
        self,
        *,
        client_id: str,
        status: DeploymentStatus,
        reason: str,
    ) -> DeploymentRecord:
        record = self._require(client_id)
        record.status = status
        record.updated_at = datetime.now(timezone.utc).isoformat()
        record.metadata["last_status_reason"] = reason

        self._write(record)
        return record

    def _require(self, client_id: str) -> DeploymentRecord:
        record = self.get_deployment(client_id)

        if record is None:
            raise FileNotFoundError(f"Deployment not found for client_id='{client_id}'")

        return record

    def _write(self, record: DeploymentRecord) -> None:
        data = asdict(record)
        data["status"] = record.status.value

        self._path(record.client_id).write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def _path(self, client_id: str) -> Path:
        return self.deployment_root / f"{client_id}.json"


def main() -> None:
    tenant_manager = TenantManager()

    if not tenant_manager.tenant_exists("dis_solar"):
        tenant_manager.create_tenant(
            client_id="dis_solar",
            company_name="DIS Solar Europe",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            package_path="clients/dis_solar/agentic_one/essential_package",
            environment="production",
        )

    manager = DeploymentManager(tenant_manager=tenant_manager)

    deployment = manager.get_deployment("dis_solar")

    if deployment is None:
        deployment = manager.create_deployment(
            client_id="dis_solar",
            deployed_version="v1.0.0",
            metadata={
                "source": "deployment_manager_test",
            },
        )

    deployment = manager.mark_deploying("dis_solar")
    deployment = manager.mark_deployed("dis_solar")

    print("")
    print("Deployment Manager")
    print("------------------")
    print(json.dumps(asdict(deployment), indent=2))
    print("")


if __name__ == "__main__":
    main()
