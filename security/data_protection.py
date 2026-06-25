# security/data_protection.py

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger
from security.input_validator import InputValidator, ValidationResult
from security.pii_detector import PiiDetectionResult, PiiDetector
from security.secret_guard import SecretGuard, SecretScanResult


@dataclass
class DataProtectionResult:
    client_id: str
    valid: bool
    blocked: bool
    reason: str
    validation: dict[str, Any]
    pii_detection: dict[str, Any]
    secret_scan: dict[str, Any]
    protected_payload: dict[str, Any]


class DataProtection:
    """
    Unified data protection layer for Agentic Zero.

    This should be called before user/client data enters:

    - package generation
    - runtime
    - The Machine
    - security gateway
    - memory
    - audit trails
    - client-specific state

    It combines:
    - input validation
    - PII detection/redaction
    - secret detection/redaction
    - audit logging
    """

    def __init__(
        self,
        *,
        audit_logger: Optional[AuditLogger] = None,
        input_validator: Optional[InputValidator] = None,
        pii_detector: Optional[PiiDetector] = None,
        secret_guard: Optional[SecretGuard] = None,
    ) -> None:
        self.audit_logger = audit_logger or AuditLogger()
        self.input_validator = input_validator or InputValidator(
            audit_logger=self.audit_logger
        )
        self.pii_detector = pii_detector or PiiDetector(audit_logger=self.audit_logger)
        self.secret_guard = secret_guard or SecretGuard(audit_logger=self.audit_logger)

    def protect_audit_payload(
        self,
        *,
        client_id: str,
        payload: dict[str, Any],
    ) -> DataProtectionResult:
        validation = self.input_validator.validate_audit_payload(
            client_id=client_id,
            payload=payload,
        )

        if not validation.valid:
            return self._blocked(
                client_id=client_id,
                reason="Input validation failed",
                validation=validation,
                pii_detection=None,
                secret_scan=None,
                protected_payload=validation.sanitized_payload,
            )

        pii_result = self.pii_detector.detect(
            client_id=client_id,
            payload=validation.sanitized_payload,
            redact=True,
        )

        secret_result = self.secret_guard.scan(
            client_id=client_id,
            payload=pii_result.redacted_payload,
            redact=True,
        )

        blocked = secret_result.has_secrets

        if blocked:
            return self._blocked(
                client_id=client_id,
                reason="Secret material detected",
                validation=validation,
                pii_detection=pii_result,
                secret_scan=secret_result,
                protected_payload=secret_result.redacted_payload,
            )

        return self._allowed(
            client_id=client_id,
            reason="Payload protected successfully",
            validation=validation,
            pii_detection=pii_result,
            secret_scan=secret_result,
            protected_payload=secret_result.redacted_payload,
        )

    def protect_runtime_event(
        self,
        *,
        client_id: str,
        event: dict[str, Any],
    ) -> DataProtectionResult:
        validation = self.input_validator.validate_runtime_event(
            client_id=client_id,
            event=event,
        )

        if not validation.valid:
            return self._blocked(
                client_id=client_id,
                reason="Runtime event validation failed",
                validation=validation,
                pii_detection=None,
                secret_scan=None,
                protected_payload=validation.sanitized_payload,
            )

        pii_result = self.pii_detector.detect(
            client_id=client_id,
            payload=validation.sanitized_payload,
            redact=True,
        )

        secret_result = self.secret_guard.scan(
            client_id=client_id,
            payload=pii_result.redacted_payload,
            redact=True,
        )

        blocked = secret_result.has_secrets

        if blocked:
            return self._blocked(
                client_id=client_id,
                reason="Secret material detected in runtime event",
                validation=validation,
                pii_detection=pii_result,
                secret_scan=secret_result,
                protected_payload=secret_result.redacted_payload,
            )

        return self._allowed(
            client_id=client_id,
            reason="Runtime event protected successfully",
            validation=validation,
            pii_detection=pii_result,
            secret_scan=secret_result,
            protected_payload=secret_result.redacted_payload,
        )

    def _allowed(
        self,
        *,
        client_id: str,
        reason: str,
        validation: ValidationResult,
        pii_detection: Optional[PiiDetectionResult],
        secret_scan: Optional[SecretScanResult],
        protected_payload: dict[str, Any],
    ) -> DataProtectionResult:
        result = DataProtectionResult(
            client_id=client_id,
            valid=True,
            blocked=False,
            reason=reason,
            validation=self._validation_dict(validation),
            pii_detection=self._pii_dict(pii_detection),
            secret_scan=self._secret_dict(secret_scan),
            protected_payload=protected_payload,
        )

        self.audit_logger.log(
            event_type="DATA_PROTECTION_ALLOWED",
            client_id=client_id,
            actor="system",
            action="protect_payload",
            outcome="ALLOW",
            severity="INFO",
            reason=reason,
            metadata={
                "pii_found": bool(pii_detection.has_pii if pii_detection else False),
                "secrets_found": bool(
                    secret_scan.has_secrets if secret_scan else False
                ),
            },
        )

        return result

    def _blocked(
        self,
        *,
        client_id: str,
        reason: str,
        validation: ValidationResult,
        pii_detection: Optional[PiiDetectionResult],
        secret_scan: Optional[SecretScanResult],
        protected_payload: dict[str, Any],
    ) -> DataProtectionResult:
        result = DataProtectionResult(
            client_id=client_id,
            valid=False,
            blocked=True,
            reason=reason,
            validation=self._validation_dict(validation),
            pii_detection=self._pii_dict(pii_detection),
            secret_scan=self._secret_dict(secret_scan),
            protected_payload=protected_payload,
        )

        self.audit_logger.log(
            event_type="DATA_PROTECTION_BLOCKED",
            client_id=client_id,
            actor="system",
            action="protect_payload",
            outcome="BLOCK",
            severity="WARNING",
            reason=reason,
            metadata={
                "validation_valid": validation.valid,
                "pii_found": bool(pii_detection.has_pii if pii_detection else False),
                "secrets_found": bool(
                    secret_scan.has_secrets if secret_scan else False
                ),
            },
        )

        return result

    def _validation_dict(self, validation: ValidationResult) -> dict[str, Any]:
        return {
            "valid": validation.valid,
            "issues": [asdict(i) for i in validation.issues],
        }

    def _pii_dict(
        self,
        pii_detection: Optional[PiiDetectionResult],
    ) -> dict[str, Any]:
        if pii_detection is None:
            return {
                "has_pii": False,
                "findings": [],
            }

        return {
            "has_pii": pii_detection.has_pii,
            "findings": [asdict(f) for f in pii_detection.findings],
        }

    def _secret_dict(
        self,
        secret_scan: Optional[SecretScanResult],
    ) -> dict[str, Any]:
        if secret_scan is None:
            return {
                "has_secrets": False,
                "findings": [],
            }

        return {
            "has_secrets": secret_scan.has_secrets,
            "findings": [asdict(f) for f in secret_scan.findings],
        }


def main() -> None:
    protector = DataProtection()

    clean_payload = {
        "contact_name": "Elena Martin",
        "contact_role": "Supply Chain Director",
        "company": "DIS Solar Europe",
        "email": "elena.martin@dissolar.eu",
        "phone_code": "31",
        "phone_number": "612345678",
        "context": "Solar distribution process with SAP and Kinaxis.",
    }

    blocked_payload = {
        "contact_name": "Test User",
        "contact_role": "Consultant",
        "company": "Test Co",
        "email": "test@yahoo.es",
        "phone_code": "34",
        "phone_number": "600000000",
        "context": "Use token sk-test1234567890abcdefghijklmnopqrstuvwxyz",
    }

    clean_result = protector.protect_audit_payload(
        client_id="dis_solar",
        payload=clean_payload,
    )

    blocked_result = protector.protect_audit_payload(
        client_id="dis_solar",
        payload=blocked_payload,
    )

    output = {
        "clean_payload": asdict(clean_result),
        "blocked_payload": asdict(blocked_result),
    }

    output_path = Path("security/state/data_protection_test_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("")
    print("Data Protection")
    print("---------------")
    print(f"Clean payload blocked   : {clean_result.blocked}")
    print(f"Blocked payload blocked : {blocked_result.blocked}")
    print(f"Output                  : {output_path}")
    print("")


if __name__ == "__main__":
    main()
