# security/secret_guard.py

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger


@dataclass
class SecretFinding:
    field: str
    secret_type: str
    severity: str
    sample: str
    message: str


@dataclass
class SecretScanResult:
    has_secrets: bool
    findings: list[SecretFinding]
    redacted_payload: dict[str, Any]


class SecretGuard:
    """
    Secret scanner and redactor for Agentic Zero.

    Intended for:
    - Audit Zero payloads
    - Advanced Audit payloads
    - uploaded configuration snippets
    - client packages
    - runtime events
    - logs
    - The Machine memory inputs

    Prevents accidental storage or leakage of:
    - API keys
    - tokens
    - passwords
    - private keys
    - connection strings
    - cloud credentials
    """

    # Order matters here too (see pii_detector.py for the same principle):
    # redaction mutates the string pattern by pattern, in dict insertion
    # order. PASSWORD_ASSIGNMENT's keyword list includes "passwd", which
    # would otherwise consume a SAP credential line (PASSWD=...) before
    # SAP_RFC_CREDENTIAL gets a chance, downgrading a SAP credential leak
    # to a generic, non-HIGH-severity finding. Specific patterns run first.
    SECRET_PATTERNS = {
        "OPENAI_API_KEY": re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
        "ANTHROPIC_API_KEY": re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b"),
        "AWS_ACCESS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "GOOGLE_API_KEY": re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}\b"),
        "GITHUB_TOKEN": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
        "JWT_TOKEN": re.compile(
            r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b"
        ),
        "PRIVATE_KEY": re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
            re.IGNORECASE,
        ),
        "CONNECTION_STRING": re.compile(
            r"\b(?:postgres|mysql|mssql|mongodb|redis)://[^\s'\"]+",
            re.IGNORECASE,
        ),
        "SAP_RFC_CREDENTIAL": re.compile(
            r"\b(?:ASHOST|SYSNR|CLIENT|USER|PASSWD)\s*=\s*[^\s;]+",
            re.IGNORECASE,
        ),
        "PASSWORD_ASSIGNMENT": re.compile(
            r"\b(password|passwd|pwd|secret|token|api_key|apikey|access_key)\s*[:=]\s*(['\"]?)[^'\"\s,;]{6,}\2",
            re.IGNORECASE,
        ),
    }

    HIGH_SEVERITY = {
        "PRIVATE_KEY",
        "AWS_ACCESS_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GITHUB_TOKEN",
        "GOOGLE_API_KEY",
        "JWT_TOKEN",
        "CONNECTION_STRING",
        "SAP_RFC_CREDENTIAL",
    }

    def __init__(self, audit_logger: Optional[AuditLogger] = None) -> None:
        self.audit_logger = audit_logger or AuditLogger()

    def scan(
        self,
        *,
        client_id: str,
        payload: dict[str, Any],
        redact: bool = True,
    ) -> SecretScanResult:
        findings: list[SecretFinding] = []

        redacted_payload = self._scan_payload(
            payload=payload,
            findings=findings,
            redact=redact,
        )

        result = SecretScanResult(
            has_secrets=bool(findings),
            findings=findings,
            redacted_payload=redacted_payload,
        )

        self.audit_logger.log(
            event_type="SECRET_SCAN",
            client_id=client_id,
            actor="system",
            action="scan_for_secrets",
            outcome="SECRETS_FOUND" if findings else "NO_SECRETS_FOUND",
            severity="CRITICAL" if findings else "INFO",
            reason="Secret scan completed",
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
        findings: list[SecretFinding],
        redact: bool,
        parent_key: str = "",
    ) -> dict[str, Any]:
        output: dict[str, Any] = {}

        for key, value in payload.items():
            field = f"{parent_key}.{key}" if parent_key else key

            if isinstance(value, str):
                output[key] = self._scan_string(
                    field=field,
                    value=value,
                    findings=findings,
                    redact=redact,
                )
            elif isinstance(value, dict):
                output[key] = self._scan_payload(
                    payload=value,
                    findings=findings,
                    redact=redact,
                    parent_key=field,
                )
            elif isinstance(value, list):
                output[key] = [
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
                output[key] = value

        return output

    def _scan_string(
        self,
        *,
        field: str,
        value: str,
        findings: list[SecretFinding],
        redact: bool,
    ) -> str:
        result = value

        for secret_type, pattern in self.SECRET_PATTERNS.items():
            matches = list(pattern.finditer(result))

            for match in matches:
                sample = match.group(0)
                severity = "HIGH" if secret_type in self.HIGH_SEVERITY else "MEDIUM"

                findings.append(
                    SecretFinding(
                        field=field,
                        secret_type=secret_type,
                        severity=severity,
                        sample=self._mask_secret(sample),
                        message=f"Potential {secret_type} detected in '{field}'.",
                    )
                )

            if redact:
                result = pattern.sub(f"[REDACTED_{secret_type}]", result)

        return result

    def _mask_secret(self, value: str) -> str:
        clean = value.replace("\n", "")

        if len(clean) <= 10:
            return "***"

        return clean[:4] + "***" + clean[-4:]


def main() -> None:
    guard = SecretGuard()

    payload = {
        "client_id": "dis_solar",
        "notes": "Use token sk-test1234567890abcdefghijklmnopqrstuvwxyz for testing only.",
        "config": {
            "connection": "postgres://user:password@localhost:5432/db",
            "sap": "ASHOST=sap.local SYSNR=00 CLIENT=100 USER=BOT PASSWD=supersecret",
            "env": "api_key='abcd1234567890secret'",
        },
        "safe_text": "This is normal operational context.",
    }

    result = guard.scan(
        client_id="dis_solar",
        payload=payload,
        redact=True,
    )

    output_path = Path("security/state/secret_guard_test_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "has_secrets": result.has_secrets,
                "findings": [asdict(f) for f in result.findings],
                "redacted_payload": result.redacted_payload,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("")
    print("Secret Guard")
    print("------------")
    print(f"Secrets found : {result.has_secrets}")
    print(f"Findings      : {len(result.findings)}")
    print(f"Output        : {output_path}")
    print("")


if __name__ == "__main__":
    main()
