# security/pii_detector.py

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger


@dataclass
class PiiFinding:
    field: str
    pii_type: str
    severity: str
    sample: str
    message: str


@dataclass
class PiiDetectionResult:
    has_pii: bool
    findings: list[PiiFinding]
    redacted_payload: dict[str, Any]


class PiiDetector:
    """
    PII detector for Agentic Zero.

    Intended for:
    - Audit Zero
    - Advanced Audit
    - uploaded process descriptions
    - runtime events
    - logs
    - The Machine memory inputs

    This is not a legal substitute for GDPR compliance,
    but it helps detect and redact obvious personal data
    before it enters internal systems.
    """

    # Order matters: redaction mutates the string progressively, pattern by
    # pattern, in dict insertion order. PHONE's pattern is deliberately loose
    # (6-10 digits, optional prefix) so it can catch real phone numbers in
    # free text - but that same looseness means it will eat the digit
    # portion of a Spanish DNI/NIE, an IBAN or a credit card number if it
    # runs first, leaving a mislabeled MEDIUM-severity "PHONE" finding and a
    # partially-redacted leftover (e.g. a DNI's checksum letter surviving
    # alone as "[REDACTED_PHONE]Z"). Specific, high-severity patterns MUST
    # run before PHONE so they get first claim on their own digits.
    PATTERNS = {
        "EMAIL": re.compile(
            r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b",
            re.IGNORECASE,
        ),
        "SPANISH_DNI_NIE": re.compile(
            r"\b(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])\b",
            re.IGNORECASE,
        ),
        "IBAN": re.compile(
            r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
            re.IGNORECASE,
        ),
        "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        "PHONE": re.compile(
            r"(?<!\d)(?:\+?\d{1,3}[\s\-\.]?)?(?:\(?\d{2,4}\)?[\s\-\.]?)?\d{6,10}(?!\d)"
        ),
        "IP_ADDRESS": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    }

    HIGH_SEVERITY = {
        "IBAN",
        "CREDIT_CARD",
        "SPANISH_DNI_NIE",
    }

    def __init__(self, audit_logger: Optional[AuditLogger] = None) -> None:
        self.audit_logger = audit_logger or AuditLogger()

    def detect(
        self,
        *,
        client_id: str,
        payload: dict[str, Any],
        redact: bool = True,
    ) -> PiiDetectionResult:
        findings: list[PiiFinding] = []
        redacted_payload = self._scan_payload(
            payload=payload,
            findings=findings,
            redact=redact,
        )

        result = PiiDetectionResult(
            has_pii=bool(findings),
            findings=findings,
            redacted_payload=redacted_payload,
        )

        self.audit_logger.log(
            event_type="PII_DETECTION",
            client_id=client_id,
            actor="system",
            action="detect_pii",
            outcome="PII_FOUND" if findings else "NO_PII_FOUND",
            severity="WARNING" if findings else "INFO",
            reason="PII detection completed",
            metadata={
                "finding_count": len(findings),
                "findings": [asdict(f) for f in findings],
                "redacted": redact,
            },
        )

        return result

    def _scan_payload(
        self,
        *,
        payload: dict[str, Any],
        findings: list[PiiFinding],
        redact: bool,
        parent_key: str = "",
    ) -> dict[str, Any]:
        output: dict[str, Any] = {}

        for key, value in payload.items():
            field = f"{parent_key}.{key}" if parent_key else key

            if isinstance(value, str):
                output[field.split(".")[-1]] = self._scan_string(
                    field=field,
                    value=value,
                    findings=findings,
                    redact=redact,
                )
            elif isinstance(value, dict):
                output[field.split(".")[-1]] = self._scan_payload(
                    payload=value,
                    findings=findings,
                    redact=redact,
                    parent_key=field,
                )
            elif isinstance(value, list):
                output[field.split(".")[-1]] = [
                    self._scan_string(
                        field=f"{field}[{index}]",
                        value=item,
                        findings=findings,
                        redact=redact,
                    )
                    if isinstance(item, str)
                    else self._scan_payload(
                        payload=item,
                        findings=findings,
                        redact=redact,
                        parent_key=f"{field}[{index}]",
                    )
                    if isinstance(item, dict)
                    else item
                    for index, item in enumerate(value)
                ]
            else:
                output[field.split(".")[-1]] = value

        return output

    def _scan_string(
        self,
        *,
        field: str,
        value: str,
        findings: list[PiiFinding],
        redact: bool,
    ) -> str:
        result = value

        for pii_type, pattern in self.PATTERNS.items():
            matches = list(pattern.finditer(result))

            for match in matches:
                sample = match.group(0)
                severity = "HIGH" if pii_type in self.HIGH_SEVERITY else "MEDIUM"

                findings.append(
                    PiiFinding(
                        field=field,
                        pii_type=pii_type,
                        severity=severity,
                        sample=self._mask_sample(sample),
                        message=f"Potential {pii_type} detected in '{field}'.",
                    )
                )

            if redact:
                result = pattern.sub(f"[REDACTED_{pii_type}]", result)

        return result

    def _mask_sample(self, sample: str) -> str:
        if len(sample) <= 6:
            return "***"

        return sample[:3] + "***" + sample[-3:]


def main() -> None:
    detector = PiiDetector()

    payload = {
        "contact_name": "Elena Martin",
        "email": "elena.martin@dissolar.eu",
        "phone": "+31 612345678",
        "notes": (
            "Please contact elena.martin@dissolar.eu. "
            "Backup phone +31 612345678. "
            "Do not store bank account ES9121000418450200051332."
        ),
        "nested": {
            "ip": "192.168.1.20",
            "dni": "12345678Z",
        },
    }

    result = detector.detect(
        client_id="dis_solar",
        payload=payload,
        redact=True,
    )

    output_path = Path("security/state/pii_detector_test_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "has_pii": result.has_pii,
                "findings": [asdict(f) for f in result.findings],
                "redacted_payload": result.redacted_payload,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("")
    print("PII Detector")
    print("------------")
    print(f"PII found : {result.has_pii}")
    print(f"Findings  : {len(result.findings)}")
    print(f"Output    : {output_path}")
    print("")


if __name__ == "__main__":
    main()
