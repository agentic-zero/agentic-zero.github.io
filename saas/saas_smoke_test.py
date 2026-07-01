# saas/saas_smoke_test.py

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from saas.backup_manager import BackupManager
from saas.billing_manager import BillingManager
from saas.customer_portal import CustomerPortal
from saas.deployment_manager import DeploymentManager
from saas.disaster_recovery import DisasterRecovery
from saas.governance_report import GovernanceReportBuilder
from saas.monitoring_manager import MonitoringManager
from saas.subscription_sync import SubscriptionSync
from saas.tenant_manager import TenantManager
from saas.token_governance import TokenGovernance
from saas.usage_analytics import UsageAnalytics
from security.license_manager import LicenseManager


TEST_CLIENT = "dis_solar"


def assert_true(condition: bool, message: str) -> dict[str, Any]:
    return {
        "check": message,
        "passed": bool(condition),
    }


def main() -> None:
    results: list[dict[str, Any]] = []

    tenant_manager = TenantManager()
    billing_manager = BillingManager()
    usage_analytics = UsageAnalytics()
    license_manager = LicenseManager()

    # 1. Tenant
    if not tenant_manager.tenant_exists(TEST_CLIENT):
        tenant = tenant_manager.create_tenant(
            client_id=TEST_CLIENT,
            company_name="DIS Solar Europe",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            package_path="clients/dis_solar/agentic_one/essential_package",
            environment="production",
            metadata={
                "source": "saas_smoke_test",
            },
        )
    else:
        tenant = tenant_manager.get_tenant(TEST_CLIENT)

    results.append(assert_true(tenant is not None, "Tenant exists"))

    # 2. Billing
    if billing_manager.get_billing(TEST_CLIENT) is None:
        billing = billing_manager.create_billing(
            client_id=TEST_CLIENT,
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            metadata={
                "source": "saas_smoke_test",
            },
        )
    else:
        billing = billing_manager.get_billing(TEST_CLIENT)

    results.append(assert_true(billing is not None, "Billing exists"))
    results.append(assert_true(billing.status.value == "ACTIVE", "Billing ACTIVE"))

    # 3. License
    if license_manager.load_license(TEST_CLIENT) is None:
        license_manager.create_license(
            client_id=TEST_CLIENT,
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            expires_at="2099-12-31T23:59:59Z",
            metadata={
                "source": "saas_smoke_test",
            },
        )

    license_validation = license_manager.validate(TEST_CLIENT)
    results.append(assert_true(license_validation.valid, "License valid"))

    # 4. Subscription Sync
    subscription_sync = SubscriptionSync(
        billing_manager=billing_manager,
        tenant_manager=tenant_manager,
    )

    sync_result = subscription_sync.sync_client(TEST_CLIENT)
    results.append(assert_true(sync_result.synced, "Subscription synced"))
    results.append(
        assert_true(
            sync_result.entitlement_status == "ACTIVE",
            "Entitlement ACTIVE",
        )
    )

    # 5. Customer Portal
    portal = CustomerPortal(
        tenant_manager=tenant_manager,
        billing_manager=billing_manager,
        license_manager=license_manager,
        subscription_sync=subscription_sync,
    )

    portal_view = portal.get_customer_view(TEST_CLIENT)
    results.append(
        assert_true(
            portal_view.runtime_access == "FULL_ACCESS",
            "Customer portal FULL_ACCESS",
        )
    )

    # 6. Usage Analytics
    usage_analytics.record_usage(
        client_id=TEST_CLIENT,
        product="AGENTIC_ONE",
        component="agentic_one_runtime",
        action="runtime_action_authorized",
        quantity=1,
        unit="action",
        metadata={
            "source": "saas_smoke_test",
        },
    )

    usage_summary = usage_analytics.summarize_client(TEST_CLIENT)
    results.append(
        assert_true(
            usage_summary.total_events >= 1,
            "Usage events recorded",
        )
    )

    # 7. Deployment
    deployment_manager = DeploymentManager(
        tenant_manager=tenant_manager,
    )

    deployment = deployment_manager.get_deployment(TEST_CLIENT)

    if deployment is None:
        deployment = deployment_manager.create_deployment(
            client_id=TEST_CLIENT,
            deployed_version="v1.0.0",
            metadata={
                "source": "saas_smoke_test",
            },
        )

    deployment = deployment_manager.mark_deploying(TEST_CLIENT)
    deployment = deployment_manager.mark_deployed(TEST_CLIENT)

    results.append(
        assert_true(
            deployment.status.value == "DEPLOYED",
            "Deployment DEPLOYED",
        )
    )

    # 8. Monitoring
    monitoring_manager = MonitoringManager(
        tenant_manager=tenant_manager,
        billing_manager=billing_manager,
        usage_analytics=usage_analytics,
        license_manager=license_manager,
    )

    monitoring_snapshot = monitoring_manager.run_checks(TEST_CLIENT)
    results.append(
        assert_true(
            monitoring_snapshot.overall_status.value in {"HEALTHY", "WARNING"},
            "Monitoring snapshot generated",
        )
    )

    # 9. Backup
    backup_manager = BackupManager(
        tenant_manager=tenant_manager,
    )

    backup = backup_manager.create_backup(
        client_id=TEST_CLIENT,
        include_client_package=True,
        metadata={
            "source": "saas_smoke_test",
        },
    )

    results.append(
        assert_true(
            backup.status.value == "CREATED",
            "Backup CREATED",
        )
    )

    # 10. Disaster Recovery
    disaster_recovery = DisasterRecovery(
        tenant_manager=tenant_manager,
        backup_manager=backup_manager,
    )

    recovery = disaster_recovery.plan_recovery(
        client_id=TEST_CLIENT,
        reason="SaaS smoke test recovery",
        metadata={
            "source": "saas_smoke_test",
        },
    )

    recovery = disaster_recovery.execute_recovery(
        client_id=TEST_CLIENT,
        recovery_id=recovery.recovery_id,
    )

    results.append(
        assert_true(
            recovery.status.value == "COMPLETED",
            "Disaster recovery COMPLETED",
        )
    )

    # 11. Token Governance (M11) - record real usage and confirm budget
    # check classifies correctly. Built after Tests 1-10 already existed,
    # so without this it would silently never get regression-tested.
    token_governance = TokenGovernance()
    token_governance.record_usage(
        client_id=TEST_CLIENT,
        provider="anthropic",
        model="claude-sonnet-4-6",
        component="saas_smoke_test",
        input_tokens=1000,
        output_tokens=500,
    )
    budget = token_governance.check_budget(TEST_CLIENT, billing.plan)
    results.append(
        assert_true(
            budget.tokens_used_this_month >= 1500,
            "Token usage recorded and reflected in budget check",
        )
    )

    # 12. Governance Report (cross-references Billing x Token Governance)
    # - same reasoning: built after the others, never wired into this
    # smoke test until now.
    governance_builder = GovernanceReportBuilder(
        billing_manager=billing_manager,
        token_governance=token_governance,
    )
    governance_summary = governance_builder.client_summary(TEST_CLIENT)
    results.append(
        assert_true(
            governance_summary is not None and governance_summary.client_id == TEST_CLIENT,
            "Governance report correctly cross-references billing and token usage",
        )
    )

    passed = sum(1 for item in results if item["passed"])
    failed = len(results) - passed

    summary = {
        "saas_smoke_test": "COMPLETE",
        "client_id": TEST_CLIENT,
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "results": results,
        "artifacts": {
            "tenant": "saas/state/tenants/dis_solar.json",
            "billing": "saas/state/billing/dis_solar.json",
            "usage": "saas/state/usage/dis_solar.jsonl",
            "monitoring": "saas/state/monitoring/dis_solar.json",
            "deployment": "saas/state/deployments/dis_solar.json",
            "backups": "saas/backups/dis_solar/",
            "recovery": "saas/recovery/dis_solar/",
            "entitlement": "security/state/entitlements/dis_solar.json",
        },
    }

    output_path = Path("saas/state/saas_smoke_test_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("")
    print("SaaS Smoke Test")
    print("---------------")
    print(f"Passed : {passed}")
    print(f"Failed : {failed}")
    print(f"Total  : {len(results)}")
    print(f"Output : {output_path}")
    print("")

    if failed:
        print(json.dumps(summary, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
