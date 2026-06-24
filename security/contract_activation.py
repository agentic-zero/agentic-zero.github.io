# security/contract_activation.py

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from security.audit_logger import AuditLogger
from security.entitlement_guard import EntitlementGuard, EntitlementStatus
from security.license_manager import LicenseManager


@dataclass
class ActivationResult:
    client_id: str
    stage: str
    license_id: Optional[str]
    entitlement_status: str
    activated_by: str
    contract_reference: str


class ContractActivation:
    """
    The human gate between commercial interest (AUDIT form, proposal) and
    real runtime access (license + entitlement).

    Nothing upstream of this module - audit.html, advanced-audit.html,
    Scout Comercial, the proposal generator - is allowed to create a
    license or an entitlement on its own. A lead filling a form is
    interest, not a contract. This module exists so that the ONLY way a
    client gets a real license is a named human explicitly confirming a
    signed contract, with a mandatory reference and reason - same pattern
    as agentic_shield/human_accountability.py: no empty attribution, no
    silent automation, every activation is a permanent audit record.

    Lifecycle:
      provision_from_contract()  -> contract signed, license created,
                                     entitlement created in READ_ONLY
                                     (client exists, dashboard can show
                                     build progress, execution_allowed
                                     stays False - there is nothing real
                                     to execute yet).
      go_live()                  -> deploy finished, entitlement flips
                                     READ_ONLY -> ACTIVE. Separate,
                                     explicit human action.
      deactivate()               -> non-payment / churn / decommission,
                                     entitlement flips to LOCKED or
                                     DECOMMISSIONED. Always attributable.

    Output:
      security/state/licenses/<client_id>.json        (via LicenseManager)
      security/state/entitlements/<client_id>.json     (via EntitlementGuard)
      security/state/audit_logs/<client_id>.jsonl      (CRITICAL events for
                                                          every transition)
    """

    def __init__(
        self,
        *,
        audit_logger: Optional[AuditLogger] = None,
        license_manager: Optional[LicenseManager] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
    ) -> None:
        self.audit_logger = audit_logger or AuditLogger()
        self.license_manager = license_manager or LicenseManager(
            audit_logger=self.audit_logger
        )
        self.entitlement_guard = entitlement_guard or EntitlementGuard()

    def _require_attribution(self, activated_by: str, contract_reference: str) -> None:
        if not activated_by or not activated_by.strip():
            raise ValueError(
                "activated_by cannot be empty - every contract activation "
                "must be attributable to a named person."
            )
        if not contract_reference or not contract_reference.strip():
            raise ValueError(
                "contract_reference cannot be empty - every activation must "
                "cite the signed contract/document it is based on."
            )

    def provision_from_contract(
        self,
        *,
        client_id: str,
        product: str,
        plan: str,
        expires_at: Optional[str],
        activated_by: str,
        contract_reference: str,
        monthly_subscription_required: bool = True,
        connectors_enabled: bool = True,
        swarm_enabled: bool = True,
    ) -> ActivationResult:
        self._require_attribution(activated_by, contract_reference)

        existing_license = self.license_manager.load_license(client_id)
        if existing_license is not None:
            raise ValueError(
                f"Client '{client_id}' already has a license "
                f"(license_id={existing_license.license_id}, "
                f"status={existing_license.status.value}). "
                f"Use go_live()/deactivate() to change its lifecycle stage, "
                f"not provision_from_contract() again."
            )

        license_record = self.license_manager.create_license(
            client_id=client_id,
            product=product,
            plan=plan,
            expires_at=expires_at,
            monthly_subscription_required=monthly_subscription_required,
            metadata={
                "activated_by": activated_by,
                "contract_reference": contract_reference,
                "lifecycle_stage": "PROVISIONING",
            },
        )

        self.entitlement_guard.provision(
            client_id=client_id,
            product=product,
            plan=plan,
            expires_at=expires_at,
            monthly_subscription_required=monthly_subscription_required,
            connectors_enabled=connectors_enabled,
            swarm_enabled=swarm_enabled,
        )

        self.audit_logger.log(
            event_type="CONTRACT_ACTIVATED",
            client_id=client_id,
            actor=activated_by,
            action="provision_from_contract",
            outcome="SUCCESS",
            severity="CRITICAL",
            reason=f"Contract signed - provisioning client (read-only until go-live)",
            metadata={
                "license_id": license_record.license_id,
                "product": product,
                "plan": plan,
                "expires_at": expires_at,
                "contract_reference": contract_reference,
            },
        )

        return ActivationResult(
            client_id=client_id,
            stage="PROVISIONING",
            license_id=license_record.license_id,
            entitlement_status=EntitlementStatus.READ_ONLY.value,
            activated_by=activated_by,
            contract_reference=contract_reference,
        )

    def go_live(
        self,
        *,
        client_id: str,
        activated_by: str,
        contract_reference: str,
    ) -> ActivationResult:
        self._require_attribution(activated_by, contract_reference)

        license_record = self.license_manager.load_license(client_id)
        if license_record is None:
            raise ValueError(
                f"Client '{client_id}' has no license on file. "
                f"Run provision_from_contract() first."
            )

        self.entitlement_guard.set_status(client_id, EntitlementStatus.ACTIVE)

        self.audit_logger.log(
            event_type="CONTRACT_GO_LIVE",
            client_id=client_id,
            actor=activated_by,
            action="go_live",
            outcome="SUCCESS",
            severity="CRITICAL",
            reason="Deploy complete - client moved from provisioning to active execution",
            metadata={
                "license_id": license_record.license_id,
                "contract_reference": contract_reference,
            },
        )

        return ActivationResult(
            client_id=client_id,
            stage="ACTIVE",
            license_id=license_record.license_id,
            entitlement_status=EntitlementStatus.ACTIVE.value,
            activated_by=activated_by,
            contract_reference=contract_reference,
        )

    def deactivate(
        self,
        *,
        client_id: str,
        activated_by: str,
        contract_reference: str,
        target_status: EntitlementStatus = EntitlementStatus.LOCKED,
        revoke_license: bool = False,
    ) -> ActivationResult:
        self._require_attribution(activated_by, contract_reference)

        license_record = self.license_manager.load_license(client_id)
        if license_record is None:
            raise ValueError(f"Client '{client_id}' has no license on file.")

        self.entitlement_guard.set_status(client_id, target_status)

        if revoke_license:
            self.license_manager.revoke(client_id, reason=contract_reference)

        self.audit_logger.log(
            event_type="CONTRACT_DEACTIVATED",
            client_id=client_id,
            actor=activated_by,
            action="deactivate",
            outcome="SUCCESS",
            severity="CRITICAL",
            reason=f"Client moved to {target_status.value}"
            + (" and license revoked" if revoke_license else ""),
            metadata={
                "license_id": license_record.license_id,
                "contract_reference": contract_reference,
                "target_status": target_status.value,
                "license_revoked": revoke_license,
            },
        )

        return ActivationResult(
            client_id=client_id,
            stage=target_status.value,
            license_id=license_record.license_id,
            entitlement_status=target_status.value,
            activated_by=activated_by,
            contract_reference=contract_reference,
        )


def run_cli() -> None:
    parser = argparse.ArgumentParser(
        description="Agentic Zero - Contract Activation (human gate: lead -> licensed client)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_provision = sub.add_parser(
        "provision", help="Contract signed - create license + entitlement (READ_ONLY)"
    )
    p_provision.add_argument("--client-id", required=True)
    p_provision.add_argument("--product", required=True)
    p_provision.add_argument("--plan", required=True)
    p_provision.add_argument("--expires-at", default=None)
    p_provision.add_argument("--activated-by", required=True)
    p_provision.add_argument("--contract-reference", required=True)
    p_provision.add_argument("--no-monthly-subscription", action="store_true")
    p_provision.add_argument("--no-connectors", action="store_true")
    p_provision.add_argument("--no-swarm", action="store_true")

    p_golive = sub.add_parser("go-live", help="Deploy complete - flip to ACTIVE")
    p_golive.add_argument("--client-id", required=True)
    p_golive.add_argument("--activated-by", required=True)
    p_golive.add_argument("--contract-reference", required=True)

    p_deactivate = sub.add_parser("deactivate", help="Lock/decommission a client")
    p_deactivate.add_argument("--client-id", required=True)
    p_deactivate.add_argument("--activated-by", required=True)
    p_deactivate.add_argument("--contract-reference", required=True)
    p_deactivate.add_argument(
        "--target-status",
        choices=["LOCKED", "DECOMMISSIONED"],
        default="LOCKED",
    )
    p_deactivate.add_argument("--revoke-license", action="store_true")

    args = parser.parse_args()
    activation = ContractActivation()

    try:
        if args.command == "provision":
            result = activation.provision_from_contract(
                client_id=args.client_id,
                product=args.product,
                plan=args.plan,
                expires_at=args.expires_at,
                activated_by=args.activated_by,
                contract_reference=args.contract_reference,
                monthly_subscription_required=not args.no_monthly_subscription,
                connectors_enabled=not args.no_connectors,
                swarm_enabled=not args.no_swarm,
            )
        elif args.command == "go-live":
            result = activation.go_live(
                client_id=args.client_id,
                activated_by=args.activated_by,
                contract_reference=args.contract_reference,
            )
        elif args.command == "deactivate":
            result = activation.deactivate(
                client_id=args.client_id,
                activated_by=args.activated_by,
                contract_reference=args.contract_reference,
                target_status=EntitlementStatus(args.target_status),
                revoke_license=args.revoke_license,
            )
        else:
            raise ValueError(f"Unknown command: {args.command}")
    except ValueError as e:
        print(f"\nREJECTED: {e}\n")
        raise SystemExit(1)

    print("\nContract Activation")
    print("--------------------")
    print(json.dumps(asdict(result), indent=2))
    print("")


if __name__ == "__main__":
    run_cli()
