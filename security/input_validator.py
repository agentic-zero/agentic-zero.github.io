# security/input_validator.py

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger


@dataclass
class ValidationIssue:
    field: str
    issue_type: str
    severity: str
    message: str


@dataclass
class ValidationResult:
    valid: bool
    issues: list[ValidationIssue]
    sanitized_payload: dict[str, Any]


class InputValidator:
    """
    Input validation layer for Agentic Zero.

    Intended for:
    - Audit Zero payloads
    - Advanced Audit payloads
    - client package ingestion
    - runtime events
    - manual API payloads

    It validates and sanitizes user-controlled input before it reaches:
    - factory
    - runtime
    - The Machine
    - security gateway
    """

    FREE_EMAIL_DOMAINS = {
        "gmail.com",
        "googlemail.com",
        "hotmail.com",
        "hotmail.es",
        "outlook.com",
        "outlook.es",
        "live.com",
        "live.es",
        "yahoo.com",
        "yahoo.es",
        "icloud.com",
        "me.com",
        "mac.com",
        "proton.me",
        "protonmail.com",
        "aol.com",
        "gmx.com",
        "gmx.es",
        "mail.com",
        "zoho.com",
        "yandex.com",
    }

    DANGEROUS_PATTERNS = [
        r"<script\b",
        r"</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"eval\s*\(",
        r"document\.cookie",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"INSERT\s+INTO",
        r"UPDATE\s+\w+\s+SET",
        r"\.\./",
        r"\.\.\\",
    ]

    def __init__(self, audit_logger: Optional[AuditLogger] = None) -> None:
        self.audit_logger = audit_logger or AuditLogger()

    def validate_audit_payload(
        self,
        *,
        client_id: str,
        payload: dict[str, Any],
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []
        sanitized = self._sanitize_payload(payload)

        required_fields = [
            "contact_name",
            "contact_role",
            "company",
            "email",
            "phone_code",
            "phone_number",
        ]

        for field in required_fields:
            if not str(sanitized.get(field, "")).strip():
                issues.append(
                    ValidationIssue(
                        field=field,
                        issue_type="REQUIRED_FIELD_MISSING",
                        severity="ERROR",
                        message=f"Required field '{field}' is missing.",
                    )
                )

        email = str(sanitized.get("email", "")).strip().lower()

        if email:
            if not self.is_valid_email(email):
                issues.append(
                    ValidationIssue(
                        field="email",
                        issue_type="INVALID_EMAIL_FORMAT",
                        severity="ERROR",
                        message="Email format is invalid.",
                    )
                )
            elif not self.is_corporate_email(email):
                issues.append(
                    ValidationIssue(
                        field="email",
                        issue_type="NON_CORPORATE_EMAIL",
                        severity="ERROR",
                        message="Only corporate email addresses are accepted.",
                    )
                )

        self._detect_dangerous_content(
            payload=sanitized,
            issues=issues,
        )

        valid = not any(i.severity == "ERROR" for i in issues)

        self.audit_logger.log(
            event_type="INPUT_VALIDATION",
            client_id=client_id,
            actor="system",
            action="validate_audit_payload",
            outcome="VALID" if valid else "INVALID",
            severity="INFO" if valid else "WARNING",
            reason="Audit payload validation completed",
            metadata={
                "issue_count": len(issues),
                "issues": [asdict(i) for i in issues],
            },
        )

        return ValidationResult(
            valid=valid,
            issues=issues,
            sanitized_payload=sanitized,
        )

    def validate_runtime_event(
        self,
        *,
        client_id: str,
        event: dict[str, Any],
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []
        sanitized = self._sanitize_payload(event)

        required_fields = [
            "event_id",
            "event_type",
            "source",
            "timestamp",
        ]

        for field in required_fields:
            if not str(sanitized.get(field, "")).strip():
                issues.append(
                    ValidationIssue(
                        field=field,
                        issue_type="REQUIRED_FIELD_MISSING",
                        severity="ERROR",
                        message=f"Runtime event requires '{field}'.",
                    )
                )

        self._detect_dangerous_content(
            payload=sanitized,
            issues=issues,
        )

        valid = not any(i.severity == "ERROR" for i in issues)

        self.audit_logger.log(
            event_type="RUNTIME_EVENT_VALIDATION",
            client_id=client_id,
            actor="system",
            action="validate_runtime_event",
            outcome="VALID" if valid else "INVALID",
            severity="INFO" if valid else "WARNING",
            reason="Runtime event validation completed",
            metadata={
                "issue_count": len(issues),
                "issues": [asdict(i) for i in issues],
            },
        )

        return ValidationResult(
            valid=valid,
            issues=issues,
            sanitized_payload=sanitized,
        )

    def is_valid_email(self, email: str) -> bool:
        pattern = r"^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$"
        return re.match(pattern, email, re.IGNORECASE) is not None

    def is_corporate_email(self, email: str) -> bool:
        domain = email.split("@")[-1].lower().strip()

        if domain in self.FREE_EMAIL_DOMAINS:
            return False

        return True

    def _sanitize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        sanitized: dict[str, Any] = {}

        for key, value in payload.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_payload(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_string(v)
                    if isinstance(v, str)
                    else self._sanitize_payload(v)
                    if isinstance(v, dict)
                    else v
                    for v in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_string(self, value: str) -> str:
        return value.replace("\x00", "").replace("\r", " ").strip()

    def _detect_dangerous_content(
        self,
        *,
        payload: dict[str, Any],
        issues: list[ValidationIssue],
        parent_key: str = "",
    ) -> None:
        for key, value in payload.items():
            field = f"{parent_key}.{key}" if parent_key else key

            if isinstance(value, str):
                for pattern in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        issues.append(
                            ValidationIssue(
                                field=field,
                                issue_type="DANGEROUS_CONTENT",
                                severity="ERROR",
                                message=f"Dangerous content detected in '{field}'.",
                            )
                        )
            elif isinstance(value, dict):
                self._detect_dangerous_content(
                    payload=value,
                    issues=issues,
                    parent_key=field,
                )
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        self._detect_dangerous_content(
                            payload=item,
                            issues=issues,
                            parent_key=f"{field}[{index}]",
                        )
                    elif isinstance(item, str):
                        for pattern in self.DANGEROUS_PATTERNS:
                            if re.search(pattern, item, re.IGNORECASE):
                                issues.append(
                                    ValidationIssue(
                                        field=f"{field}[{index}]",
                                        issue_type="DANGEROUS_CONTENT",
                                        severity="ERROR",
                                        message=f"Dangerous content detected in '{field}[{index}]'.",
                                    )
                                )


def main() -> None:
    validator = InputValidator()

    good_payload = {
        "contact_name": "Elena Martin",
        "contact_role": "Supply Chain Director",
        "company": "DIS Solar Europe",
        "email": "elena.martin@dissolar.eu",
        "phone_code": "31",
        "phone_number": "612345678",
    }

    bad_payload = {
        "contact_name": "Test User",
        "contact_role": "Student",
        "company": "Fake",
        "email": "test@yahoo.es",
        "phone_code": "34",
        "phone_number": "600000000",
        "notes": "<script>alert('x')</script>",
    }

    print("")
    print("Input Validator")
    print("---------------")

    good_result = validator.validate_audit_payload(
        client_id="dis_solar",
        payload=good_payload,
    )

    bad_result = validator.validate_audit_payload(
        client_id="dis_solar",
        payload=bad_payload,
    )

    print("Good payload valid:", good_result.valid)
    print("Bad payload valid :", bad_result.valid)

    output = {
        "good": {
            "valid": good_result.valid,
            "issues": [asdict(i) for i in good_result.issues],
        },
        "bad": {
            "valid": bad_result.valid,
            "issues": [asdict(i) for i in bad_result.issues],
        },
    }

    out_path = Path("security/state/input_validator_test_result.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("Output:", out_path)
    print("")


if __name__ == "__main__":
    main()
