# client_access/customer_downloads.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from client_access.artifact_delivery_manager import ArtifactDeliveryManager
from client_access.package_access_manager import PackageAccessManager


@dataclass
class CustomerDownloadItem:
    client_id: str
    resource: str
    title: str
    category: str
    available: bool
    access_allowed: bool
    reason: str
    generated_at: str
    metadata: dict[str, Any]


class CustomerDownloads:
    """
    Customer-facing download catalogue.

    The customer can only see/download resources that pass:
    - AccessBoundary
    - PackageAccessManager
    - license / entitlement checks

    This module never exposes internal engines or code.
    """

    DEFAULT_RESOURCES = [
        {
            "resource": "customer_packages/{client_id}/package.zip",
            "title": "Delivered Agentic Package",
            "category": "package",
        },
        {
            "resource": "reports/{client_id}/roi_report.pdf",
            "title": "ROI Report",
            "category": "report",
        },
        {
            "resource": "reports/{client_id}/audit_summary.pdf",
            "title": "Audit Summary",
            "category": "report",
        },
        {
            "resource": "docs/customer/{client_id}/user_guide.pdf",
            "title": "Customer User Guide",
            "category": "documentation",
        },
        {
            "resource": "licenses/customer/{client_id}/license_summary.pdf",
            "title": "License Summary",
            "category": "license",
        },
    ]

    def __init__(
        self,
        *,
        package_access_manager: Optional[PackageAccessManager] = None,
        artifact_delivery_manager: Optional[ArtifactDeliveryManager] = None,
        catalogue_root: str | Path = "client_access/state/downloads",
    ) -> None:
        self.package_access_manager = package_access_manager or PackageAccessManager()
        self.artifact_delivery_manager = (
            artifact_delivery_manager
            or ArtifactDeliveryManager(
                package_access_manager=self.package_access_manager
            )
        )
        self.catalogue_root = Path(catalogue_root)
        self.catalogue_root.mkdir(parents=True, exist_ok=True)

    def list_downloads(self, client_id: str) -> list[CustomerDownloadItem]:
        items: list[CustomerDownloadItem] = []

        for entry in self.DEFAULT_RESOURCES:
            resource = entry["resource"].format(client_id=client_id)

            access = self.package_access_manager.authorize_package_access(
                client_id=client_id,
                resource=resource,
                action="view",
                metadata={
                    "stage": "list_downloads",
                    "category": entry["category"],
                },
            )

            items.append(
                CustomerDownloadItem(
                    client_id=client_id,
                    resource=resource,
                    title=entry["title"],
                    category=entry["category"],
                    available=Path(resource).exists(),
                    access_allowed=access.allowed,
                    reason=access.reason,
                    generated_at=datetime.now(timezone.utc).isoformat(),
                    metadata={
                        "mode": access.mode.value,
                        "entitlement_status": access.entitlement_status,
                    },
                )
            )

        self._write_catalogue(client_id, items)
        return items

    def request_download(
        self,
        *,
        client_id: str,
        resource: str,
        metadata: Optional[dict[str, Any]] = None,
    ):
        access = self.package_access_manager.authorize_package_access(
            client_id=client_id,
            resource=resource,
            action="download",
            metadata={
                **(metadata or {}),
                "stage": "request_download",
            },
        )

        if not access.allowed:
            return {
                "client_id": client_id,
                "resource": resource,
                "download_allowed": False,
                "reason": access.reason,
                "delivery": None,
            }

        delivery = self.artifact_delivery_manager.prepare_delivery(
            client_id=client_id,
            source_artifact=resource,
            metadata={
                **(metadata or {}),
                "stage": "customer_download",
            },
        )

        return {
            "client_id": client_id,
            "resource": resource,
            "download_allowed": delivery.status.value in {"PREPARED", "DELIVERED"},
            "reason": delivery.reason,
            "delivery": asdict(delivery),
        }

    def _write_catalogue(
        self,
        client_id: str,
        items: list[CustomerDownloadItem],
    ) -> None:
        path = self.catalogue_root / f"{client_id}.json"
        path.write_text(
            json.dumps([asdict(item) for item in items], indent=2),
            encoding="utf-8",
        )


def main() -> None:
    downloads = CustomerDownloads()

    items = downloads.list_downloads("dis_solar")

    request = downloads.request_download(
        client_id="dis_solar",
        resource="customer_packages/dis_solar/package.zip",
        metadata={"test": True},
    )

    blocked = downloads.request_download(
        client_id="dis_solar",
        resource="agentic_shield/policy_engine.py",
        metadata={"test": True},
    )

    output_path = Path("client_access/state/customer_downloads_test_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "items": [asdict(item) for item in items],
                "allowed_request": request,
                "blocked_request": blocked,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("")
    print("Customer Downloads")
    print("------------------")
    print(f"Catalogue items : {len(items)}")
    print(f"Allowed request : {request['download_allowed']}")
    print(f"Blocked request : {blocked['download_allowed']}")
    print(f"Output          : {output_path}")
    print("")


if __name__ == "__main__":
    main()
