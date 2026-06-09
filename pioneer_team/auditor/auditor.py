"""
AGENTIC ZERO — AUDITOR AGENT v1.0
==================================
Valida agentes en review_queue aplicando el protocolo humano embebido.
Autonomía B: aprobación automática para casos claros, escalada en casos críticos.

Uso:
    python auditor.py --process SCOR-S1.1
    python auditor.py --all              # procesa toda la review_queue
    python auditor.py --status           # muestra estado de review_queue
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from loguru import logger

# ── Rutas ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
while ROOT.name != "agentic-zero" and ROOT.parent != ROOT:
    ROOT = ROOT.parent

LIBRARY = ROOT / "library" / "scor"
CERTS = LIBRARY / "certificates"
AGENTS = LIBRARY / "agents"
PACKAGES = LIBRARY / "packages"
SOPS = LIBRARY / "sops"
REVIEW_Q = ROOT / "core" / "queue" / "jobs" / "review_queue"
COMPLETED_Q = ROOT / "core" / "queue" / "jobs" / "completed_queue"
AUDITOR_LOG = ROOT / "core" / "auditor" / "audit_log.json"

AUDITOR_LOG.parent.mkdir(parents=True, exist_ok=True)

# ── Umbrales de decisión ───────────────────────────────────────────────
THRESHOLD_AUTO_APPROVE = 88  # score ≥ 88 + NIST 100 + GDPR Clear → AUTO
THRESHOLD_APPROVE_CONDITIONS = 75  # score 75-87 → APPROVE WITH CONDITIONS
THRESHOLD_HOLD = 75  # score < 75 → HOLD

EU_AI_REQUIRED_ARTICLES = ["art_9", "art_10", "art_11"]


# ══════════════════════════════════════════════════════════════════════
# CARGA DE DOCUMENTOS
# ══════════════════════════════════════════════════════════════════════


def load_guardian_json(process_id: str) -> dict:
    path = CERTS / f"{process_id}_guardian.json"
    if not path.exists():
        raise FileNotFoundError(f"Guardian JSON not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_builder_json(process_id: str) -> dict:
    path = AGENTS / f"{process_id}_builder.json"
    if not path.exists():
        raise FileNotFoundError(f"Builder JSON not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_package_json(process_id: str) -> dict:
    path = PACKAGES / f"{process_id}_package.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_review_queue_jobs() -> list:
    if not REVIEW_Q.exists():
        return []
    jobs = []
    for f in sorted(REVIEW_Q.glob("review_*.json")):
        with open(f, encoding="utf-8") as fh:
            job = json.load(fh)
            job["_file"] = f
            jobs.append(job)
    return jobs


# ══════════════════════════════════════════════════════════════════════
# CHECKS DE VALIDACIÓN
# ══════════════════════════════════════════════════════════════════════


def check_eu_ai_act(guardian: dict) -> dict:
    """Verifica cobertura de Arts. 9, 10, 11 del EU AI Act."""
    result = {"risk_level": "UNKNOWN", "articles": {}, "status": "PASS"}

    cert = guardian.get("certificate", guardian)
    eu = cert.get("eu_ai_act", {})
    risk = eu.get("risk_level", "HIGH_RISK")
    result["risk_level"] = risk

    conditions = cert.get("conditions", [])
    all_issues = [str(c).lower() for c in conditions]

    for art, keywords in [
        ("art_9", ["art. 9", "art.9", "risk management"]),
        ("art_10", ["art. 10", "art.10", "data governance"]),
        ("art_11", ["art. 11", "art.11", "technical documentation"]),
    ]:
        found_gap = any(kw in issue for kw in keywords for issue in all_issues)
        result["articles"][art] = "GAP" if found_gap else "OK"

    gaps_found = [a for a, v in result["articles"].items() if v == "GAP"]
    result["status"] = "GAP" if gaps_found else "PASS"

    return result


def check_iso_42001(guardian: dict) -> dict:
    """Verifica score ISO/IEC 42001."""
    cert = guardian.get("certificate", guardian)
    iso = cert.get("iso_42001", {})
    score = iso.get("score", 0)
    if isinstance(score, float) and score <= 1.0:
        score = score * 100
    if isinstance(score, str):
        score = float(score.replace("%", ""))

    return {
        "score": round(score),
        "status": "PASS" if score >= 40 else "FAIL",
        "note": "Acceptable for library"
        if score >= 40
        else "Below minimum threshold — ISO/IEC 42001 not yet mature for complex industrial processes. NIST AI RMF 100% covers the gap.",
    }


def check_nist(guardian: dict) -> dict:
    """Verifica NIST AI RMF."""
    cert = guardian.get("certificate", guardian)
    nist = cert.get("nist_ai_rmf", {})
    score = nist.get("overall_score", 0)
    if isinstance(score, float) and score <= 1.0:
        score = score * 100
    if isinstance(score, str):
        score = float(score.replace("%", ""))

    return {"score": round(score), "status": "PASS" if score >= 95 else "GAP"}


def check_gdpr(guardian: dict) -> dict:
    """Verifica GDPR AI."""
    cert = guardian.get("certificate", guardian)
    gdpr = cert.get("gdpr", cert.get("gdpr_ai", {}))
    issues = gdpr.get("issues", [])
    personal_data = gdpr.get("personal_data_involved", False)
    has_issues = len(issues) > 0

    return {
        "status": "ISSUES" if has_issues else "CLEAR",
        "personal_data": personal_data,
        "detail": str(issues) if has_issues else "Clear",
    }


def check_quality(guardian: dict) -> dict:
    """Verifica quality score."""
    cert = guardian.get("certificate", guardian)
    score = cert.get("quality_score", 0)
    if isinstance(score, float) and score <= 1.0:
        score = score * 100
    if isinstance(score, str):
        score = float(score.replace("%", ""))
    issues = cert.get("quality_issues", [])

    return {
        "score": round(score),
        "status": "PASS" if score >= 80 else "FAIL",
        "issues": issues,
    }


def check_artifacts(process_id: str) -> dict:
    """Verifica existencia de artefactos requeridos."""
    checks = {
        "sop": (SOPS / f"{process_id}_sop.md").exists(),
        "builder_json": (AGENTS / f"{process_id}_builder.json").exists(),
        "package_json": (PACKAGES / f"{process_id}_package.json").exists(),
        "certificate": (CERTS / f"{process_id}_certificate.txt").exists(),
    }
    # Código del agente — buscar en agents/code/
    code_dir = AGENTS / "code"
    builder = {}
    try:
        builder = load_builder_json(process_id)
    except Exception:
        pass
    agent_name = builder.get("agent_name", builder.get("agent", {}).get("name", ""))
    if agent_name:
        checks["agent_code"] = (code_dir / f"{agent_name}.py").exists()
    else:
        checks["agent_code"] = (
            any(code_dir.glob("*.py")) if code_dir.exists() else False
        )

    all_ok = all(checks.values())
    return {"checks": checks, "status": "PASS" if all_ok else "GAP"}


# ══════════════════════════════════════════════════════════════════════
# MOTOR DE DECISIÓN
# ══════════════════════════════════════════════════════════════════════


def make_decision(process_id: str, guardian: dict) -> dict:
    """Aplica lógica de autonomía B y devuelve decisión."""

    cert = guardian.get("certificate", guardian)
    overall_score = cert.get("overall_score", guardian.get("overall_score", 0))
    if isinstance(overall_score, float) and overall_score <= 1.0:
        overall_score = overall_score * 100
    if isinstance(overall_score, str):
        overall_score = float(overall_score.replace("%", ""))
    overall_score = round(overall_score)

    eu_check = check_eu_ai_act(guardian)
    iso_check = check_iso_42001(guardian)
    nist_check = check_nist(guardian)
    gdpr_check = check_gdpr(guardian)
    quality_check = check_quality(guardian)
    artifact_check = check_artifacts(process_id)

    checks = {
        "overall_score": overall_score,
        "eu_ai_act": eu_check,
        "iso_42001": iso_check,
        "nist_ai_rmf": nist_check,
        "gdpr_ai": gdpr_check,
        "quality": quality_check,
        "artifacts": artifact_check,
    }

    # ── Lógica de decisión ─────────────────────────────────────────
    conditions = []
    escalate = False
    decision = "APPROVE"

    # REJECT inmediato — solo si GDPR issues Y score bajo O artifacts faltantes
    gdpr_blocking = gdpr_check["status"] == "ISSUES" and (
        overall_score < THRESHOLD_APPROVE_CONDITIONS
        or artifact_check["status"] != "PASS"
    )

    if gdpr_blocking:
        decision = "REJECT"
        escalate = True
        conditions.append("GDPR violation detected — immediate escalation required")

    elif (
        gdpr_check["status"] == "ISSUES"
        and overall_score >= THRESHOLD_APPROVE_CONDITIONS
    ):
        # GDPR issues pero score aceptable → APPROVE WITH CONDITIONS
        # El Guardian ya certificó para library — el Auditor añade condiciones GDPR
        decision = "APPROVE_WITH_CONDITIONS"
        delivery = True
        escalate = True
        conditions.append(
            "GDPR issues noted (non-blocking): define lawful basis and retention policy before client deployment"
        )
        conditions.append(
            f"Overall score {overall_score}% meets threshold — approved with GDPR remediation plan required"
        )

    elif quality_check["status"] == "FAIL":
        decision = "REJECT"
        escalate = True
        conditions.append("Quality check failed — agent code or tests incomplete")

    # HOLD
    elif overall_score < THRESHOLD_HOLD:
        decision = "HOLD"
        escalate = True
        conditions.append(
            f"Overall score {overall_score}% below minimum threshold {THRESHOLD_HOLD}%"
        )

    elif eu_check["status"] == "FAIL":
        decision = "HOLD"
        escalate = True
        missing = [a for a, v in eu_check["articles"].items() if v == "MISSING"]
        conditions.append(f"EU AI Act articles MISSING: {', '.join(missing)}")

    elif iso_check["status"] == "FAIL":
        decision = "HOLD"
        escalate = True
        conditions.append(
            f"ISO/IEC 42001 score {iso_check['score']}% below 40% minimum — standard not yet mature for complex industrial operational processes"
        )

    else:
        # AUTO-APPROVE
        if (
            overall_score >= THRESHOLD_AUTO_APPROVE
            and nist_check["status"] == "PASS"
            and gdpr_check["status"] == "CLEAR"
            and eu_check["status"] in ("PASS", "GAP")
        ):
            decision = "AUTO_APPROVE"
            delivery = True

            if eu_check["status"] == "GAP":
                gaps = [a for a, v in eu_check["articles"].items() if v == "GAP"]
                conditions.append(
                    f"EU AI Act gaps noted (non-blocking): {', '.join(gaps)}"
                )
            if iso_check["score"] < 80:
                conditions.append(
                    f"ISO/IEC 42001 at {iso_check['score']}% — monitor evolution"
                )

        # APPROVE WITH CONDITIONS
        else:
            decision = "APPROVE_WITH_CONDITIONS"
            delivery = True
            escalate = True

            if eu_check["status"] == "GAP":
                gaps = [a for a, v in eu_check["articles"].items() if v == "GAP"]
                conditions.append(
                    f"EU AI Act gaps require documentation: {', '.join(gaps)}"
                )
            if iso_check["score"] < 80:
                conditions.append(
                    f"ISO/IEC 42001 at {iso_check['score']}% — improvement roadmap required"
                )
            if nist_check["status"] != "PASS":
                conditions.append(
                    f"NIST AI RMF at {nist_check['score']}% — review governance controls"
                )

    # Delivery flag
    delivery = decision in ("AUTO_APPROVE", "APPROVE_WITH_CONDITIONS")
    restricted = decision == "APPROVE_WITH_CONDITIONS"

    return {
        "process_id": process_id,
        "decision": decision,
        "delivery": delivery,
        "restricted": restricted,
        "escalate": escalate,
        "conditions": conditions,
        "checks": checks,
        "audited_at": datetime.now().isoformat(),
        "auditor": "Auditor Agent v1.0 — Agentic Zero",
    }


# ══════════════════════════════════════════════════════════════════════
# OUTPUT Y LOG
# ══════════════════════════════════════════════════════════════════════

DECISION_COLORS = {
    "AUTO_APPROVE": "✅ AUTO-APPROVED",
    "APPROVE_WITH_CONDITIONS": "✅ APPROVED WITH CONDITIONS",
    "HOLD": "⏸️  HOLD",
    "REJECT": "❌ REJECT",
}


def print_report(result: dict):
    d = result["decision"]
    c = result["checks"]
    print(f"\n{'═' * 55}")
    print(f"  AUDITOR REPORT — {result['process_id']}")
    print(f"{'═' * 55}")
    print(f"  Decision:      {DECISION_COLORS.get(d, d)}")
    print(f"  Delivery:      {'✅ True' if result['delivery'] else '❌ False'}")
    print(f"  Restricted:    {'⚠️  Yes' if result['restricted'] else 'No'}")
    print(
        f"  Escalate:      {'⚠️  Yes — human review needed' if result['escalate'] else 'No'}"
    )
    print(f"\n  SCORES")
    print(f"  {'─' * 40}")
    print(f"  Overall:       {c['overall_score']}%")
    print(f"  ISO/IEC 42001: {c['iso_42001']['score']}%  [{c['iso_42001']['status']}]")
    print(
        f"  NIST AI RMF:   {c['nist_ai_rmf']['score']}%  [{c['nist_ai_rmf']['status']}]"
    )
    print(f"  GDPR AI:       {c['gdpr_ai']['status']}")
    print(f"  Quality:       {c['quality']['score']}%  [{c['quality']['status']}]")
    print(f"\n  EU AI Act Articles")
    print(f"  {'─' * 40}")
    for art, status in c["eu_ai_act"]["articles"].items():
        icon = "✅" if status == "OK" else "⚠️ " if status == "GAP" else "❌"
        print(f"  {icon} {art.upper().replace('_', '.')}: {status}")
    print(f"\n  Artifacts")
    print(f"  {'─' * 40}")
    for art, ok in c["artifacts"]["checks"].items():
        print(f"  {'✅' if ok else '❌'} {art}")
    if result["conditions"]:
        print(f"\n  Conditions / Notes")
        print(f"  {'─' * 40}")
        for cond in result["conditions"]:
            print(f"  · {cond}")
    print(f"\n  Audited: {result['audited_at']}")
    print(f"{'═' * 55}\n")


def save_audit_result(result: dict):
    """Guarda resultado en log de auditoría."""
    log = []
    if AUDITOR_LOG.exists():
        with open(AUDITOR_LOG, encoding="utf-8") as f:
            try:
                log = json.load(f)
            except Exception:
                log = []
    log.append(result)
    with open(AUDITOR_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def update_guardian_json(process_id: str, result: dict):
    """Actualiza guardian.json con la decisión del Auditor."""
    path = CERTS / f"{process_id}_guardian.json"
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        guardian = json.load(f)

    guardian["auditor_review"] = {
        "decision": result["decision"],
        "delivery": result["delivery"],
        "restricted": result["restricted"],
        "conditions": result["conditions"],
        "audited_at": result["audited_at"],
        "auditor": result["auditor"],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(guardian, f, indent=2, ensure_ascii=False)
    logger.success(f"Guardian JSON updated: {path.name}")


def move_review_job(process_id: str):
    """Mueve el job de review_queue a completed_queue."""
    for job_file in REVIEW_Q.glob("review_*.json"):
        with open(job_file, encoding="utf-8") as f:
            job = json.load(f)
        if (
            job.get("process_id") == process_id
            or job.get("data", {}).get("process_id") == process_id
        ):
            dest = COMPLETED_Q / job_file.name
            job_file.rename(dest)
            logger.success(f"Job moved to completed: {job_file.name}")
            return
    logger.warning(f"Review job not found for {process_id}")


# ══════════════════════════════════════════════════════════════════════
# PROCESO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════


def audit_process(process_id: str) -> dict:
    logger.info(f"Auditor starting: {process_id}")
    try:
        guardian = load_guardian_json(process_id)
    except FileNotFoundError as e:
        logger.error(str(e))
        return {"process_id": process_id, "decision": "ERROR", "error": str(e)}

    result = make_decision(process_id, guardian)
    print_report(result)
    save_audit_result(result)
    update_guardian_json(process_id, result)

    if result["decision"] in ("AUTO_APPROVE", "APPROVE_WITH_CONDITIONS"):
        move_review_job(process_id)
        logger.success(
            f"{process_id} → {result['decision']} · Delivery: {result['delivery']}"
        )
    elif result["decision"] == "HOLD":
        logger.warning(f"{process_id} → HOLD · Requires builder rework")
    elif result["decision"] == "REJECT":
        logger.error(f"{process_id} → REJECT · Immediate attention required")

    return result


def show_status():
    jobs = get_review_queue_jobs()
    print(f"\n📋 Review Queue — {len(jobs)} jobs pending\n{'─' * 45}")
    if not jobs:
        print("  Queue empty ✅")
        return
    for job in jobs:
        pid = job.get("process_id", job.get("data", {}).get("process_id", "unknown"))
        ts = job.get("created_at", job.get("timestamp", ""))
        print(f"  · {pid}  [{ts}]")
    print()


def audit_all():
    jobs = get_review_queue_jobs()
    if not jobs:
        print("✅ Review queue is empty.")
        return
    results = []
    seen = set()
    for job in jobs:
        # Estructura real: payload.process_id
        pid = (
            job.get("payload", {}).get("process_id")
            or job.get("process_id")
            or job.get("data", {}).get("process_id")
        )
        if not pid:
            for v in job.values():
                if isinstance(v, str) and v.startswith("SCOR-"):
                    pid = v
                    break
        if pid:
            if pid in seen:
                logger.debug(f"Skipping duplicate: {pid}")
                continue
            seen.add(pid)
            r = audit_process(pid)
            results.append(r)
        else:
            logger.warning(f"Cannot determine process_id from job: {job.get('_file')}")

    # Resumen final
    print(f"\n{'═' * 55}")
    print(f"  AUDIT COMPLETE — {len(results)} processes")
    print(f"{'═' * 55}")
    for r in results:
        icon = {
            "AUTO_APPROVE": "✅",
            "APPROVE_WITH_CONDITIONS": "✅⚠️",
            "HOLD": "⏸️",
            "REJECT": "❌",
            "ERROR": "💥",
        }.get(r["decision"], "?")
        print(f"  {icon}  {r['process_id']:20} {r['decision']}")
    print()


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero — Auditor Agent v1.0")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--process",
        metavar="PROCESS_ID",
        help="Audit a single process (e.g. SCOR-S1.1)",
    )
    group.add_argument(
        "--all", action="store_true", help="Audit all jobs in review_queue"
    )
    group.add_argument("--status", action="store_true", help="Show review_queue status")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.all:
        audit_all()
    elif args.process:
        audit_process(args.process)
