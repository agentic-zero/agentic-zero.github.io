# client_access/client_access_smoke_test.py

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from client_access.access_boundary import AccessBoundary
from client_access.artifact_delivery_manager import (
    ArtifactDeliveryManager,
    DeliveryStatus,
)
from client_access.client_portal_auth import ClientPortalAuth
from client_access.customer_downloads import CustomerDownloads
from client_access.package_access_manager import PackageAccessManager
from client_access.package_license_guard import PackageLicenseGuard
from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager


TEST_CLIENT = "dis_solar"


def check(condition: bool, message: str) -> dict[str, Any]:
    return {
        "check": message,
        "passed": bool(condition),
    }


def ensure_license_and_entitlement() -> None:
    license_manager = LicenseManager()
    entitlement_guard = EntitlementGuard()

    if license_manager.load_license(TEST_CLIENT) is None:
        license_manager.create_license(
            client_id=TEST_CLIENT,
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            expires_at="2099-12-31T23:59:59Z",
            metadata={
                "source": "client_access_smoke_test",
            },
        )

    entitlement_guard.create_demo_entitlement(TEST_CLIENT)


def main() -> None:
    ensure_license_and_entitlement()

    results: list[dict[str, Any]] = []

    # 1. Access Boundary
    boundary = AccessBoundary()

    customer_package = boundary.authorize_resource_access(
        client_id=TEST_CLIENT,
        resource="customer_packages/dis_solar/package.zip",
    )

    internal_engine = boundary.authorize_resource_access(
        client_id=TEST_CLIENT,
        resource="the_machine/evolution_engine.py",
    )

    internal_security = boundary.authorize_resource_access(
        client_id=TEST_CLIENT,
        resource="security/license_manager.py",
    )

    results.append(
        check(
            customer_package.decision.value == "ALLOW",
            "Customer package allowed by AccessBoundary",
        )
    )

    results.append(
        check(
            internal_engine.decision.value == "DENY",
            "The Machine denied by AccessBoundary",
        )
    )

    results.append(
        check(
            internal_security.decision.value == "DENY",
            "Security source denied by AccessBoundary",
        )
    )

    # 2. Package Access Manager
    package_access = PackageAccessManager()

    package_decision = package_access.authorize_package_access(
        client_id=TEST_CLIENT,
        resource="customer_packages/dis_solar/package.zip",
        action="download",
    )

    shield_decision = package_access.authorize_package_access(
        client_id=TEST_CLIENT,
        resource="agentic_shield/policy_engine.py",
        action="download",
    )

    results.append(
        check(
            package_decision.allowed,
            "Customer package allowed by PackageAccessManager",
        )
    )

    results.append(
        check(
            not shield_decision.allowed,
            "Agentic Shield source denied by PackageAccessManager",
        )
    )

    # 3. Artifact Delivery
    delivery_manager = ArtifactDeliveryManager(
        package_access_manager=package_access,
    )

    allowed_delivery = delivery_manager.prepare_delivery(
        client_id=TEST_CLIENT,
        source_artifact="customer_packages/dis_solar/package.zip",
        metadata={
            "source": "client_access_smoke_test",
        },
    )

    blocked_delivery = delivery_manager.prepare_delivery(
        client_id=TEST_CLIENT,
        source_artifact="runtime_core/event_router.py",
        metadata={
            "source": "client_access_smoke_test",
        },
    )

    if allowed_delivery.status == DeliveryStatus.PREPARED:
        allowed_delivery = delivery_manager.mark_delivered(
            client_id=TEST_CLIENT,
            delivery_id=allowed_delivery.delivery_id,
        )

    results.append(
        check(
            allowed_delivery.status.value == "DELIVERED",
            "Allowed artifact delivered",
        )
    )

    results.append(
        check(
            blocked_delivery.status.value == "BLOCKED",
            "Internal artifact delivery blocked",
        )
    )

    # 4. Customer Downloads
    downloads = CustomerDownloads(
        package_access_manager=package_access,
        artifact_delivery_manager=delivery_manager,
    )

    catalogue = downloads.list_downloads(TEST_CLIENT)

    allowed_download = downloads.request_download(
        client_id=TEST_CLIENT,
        resource="customer_packages/dis_solar/package.zip",
        metadata={
            "source": "client_access_smoke_test",
        },
    )

    blocked_download = downloads.request_download(
        client_id=TEST_CLIENT,
        resource="the_machine/evolution_engine.py",
        metadata={
            "source": "client_access_smoke_test",
        },
    )

    results.append(
        check(
            len(catalogue) >= 5,
            "Customer download catalogue generated",
        )
    )

    results.append(
        check(
            bool(allowed_download["download_allowed"]),
            "Allowed customer download approved",
        )
    )

    results.append(
        check(
            not bool(blocked_download["download_allowed"]),
            "Internal download blocked",
        )
    )

    # 5. Client Portal Auth
    auth = ClientPortalAuth(
        package_access_manager=package_access,
    )

    if (
        auth.get_user_by_email(
            client_id=TEST_CLIENT,
            email="elena.martin@dissolar.eu",
        )
        is None
    ):
        auth.create_user(
            client_id=TEST_CLIENT,
            email="elena.martin@dissolar.eu",
            name="Elena Martin",
            role="Customer Admin",
            password="ChangeMe123!",
            metadata={
                "source": "client_access_smoke_test",
            },
        )

    login = auth.login(
        client_id=TEST_CLIENT,
        email="elena.martin@dissolar.eu",
        password="ChangeMe123!",
        metadata={
            "source": "client_access_smoke_test",
        },
    )

    results.append(
        check(
            login.success and login.session is not None,
            "Client portal login successful",
        )
    )

    if login.session:
        session_allowed = auth.authorize_session_resource(
            session_id=login.session.session_id,
            resource="customer_packages/dis_solar/package.zip",
            action="view",
        )

        session_denied = auth.authorize_session_resource(
            session_id=login.session.session_id,
            resource="agentic_shield/policy_engine.py",
            action="view",
        )

        results.append(
            check(
                bool(session_allowed["allowed"]),
                "Portal session can view customer package",
            )
        )

        results.append(
            check(
                not bool(session_denied["allowed"]),
                "Portal session cannot view Agentic Shield source",
            )
        )

    # 6. Package License Guard
    package_guard = PackageLicenseGuard()

    runtime_decision = package_guard.check_package_runtime(
        client_id=TEST_CLIENT,
        package_id="agentic_one_enterprise_package",
        metadata={
            "source": "client_access_smoke_test",
        },
    )

    results.append(
        check(
            runtime_decision.execution_allowed,
            "Package runtime execution allowed for ACTIVE client",
        )
    )

    results.append(
        check(
            runtime_decision.connector_allowed,
            "Package connectors allowed for ACTIVE client",
        )
    )

    results.append(
        check(
            runtime_decision.swarm_allowed,
            "Package swarm allowed for ACTIVE client",
        )
    )

    passed = sum(1 for result in results if result["passed"])
    failed = len(results) - passed

    summary = {
        "client_access_smoke_test": "COMPLETE",
        "client_id": TEST_CLIENT,
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "results": results,
        "artifacts": {
            "access_boundary": "client_access/state/access_boundary_test_result.json",
            "package_access": "client_access/state/package_access_test_result.json",
            "deliveries": "client_access/deliveries/dis_solar/",
            "downloads": "client_access/state/downloads/dis_solar.json",
            "sessions": "client_access/state/sessions/",
            "package_license_guard": "client_access/state/package_license_guard_test_result.json",
        },
    }

    output = Path("client_access/state/client_access_smoke_test_result.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("")
    print("Client Access Smoke Test")
    print("------------------------")
    print(f"Passed : {passed}")
    print(f"Failed : {failed}")
    print(f"Total  : {len(results)}")
    print(f"Output : {output}")
    print("")

    if failed:
        print(json.dumps(summary, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
