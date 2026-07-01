# pioneer_team/architect/architect_regression_suite.py

"""
AGENTIC ZERO - PIONEER TEAM
Architect Regression Suite v1.0

Role:
  pioneer_team/architect/ never had an aggregate regression test - unlike
  security/ (security_regression_suite.py) and saas/ (saas_smoke_test.py).
  Today's session built/modified functional_consultant.py,
  consultant_accountability.py, connector_resolver.py, and
  customer_pipeline.py's SWARM branch - all part of one real pipeline,
  with no single test confirming they still work together. This closes
  that gap, same pattern as the other two suites: one command, real
  in-process calls (not mocked), GREEN/RED verdict.

  Does NOT call the real Anthropic API (no ANTHROPIC_API_KEY assumed
  available in CI/automated runs) - tests the deterministic fallback
  path and the structural/integration logic that doesn't depend on a
  live LLM call. The real-Claude path is validated separately, by hand,
  with a real key (see PRIORITARIO note already on file for that).
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


def assert_true(condition: bool, message: str) -> dict[str, Any]:
    return {"check": message, "passed": bool(condition)}


def test_connector_resolver_known_system() -> dict[str, Any]:
    from connector_resolver import resolve_connector

    spec = resolve_connector("Usamos SAP S/4HANA Cloud")
    return assert_true(
        spec.verified and spec.matched_id == "sap_s4hana_cloud" and "OData" in spec.protocol,
        "connector_resolver resolves a known system (SAP S/4HANA Cloud) to a verified, correct spec",
    )


def test_connector_resolver_distinguishes_sap_variants() -> dict[str, Any]:
    from connector_resolver import resolve_connector

    cloud = resolve_connector("SAP S/4HANA Cloud")
    onprem = resolve_connector("SAP ECC on-premise")
    return assert_true(
        cloud.matched_id != onprem.matched_id and cloud.protocol != onprem.protocol,
        "connector_resolver gives SAP Cloud and SAP on-premise DIFFERENT protocols, not the same one",
    )


def test_connector_resolver_unknown_system_no_invention() -> dict[str, Any]:
    from connector_resolver import resolve_connector

    spec = resolve_connector("Un ERP propietario que nadie conoce")
    return assert_true(
        spec.verified is False and "research" in spec.recommended_pattern.lower(),
        "connector_resolver never invents a protocol for an unknown system - flags for research instead",
    )


def test_functional_consultant_deterministic_fallback() -> dict[str, Any]:
    from functional_consultant import consult_on_intent

    result = consult_on_intent("Necesitamos S&OP con demand planning y supply planning", {}, "/tmp/architect_suite_test1", use_llm=False)
    return assert_true(
        result.method == "deterministic_fallback" and result.route in ("SWARM", "AGENTIC_ONE_ENTERPRISE", "PROCESS_AGENT", "COMPLEX_PROCESS_AGENT"),
        "functional_consultant's deterministic fallback produces a valid route without crashing when no LLM is available",
    )


def test_functional_consultant_audits_every_consultation() -> dict[str, Any]:
    from functional_consultant import consult_on_intent, _client_id_from_package_dir
    from security.audit_logger import AuditLogger
    from consultant_accountability import _safe_client_id, _repo_root

    client_id_hint = "/tmp/architect_suite_test_clients/audit_check_client"
    consult_on_intent("texto de prueba", {}, client_id_hint, use_llm=False)

    # The real slug log_consultation() uses is _safe_client_id(package_dir)
    # applied to the WHOLE path string (not _client_id_from_package_dir,
    # which is a DIFFERENT helper used only for token_governance billing -
    # confirmed by reading the actual call site, not assumed).
    expected_slug = _safe_client_id(client_id_hint)
    logger = AuditLogger(audit_root=_repo_root() / "security" / "state" / "audit_logs")
    events = logger.read_events(expected_slug, limit=10)
    found = any(e.get("event_type") == "CONSULTANT_DECISION" for e in events)
    return assert_true(found, "Every consultation is automatically logged to the audit trail, with no extra call needed")


def test_siop_schema_compatible_with_architect_bridge() -> dict[str, Any]:
    """Replays the exact field-access pattern architect_siop_bridge.py's
    siop_to_blueprint() uses (confirmed line-by-line against the real
    file earlier today) against a freshly-generated SIOP - catches a
    future schema drift before it reaches a real client pipeline run.
    """
    from functional_consultant import claude_consult, build_siop_internal
    import functional_consultant as fc

    fake_response = json.dumps({
        "route": "PROCESS_AGENT", "level_1_process": "Schema Check", "company": "", "sector": "", "erp": "",
        "confidence": 0.8, "rationale": "test", "missing_information": [],
        "process_flow_steps": [{"step_id": "STEP-01", "name": "x", "system": "", "inputs": ["a"], "outputs": ["b"], "rule": "r", "confidence": 0.9}],
        "decision_rules": ["d"], "exception_rules": ["e"], "approval_rules": ["a"], "kpis": ["k"],
        "autonomous_actions": [], "approval_required": [], "always_human": [],
        "matched_organisms": [], "new_organisms": [],
    })
    original_call_claude = fc.call_claude
    fc.call_claude = lambda prompt: (f"## FINAL_DECISION\n{fake_response}", 100, 50)
    try:
        result = claude_consult("test", "/tmp/architect_suite_test2")
        siop = build_siop_internal(result)
    finally:
        fc.call_claude = original_call_claude

    es = siop.get("executive_summary", {})
    bc = siop.get("business_context", {})
    biz_rules = siop.get("business_rules", {})
    autonomy = siop.get("autonomy_design", {})

    ok = (
        bool(es.get("process_name"))
        and "decision_rules" in biz_rules
        and "thresholds" in autonomy
        and isinstance(siop.get("process_flow"), list)
        and siop.get("integration_design") is not None
    )
    return assert_true(ok, "Generated SIOP has every field architect_siop_bridge.py's siop_to_blueprint() reads, plus integration_design attached")


def test_consultant_accountability_rejects_empty_attribution() -> dict[str, Any]:
    from consultant_accountability import record_correction

    try:
        record_correction(
            consultation_id="X", client_id="test", original_route="SWARM", original_tier="Standard",
            original_confidence=0.7, corrected_route="PROCESS_AGENT", corrected_tier="Essential",
            corrected_by="", rationale="something",
        )
        return assert_true(False, "consultant_accountability rejects a correction with empty corrected_by")
    except ValueError:
        return assert_true(True, "consultant_accountability rejects a correction with empty corrected_by")


def test_consultant_accountability_correction_generates_evidence() -> dict[str, Any]:
    from consultant_accountability import record_correction
    from agentic_shield.evidence_shield import verify_evidence_package

    record = record_correction(
        consultation_id="ARCHITECT-SUITE-CHECK",
        client_id="Architect Suite Test Co",
        original_route="SWARM", original_tier="Standard", original_confidence=0.78,
        corrected_route="PROCESS_AGENT", corrected_tier="Essential",
        corrected_by="architect_regression_suite", rationale="regression check",
    )

    evidence_path = Path("agentic_shield/evidence/Architect_Suite_Test_Co/EVIDENCE-ARCHITECT-SUITE-CHECK.json")
    if not evidence_path.exists():
        return assert_true(False, "Correction generates a verifiable evidence package (file not found)")

    data = json.loads(evidence_path.read_text(encoding="utf-8"))
    valid = verify_evidence_package(data) and data.get("human_accountability_present") is True
    return assert_true(valid, "Correction generates a verifiable evidence package with human_accountability_present=True")


CHECKS = [
    test_connector_resolver_known_system,
    test_connector_resolver_distinguishes_sap_variants,
    test_connector_resolver_unknown_system_no_invention,
    test_functional_consultant_deterministic_fallback,
    test_functional_consultant_audits_every_consultation,
    test_siop_schema_compatible_with_architect_bridge,
    test_consultant_accountability_rejects_empty_attribution,
    test_consultant_accountability_correction_generates_evidence,
]


def main() -> None:
    results: list[dict[str, Any]] = []

    for check in CHECKS:
        try:
            results.append(check())
        except Exception as exc:
            results.append({"check": f"{check.__name__} (raised {type(exc).__name__}: {exc})", "passed": False})

    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed

    print("\nArchitect Regression Suite")
    print("--------------------------")
    for r in results:
        marker = "PASS" if r["passed"] else "FAIL"
        print(f"  [{marker}] {r['check']}")

    print(f"\nPassed : {passed}")
    print(f"Failed : {failed}")
    print(f"Total  : {len(results)}")

    output_path = Path("pioneer_team/architect/architect_regression_suite_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Output : {output_path}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
