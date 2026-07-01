# saas/governance_report.py

"""
AGENTIC ZERO - SAAS PLATFORM
Governance Report v1.0

Role:
  token_governance.py (M11) tracks spend per client. billing_manager.py
  tracks what each client pays. Until now, nothing crossed the two -
  M11 existed but nobody could see "is client X's token spend
  proportionate to their plan, or are we quietly losing money on them."

  Read-only, same principle as security/security_dashboard.py: never
  mutates anything, only reports on what billing_manager.py and
  token_governance.py already recorded.

Output:
  Fleet-wide view: every billed client, their plan, their token budget
  status, and a flagged list of clients worth a human looking at
  (over budget without overage billing, or burning a disproportionate
  share of their plan's allowance relative to what they pay).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from saas.billing_manager import BillingManager
from saas.token_governance import TokenGovernance, PLAN_TOKEN_ALLOWANCES, GovernanceDecision


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ClientGovernanceSummary:
    client_id: str
    plan: str
    monthly_amount: float
    billing_status: str
    tokens_used_this_month: int
    monthly_token_allowance: int
    percent_used: float
    budget_status: str
    governance_decision: str
    governance_reason: str
    cost_per_token_allowance_ratio: Optional[float]  # monthly_amount / allowance, for cross-plan comparison


@dataclass
class FleetGovernanceReport:
    generated_at: str
    total_clients: int
    clients_over_budget: int
    clients_approaching_limit: int
    clients_needing_review: list[str]  # ESCALATE decisions specifically
    clients: list[ClientGovernanceSummary]


class GovernanceReportBuilder:
    def __init__(
        self,
        billing_manager: Optional[BillingManager] = None,
        token_governance: Optional[TokenGovernance] = None,
    ) -> None:
        self.billing_manager = billing_manager or BillingManager()
        self.token_governance = token_governance or TokenGovernance()

    def client_summary(self, client_id: str) -> Optional[ClientGovernanceSummary]:
        billing = self.billing_manager.get_billing(client_id)
        if billing is None:
            return None

        plan = billing.plan
        budget = self.token_governance.check_budget(client_id, plan)
        governance = self.token_governance.authorize_call(client_id, plan)

        ratio = (
            round(billing.monthly_amount / budget.monthly_allowance, 6)
            if budget.monthly_allowance else None
        )

        return ClientGovernanceSummary(
            client_id=client_id,
            plan=plan,
            monthly_amount=billing.monthly_amount,
            billing_status=billing.status.value,
            tokens_used_this_month=budget.tokens_used_this_month,
            monthly_token_allowance=budget.monthly_allowance,
            percent_used=budget.percent_used,
            budget_status=budget.status.value,
            governance_decision=governance.decision.value,
            governance_reason=governance.reason,
            cost_per_token_allowance_ratio=ratio,
        )

    def fleet_report(self) -> FleetGovernanceReport:
        summaries: list[ClientGovernanceSummary] = []

        for billing_record in self.billing_manager.list_billing_records():
            summary = self.client_summary(billing_record.client_id)
            if summary:
                summaries.append(summary)

        over_budget = [s for s in summaries if s.budget_status == "OVER_BUDGET"]
        approaching = [s for s in summaries if s.budget_status == "APPROACHING_LIMIT"]
        needing_review = [
            s.client_id for s in summaries
            if s.governance_decision == GovernanceDecision.ESCALATE.value
        ]

        return FleetGovernanceReport(
            generated_at=now(),
            total_clients=len(summaries),
            clients_over_budget=len(over_budget),
            clients_approaching_limit=len(approaching),
            clients_needing_review=needing_review,
            clients=summaries,
        )


def print_report(report: FleetGovernanceReport) -> None:
    print("\n" + "=" * 64)
    print("AGENTIC ZERO - GOVERNANCE REPORT (billing x token spend)")
    print("=" * 64)
    print(f"Generated at:           {report.generated_at}")
    print(f"Total billed clients:   {report.total_clients}")
    print(f"Over budget:            {report.clients_over_budget}")
    print(f"Approaching limit:      {report.clients_approaching_limit}")

    if report.clients_needing_review:
        print(f"\nNeeds human review ({len(report.clients_needing_review)}):")
        for client_id in report.clients_needing_review:
            print(f"  - {client_id}")

    print("\nPer client:")
    for s in report.clients:
        marker = {"WITHIN_BUDGET": "OK", "APPROACHING_LIMIT": "!!", "OVER_BUDGET": "XX"}.get(s.budget_status, "??")
        print(
            f"  [{marker}] {s.client_id:25s} plan={s.plan:10s} "
            f"tokens={s.tokens_used_this_month}/{s.monthly_token_allowance} "
            f"({s.percent_used}%)  decision={s.governance_decision}"
        )


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Governance Report")
    parser.add_argument("--client-id", default="", help="Report for one client only")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    builder = GovernanceReportBuilder()

    if args.client_id:
        summary = builder.client_summary(args.client_id)
        if summary is None:
            print(f"\nNo billing record found for client_id='{args.client_id}'.")
            raise SystemExit(1)

        if args.format == "json":
            print(json.dumps(asdict(summary), indent=2, ensure_ascii=False))
        else:
            print(f"\nClient: {summary.client_id}")
            print(f"  Plan:             {summary.plan} (€{summary.monthly_amount}/mo)")
            print(f"  Tokens used:      {summary.tokens_used_this_month}/{summary.monthly_token_allowance} ({summary.percent_used}%)")
            print(f"  Budget status:    {summary.budget_status}")
            print(f"  Decision:         {summary.governance_decision} - {summary.governance_reason}")

        if args.output:
            Path(args.output).write_text(json.dumps(asdict(summary), indent=2, ensure_ascii=False), encoding="utf-8")
        return

    report = builder.fleet_report()

    if args.format == "json":
        print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    else:
        print_report(report)

    if args.output:
        Path(args.output).write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    run_cli()
