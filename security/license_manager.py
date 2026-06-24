# security/license_manager.py

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger


class LicenseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


@dataclass
class LicenseRecord:
    license_id: str
    client_id: str
    product: str
    plan: str
    status: LicenseStatus
    issued_at: str
    expires_at: Optional[str]
    fingerprint: str
    monthly_subscription_required: bool
    metadata: dict[str, Any]


@dataclass
class LicenseValidation:
    client_id: str
    license_id: Optional[str]
    valid: bool
    status: str
    reason: str
    product: Optional[str]
    plan: Optional[str]
    checked_at: str


class LicenseManager:
    """
    License manager for Agentic Zero.

    Responsibilities:
    - create client licenses
    - validate licenses
    - suspend licenses
    - revoke licenses
    - detect expired licenses
    - generate stable license fingerprints

    This does not replace SubscriptionGate.
    SubscriptionGate decides execution access.
    LicenseManager validates whether a license exists and is usable.
    """

    def __init__(
        self,
        license_root: str | Path = "security/state/licenses",
        audit_logger: Optional[AuditLogger] = None,
    ) -> None:
        self.license_root = Path(license_root)
        self.license_root.mkdir(parents=True, exist_ok=True)
        self.audit_logger = audit_logger or AuditLogger()

    def create_license(
        self,
        *,
        client_id: str,
        product: str,
        plan: str,
        expires_at: Optional[str],
        monthly_subscription_required: bool = True,
        metadata: Optional[dict[str, Any]] = None,
    ) -> LicenseRecord:
        license_id = f"az-{uuid.uuid4()}"
        issued_at = datetime.now(timezone.utc).isoformat()

        fingerprint = self._fingerprint(
            client_id=client_id,
            license_id=license_id,
            product=product,
            plan=plan,
            issued_at=issued_at,
        )

        record = LicenseRecord(
            license_id=license_id,
            client_id=client_id,
            product=product,
            plan=plan,
            status=LicenseStatus.ACTIVE,
            issued_at=issued_at,
            expires_at=expires_at,
            fingerprint=fingerprint,
            monthly_subscription_required=monthly_subscription_required,
            metadata=metadata or {},
        )

        self._write_license(record)

        self.audit_logger.log(
            event_type="LICENSE_CREATED",
            client_id=client_id,
            actor="system",
            action="create_license",
            outcome="SUCCESS",
            severity="INFO",
            reason="License created",
            metadata={
                "license_id": license_id,
                "product": product,
                "plan": plan,
                "expires_at": expires_at,
            },
        )

        return record

    def validate(self, client_id: str) -> LicenseValidation:
        record = self.load_license(client_id)

        if record is None:
            validation = self._validation(
                client_id=client_id,
                license_id=None,
                valid=False,
                status="MISSING",
                reason="No license found",
                product=None,
                plan=None,
            )
            self._log_validation(validation)
            return validation

        if record.status == LicenseStatus.REVOKED:
            validation = self._validation(
                client_id=client_id,
                license_id=record.license_id,
                valid=False,
                status=record.status.value,
                reason="License revoked",
                product=record.product,
                plan=record.plan,
            )
            self._log_validation(validation)
            return validation

        if record.status == LicenseStatus.SUSPENDED:
            validation = self._validation(
                client_id=client_id,
                license_id=record.license_id,
                valid=False,
                status=record.status.value,
                reason="License suspended",
                product=record.product,
                plan=record.plan,
            )
            self._log_validation(validation)
            return validation

        if record.expires_at and self._is_expired(record.expires_at):
            validation = self._validation(
                client_id=client_id,
                license_id=record.license_id,
                valid=False,
                status=LicenseStatus.EXPIRED.value,
                reason="License expired",
                product=record.product,
                plan=record.plan,
            )
            self._log_validation(validation)
            return validation

        expected_fingerprint = self._fingerprint(
            client_id=record.client_id,
            license_id=record.license_id,
            product=record.product,
            plan=record.plan,
            issued_at=record.issued_at,
        )

        if expected_fingerprint != record.fingerprint:
            validation = self._validation(
                client_id=client_id,
                license_id=record.license_id,
                valid=False,
                status="TAMPERED",
                reason="License fingerprint mismatch",
                product=record.product,
                plan=record.plan,
            )
            self._log_validation(validation)
            return validation

        validation = self._validation(
            client_id=client_id,
            license_id=record.license_id,
            valid=True,
            status=record.status.value,
            reason="License valid",
            product=record.product,
            plan=record.plan,
        )
        self._log_validation(validation)
        return validation

    def load_license(self, client_id: str) -> Optional[LicenseRecord]:
        path = self._license_path(client_id)

        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            return LicenseRecord(
                license_id=data["license_id"],
                client_id=data["client_id"],
                product=data["product"],
                plan=data["plan"],
                status=LicenseStatus(data["status"]),
                issued_at=data["issued_at"],
                expires_at=data.get("expires_at"),
                fingerprint=data["fingerprint"],
                monthly_subscription_required=bool(
                    data.get("monthly_subscription_required", True)
                ),
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError, ValueError):
            # Corrupted, partially written, hand-edited or tampered license
            # file. This is an access-control layer - fail CLOSED (treat as
            # "no license found") rather than raising, so validate() denies
            # cleanly instead of crashing the caller.
            self.audit_logger.log(
                event_type="LICENSE_FILE_CORRUPTED",
                client_id=client_id,
                actor="system",
                action="load_license",
                outcome="FAIL_CLOSED",
                severity="CRITICAL",
                reason="License file unreadable, malformed or tampered - treated as missing",
                metadata={"license_path": str(path)},
            )
            return None

    def suspend(
        self, client_id: str, reason: str = "Manual suspension"
    ) -> LicenseRecord:
        record = self._require_license(client_id)
        record.status = LicenseStatus.SUSPENDED
        self._write_license(record)

        self.audit_logger.log(
            event_type="LICENSE_SUSPENDED",
            client_id=client_id,
            actor="system",
            action="suspend_license",
            outcome="SUCCESS",
            severity="WARNING",
            reason=reason,
            metadata={"license_id": record.license_id},
        )

        return record

    def revoke(
        self, client_id: str, reason: str = "Manual revocation"
    ) -> LicenseRecord:
        record = self._require_license(client_id)
        record.status = LicenseStatus.REVOKED
        self._write_license(record)

        self.audit_logger.log(
            event_type="LICENSE_REVOKED",
            client_id=client_id,
            actor="system",
            action="revoke_license",
            outcome="SUCCESS",
            severity="CRITICAL",
            reason=reason,
            metadata={"license_id": record.license_id},
        )

        return record

    def _require_license(self, client_id: str) -> LicenseRecord:
        record = self.load_license(client_id)

        if record is None:
            raise FileNotFoundError(f"No license found for client '{client_id}'")

        return record

    def _write_license(self, record: LicenseRecord) -> None:
        path = self._license_path(record.client_id)
        data = asdict(record)
        data["status"] = record.status.value
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _license_path(self, client_id: str) -> Path:
        return self.license_root / f"{client_id}.json"

    def _fingerprint(
        self,
        *,
        client_id: str,
        license_id: str,
        product: str,
        plan: str,
        issued_at: str,
    ) -> str:
        raw = "|".join([client_id, license_id, product, plan, issued_at])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _is_expired(self, expires_at: str) -> bool:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) > expiry

    def _validation(
        self,
        *,
        client_id: str,
        license_id: Optional[str],
        valid: bool,
        status: str,
        reason: str,
        product: Optional[str],
        plan: Optional[str],
    ) -> LicenseValidation:
        return LicenseValidation(
            client_id=client_id,
            license_id=license_id,
            valid=valid,
            status=status,
            reason=reason,
            product=product,
            plan=plan,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )

    def _log_validation(self, validation: LicenseValidation) -> None:
        self.audit_logger.log(
            event_type="LICENSE_VALIDATION",
            client_id=validation.client_id,
            actor="system",
            action="validate_license",
            outcome="VALID" if validation.valid else "INVALID",
            severity="INFO" if validation.valid else "WARNING",
            reason=validation.reason,
            metadata={
                "license_id": validation.license_id,
                "status": validation.status,
                "product": validation.product,
                "plan": validation.plan,
            },
        )


def main() -> None:
    manager = LicenseManager()

    record = manager.create_license(
        client_id="dis_solar",
        product="AGENTIC_ONE",
        plan="ENTERPRISE",
        expires_at="2099-12-31T23:59:59Z",
        metadata={
            "environment": "test",
            "owner": "Agentic Zero",
        },
    )

    validation = manager.validate("dis_solar")

    print("")
    print("License Manager")
    print("---------------")
    print("Created license:")
    print(json.dumps(asdict(record), indent=2))
    print("")
    print("Validation:")
    print(json.dumps(asdict(validation), indent=2))
    print("")


if __name__ == "__main__":
    main()
