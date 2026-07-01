# security/security_smoke_test.py

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from security.audit_logger import AuditLogger
from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager
from security.security_gateway import SecurityGateway


TEST_CLIENT = "dis_solar"


def write_entitlement(
    *,
    client_id: str,
    status: str,
    plan: str = "ENTERPRISE",
    expires_at: str | None = "2099-12-31T23:59:59Z",
) -> Path:
    root = Path("security/state/entitlements")
    root.mkdir(parents=True, exist_ok=True)

    file_path = root / f"{client_id}.json"

    data = {
        "client_id": client_id,
        "status": status,
        "plan": plan,
        "product": "AGENTIC_ONE",
        "expires_at": expires_at,
        "monthly_subscription_required": True,
        "runtime_execution_enabled": status in {"ACTIVE", "GRACE_PERIOD"},
        "connectors_enabled": status in {"ACTIVE", "GRACE_PERIOD"},
        "swarm_enabled": status in {"ACTIVE", "GRACE_PERIOD"},
    }

    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return file_path


def ensure_license(
    *,
    client_id: str,
    license_manager: LicenseManager,
    expires_at: str = "2099-12-31T23:59:59Z",
) -> None:
    existing = license_manager.load_license(client_id)

    if existing is None:
        license_manager.create_license(
            client_id=client_id,
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            expires_at=expires_at,
            metadata={
                "environment": "security_smoke_test",
            },
        )


def run_case(
    *,
    name: str,
    gateway: SecurityGateway,
    client_id: str,
    action: str,
    component: str,
    risk_level: str,
    governance_required: bool,
    expected_decision: str,
) -> dict[str, Any]:
    result = gateway.authorize(
        client_id=client_id,
        action=action,
        component=component,
        actor="security_smoke_test",
        autonomy_level=72,
        governance_required=governance_required,
        risk_level=risk_level,
        metadata={
            "test_case": name,
        },
    )

    passed = result.decision == expected_decision

    return {
        "case": name,
        "expected": expected_decision,
        "actual": result.decision,
        "passed": passed,
        "reason": result.reason,
        "result": asdict(result),
    }


def main() -> None:
    audit_logger = AuditLogger()
    license_manager = LicenseManager(audit_logger=audit_logger)
    entitlement_guard = EntitlementGuard()

    ensure_license(
        client_id=TEST_CLIENT,
        license_manager=license_manager,
    )

    gateway = SecurityGateway(
        audit_logger=audit_logger,
        license_manager=license_manager,
        entitlement_guard=entitlement_guard,
    )

    cases: list[dict[str, Any]] = []

    # 1. ACTIVE -> execute allowed
    write_entitlement(client_id=TEST_CLIENT, status="ACTIVE")
    cases.append(
        run_case(
            name="ACTIVE allows execution",
            gateway=gateway,
            client_id=TEST_CLIENT,
            action="execute",
            component="agentic_one_runtime",
            risk_level="MEDIUM",
            governance_required=True,
            expected_decision="ALLOW",
        )
    )

    # 2. READ_ONLY -> write denied
    write_entitlement(client_id=TEST_CLIENT, status="READ_ONLY")
    cases.append(
        run_case(
            name="READ_ONLY blocks write",
            gateway=gateway,
            client_id=TEST_CLIENT,
            action="execute",
            component="agentic_one_runtime",
            risk_level="MEDIUM",
            governance_required=True,
            expected_decision="DENY",
        )
    )

    # 3. READ_ONLY -> read allowed through subscription gate, but policy maps READ_ONLY to deny execution path
    write_entitlement(client_id=TEST_CLIENT, status="READ_ONLY")
    cases.append(
        run_case(
            name="READ_ONLY blocks runtime report through gateway policy",
            gateway=gateway,
            client_id=TEST_CLIENT,
            action="report",
            component="enterprise_dashboard",
            risk_level="LOW",
            governance_required=False,
            expected_decision="DENY",
        )
    )

    # 4. LOCKED -> all denied
    write_entitlement(client_id=TEST_CLIENT, status="LOCKED")
    cases.append(
        run_case(
            name="LOCKED blocks execution",
            gateway=gateway,
            client_id=TEST_CLIENT,
            action="execute",
            component="agentic_one_runtime",
            risk_level="MEDIUM",
            governance_required=True,
            expected_decision="DENY",
        )
    )

    # 5. ACTIVE + CRITICAL + governance required -> escalate
    write_entitlement(client_id=TEST_CLIENT, status="ACTIVE")
    cases.append(
        run_case(
            name="CRITICAL risk escalates",
            gateway=gateway,
            client_id=TEST_CLIENT,
            action="reroute",
            component="logistics_organism",
            risk_level="CRITICAL",
            governance_required=True,
            expected_decision="ESCALATE",
        )
    )

    # 6. Missing client -> denied
    cases.append(
        run_case(
            name="MISSING client blocks execution",
            gateway=gateway,
            client_id="missing_client",
            action="execute",
            component="agentic_one_runtime",
            risk_level="MEDIUM",
            governance_required=True,
            expected_decision="DENY",
        )
    )

    passed = sum(1 for c in cases if c["passed"])
    failed = len(cases) - passed

    summary = {
        "security_smoke_test": "COMPLETE",
        "client_id": TEST_CLIENT,
        "passed": passed,
        "failed": failed,
        "total": len(cases),
        "cases": cases,
    }

    output_path = Path("security/state/security_smoke_test_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("")
    print("Security Smoke Test")
    print("-------------------")
    print(f"Passed : {passed}")
    print(f"Failed : {failed}")
    print(f"Total  : {len(cases)}")
    print(f"Output : {output_path}")
    print("")

    if failed:
        print(json.dumps(summary, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
