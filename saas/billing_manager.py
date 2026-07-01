# saas/billing_manager.py

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class BillingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAYMENT_DUE = "PAYMENT_DUE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"


@dataclass
class BillingRecord:
    billing_id: str
    client_id: str
    plan: str
    product: str
    monthly_amount: float
    currency: str
    status: BillingStatus
    current_period_start: str
    current_period_end: str
    next_invoice_at: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]


class BillingManager:
    """
    SaaS billing state manager for Agentic Zero.

    This module does NOT call Shield or The Machine.

    Responsibilities:
    - create billing record
    - read billing record
    - mark payment due
    - mark past due
    - cancel billing
    - suspend billing
    - map billing status to entitlement status
    """

    PLAN_PRICES = {
        "ESSENTIAL": 490.0,
        "STANDARD": 990.0,
        "ENTERPRISE": 1800.0,
    }

    def __init__(self, billing_root: str | Path = "saas/state/billing") -> None:
        self.billing_root = Path(billing_root)
        self.billing_root.mkdir(parents=True, exist_ok=True)

    def create_billing(
        self,
        *,
        client_id: str,
        product: str,
        plan: str,
        currency: str = "EUR",
        metadata: Optional[dict[str, Any]] = None,
    ) -> BillingRecord:
        plan_key = plan.upper()

        if plan_key not in self.PLAN_PRICES:
            # A typo'd plan name ("ENTERPRICE") used to silently bill the
            # client EUR 0.00/month with no warning - a real, silent
            # revenue-loss bug, not a crash. Reject explicitly instead.
            raise ValueError(
                f"Unknown plan '{plan}'. Valid plans: {sorted(self.PLAN_PRICES)}"
            )

        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=30)

        record = BillingRecord(
            billing_id=f"billing-{uuid.uuid4()}",
            client_id=client_id,
            plan=plan_key,
            product=product,
            monthly_amount=self.PLAN_PRICES.get(plan_key, 0.0),
            currency=currency,
            status=BillingStatus.ACTIVE,
            current_period_start=now.isoformat(),
            current_period_end=period_end.isoformat(),
            next_invoice_at=period_end.isoformat(),
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            metadata=metadata or {},
        )

        self._write(record)
        return record

    def get_billing(self, client_id: str) -> Optional[BillingRecord]:
        path = self._path(client_id)

        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            try:
                status = BillingStatus(data["status"])
            except ValueError:
                # Corrupted/hand-edited/partially-written status value.
                # Fail CLOSED to the most restrictive billing state rather
                # than crashing the caller - a corrupted billing record
                # must never silently look healthier than it is, and must
                # never take down the customer portal or monitoring views
                # that depend on reading this record.
                status = BillingStatus.SUSPENDED

            return BillingRecord(
                billing_id=data["billing_id"],
                client_id=data["client_id"],
                plan=data["plan"],
                product=data["product"],
                monthly_amount=float(data["monthly_amount"]),
                currency=data["currency"],
                status=status,
                current_period_start=data["current_period_start"],
                current_period_end=data["current_period_end"],
                next_invoice_at=data["next_invoice_at"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError) as exc:
            # Malformed JSON or missing required field - same fail-closed
            # principle as above, just a different failure mode upstream
            # of enum reconstruction.
            return BillingRecord(
                billing_id="UNKNOWN",
                client_id=client_id,
                plan="UNKNOWN",
                product="UNKNOWN",
                monthly_amount=0.0,
                currency="N/A",
                status=BillingStatus.SUSPENDED,
                current_period_start="",
                current_period_end="",
                next_invoice_at="",
                created_at="",
                updated_at="",
                metadata={"corrupted": True, "error": str(exc)},
            )

    def mark_payment_due(
        self, client_id: str, reason: str = "Invoice generated"
    ) -> BillingRecord:
        return self._update_status(
            client_id=client_id,
            status=BillingStatus.PAYMENT_DUE,
            reason=reason,
        )

    def mark_past_due(
        self, client_id: str, reason: str = "Payment overdue"
    ) -> BillingRecord:
        return self._update_status(
            client_id=client_id,
            status=BillingStatus.PAST_DUE,
            reason=reason,
        )

    def cancel(
        self, client_id: str, reason: str = "Subscription cancelled"
    ) -> BillingRecord:
        return self._update_status(
            client_id=client_id,
            status=BillingStatus.CANCELLED,
            reason=reason,
        )

    def suspend(
        self, client_id: str, reason: str = "Billing suspended"
    ) -> BillingRecord:
        return self._update_status(
            client_id=client_id,
            status=BillingStatus.SUSPENDED,
            reason=reason,
        )

    def map_to_entitlement_status(self, client_id: str) -> str:
        record = self.get_billing(client_id)

        if record is None:
            return "LOCKED"

        if record.status == BillingStatus.ACTIVE:
            return "ACTIVE"

        if record.status == BillingStatus.PAYMENT_DUE:
            return "GRACE_PERIOD"

        if record.status == BillingStatus.PAST_DUE:
            return "READ_ONLY"

        if record.status in {BillingStatus.CANCELLED, BillingStatus.SUSPENDED}:
            return "LOCKED"

        return "LOCKED"

    def list_billing_records(self) -> list[BillingRecord]:
        records: list[BillingRecord] = []

        for file in sorted(self.billing_root.glob("*.json")):
            record = self.get_billing(file.stem)
            if record:
                records.append(record)

        return records

    def _update_status(
        self,
        *,
        client_id: str,
        status: BillingStatus,
        reason: str,
    ) -> BillingRecord:
        record = self._require(client_id)
        record.status = status
        record.updated_at = datetime.now(timezone.utc).isoformat()
        record.metadata["last_status_reason"] = reason

        self._write(record)
        return record

    def _require(self, client_id: str) -> BillingRecord:
        record = self.get_billing(client_id)

        if record is None:
            raise FileNotFoundError(
                f"Billing record not found for client_id='{client_id}'"
            )

        return record

    def _write(self, record: BillingRecord) -> None:
        data = asdict(record)
        data["status"] = record.status.value

        self._path(record.client_id).write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def _path(self, client_id: str) -> Path:
        return self.billing_root / f"{client_id}.json"


def main() -> None:
    manager = BillingManager()

    if manager.get_billing("dis_solar") is None:
        record = manager.create_billing(
            client_id="dis_solar",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            metadata={
                "source": "saas_billing_test",
            },
        )
    else:
        record = manager.get_billing("dis_solar")

    entitlement_status = manager.map_to_entitlement_status("dis_solar")

    print("")
    print("Billing Manager")
    print("---------------")
    print(json.dumps(asdict(record), indent=2))
    print("")
    print(f"Mapped entitlement status: {entitlement_status}")
    print("")


if __name__ == "__main__":
    main()
