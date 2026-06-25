# security/security_regression_suite.py

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SuiteCase:
    name: str
    module: str
    args: list[str]
    passed: bool
    returncode: int
    stdout_tail: str
    stderr_tail: str


@dataclass
class SuiteReport:
    run_at: str
    total: int
    passed: int
    failed: int
    cases: list[dict]


# Each entry is run as `python -m security.<module> <args>`, exactly as a
# person would run it by hand - this is deliberate: the suite tests the
# real CLI entrypoints, not internal functions, so it catches the same
# class of bug a manual run would (argparse changes, import errors,
# missing files) and not just logic bugs reachable only by importing the
# module directly.
CASES: list[tuple[str, str, list[str]]] = [
    ("Security Smoke Test (License/Entitlement/Subscription/Gateway/Policy)", "security_smoke_test", []),
    ("Input Validator", "input_validator", []),
    ("PII Detector", "pii_detector", []),
    ("Secret Guard", "secret_guard", []),
    ("Data Protection (unified gateway)", "data_protection", []),
    ("Runtime Entrypoint (kernel)", "runtime_entrypoint", []),
]

TAMPER_TEST_CLIENT = "_regression_suite_tamper_check"


def _tail(text: str, lines: int = 6) -> str:
    parts = text.strip().splitlines()
    return "\n".join(parts[-lines:]) if parts else ""


def run_case(name: str, module: str, args: list[str]) -> SuiteCase:
    result = subprocess.run(
        [sys.executable, "-m", f"security.{module}", *args],
        capture_output=True,
        text=True,
    )
    return SuiteCase(
        name=name,
        module=module,
        args=args,
        passed=result.returncode == 0,
        returncode=result.returncode,
        stdout_tail=_tail(result.stdout),
        stderr_tail=_tail(result.stderr),
    )


def run_tamper_detection_case() -> SuiteCase:
    """tamper_detection.py has no standalone self-test like the others -
    it needs a real client with files to snapshot/verify against. The
    regression suite provisions a disposable client, takes a clean
    snapshot, verifies it comes back clean, and treats that round-trip
    as the pass/fail signal for this module.
    """
    subprocess.run(
        [
            sys.executable, "-m", "security.contract_activation", "provision",
            "--client-id", TAMPER_TEST_CLIENT,
            "--product", "AGENTIC_ZERO_ESSENTIAL",
            "--plan", "ESSENTIAL",
            "--activated-by", "security_regression_suite",
            "--contract-reference", "regression_suite_tamper_roundtrip",
        ],
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [sys.executable, "-m", "security.tamper_detection", "snapshot", "--client-id", TAMPER_TEST_CLIENT],
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, "-m", "security.tamper_detection", "verify", "--client-id", TAMPER_TEST_CLIENT],
        capture_output=True,
        text=True,
    )

    return SuiteCase(
        name="Tamper Detection (clean snapshot/verify round-trip)",
        module="tamper_detection",
        args=["snapshot+verify"],
        passed=result.returncode == 0,
        returncode=result.returncode,
        stdout_tail=_tail(result.stdout),
        stderr_tail=_tail(result.stderr),
    )


def run_suite() -> SuiteReport:
    cases = [run_case(name, module, args) for name, module, args in CASES]
    cases.append(run_tamper_detection_case())

    passed = sum(1 for c in cases if c.passed)
    failed = len(cases) - passed

    return SuiteReport(
        run_at=now(),
        total=len(cases),
        passed=passed,
        failed=failed,
        cases=[asdict(c) for c in cases],
    )


def run_cli() -> None:
    report = run_suite()

    print("\n" + "=" * 72)
    print("AGENTIC ZERO - SECURITY REGRESSION SUITE")
    print("=" * 72)

    for case_dict in report.cases:
        marker = "PASS" if case_dict["passed"] else "FAIL"
        print(f"\n[{marker}] {case_dict['name']}")
        if not case_dict["passed"]:
            print(f"  return code: {case_dict['returncode']}")
            if case_dict["stdout_tail"]:
                print("  --- stdout (tail) ---")
                for line in case_dict["stdout_tail"].splitlines():
                    print(f"  {line}")
            if case_dict["stderr_tail"]:
                print("  --- stderr (tail) ---")
                for line in case_dict["stderr_tail"].splitlines():
                    print(f"  {line}")

    print("\n" + "=" * 72)
    print(f"TOTAL: {report.total}   PASSED: {report.passed}   FAILED: {report.failed}")
    print("=" * 72)

    output_path = Path("security/state/security_regression_suite_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOutput: {output_path}")

    if report.failed:
        print("\nSecurity Regression Suite: RED")
        raise SystemExit(1)

    print("\nSecurity Regression Suite: GREEN")


if __name__ == "__main__":
    run_cli()
