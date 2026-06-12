"""
AGENTIC ZERO -- CooperBench Shield v1.0
commitment.py -- Commitment + Verification Protocol

Principio CooperBench #2: Commitment + Verification
Antes de que un agente entregue trabajo al siguiente, declara
que construyo y el receptor verifica integridad antes de procesar.

Elimina el problema actual: jobs que pasan entre workers sin
validacion de integridad -- archivos corruptos, JSON incompletos,
codigo sin ejecutar.

Puntos de commitment:
  Builder   -> Packager  : commitment de agente construido
  Packager  -> Guardian  : commitment de package completo
  Guardian  -> Auditor   : commitment de certificado emitido

Basado en: Zhu & Yang, CooperBench, ICLR 2026
Ubicacion: F:/agentic-zero/pioneer_team/shield/commitment.py
"""

import json
import hashlib
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from shield_state import ShieldState, AgentRole, ProcessStatus, shield

log = logging.getLogger("shield.commitment")

ROOT = Path(os.getenv("AGENTIC_ZERO_ROOT", "F:/agentic-zero"))
LIBRARY_PATH = Path(os.getenv("LIBRARY_PATH", "F:/agentic-zero/library"))
COMMITMENTS_DIR = ROOT / "pioneer_team" / "shield" / "commitments"
COMMITMENTS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_file(path: Path) -> Optional[str]:
    """SHA256 de un archivo para verificacion de integridad."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ============================================================
# COMMITMENT RECORD -- estructura
# ============================================================

def _commitment_record(
    process_id: str,
    from_agent: AgentRole,
    to_agent: AgentRole,
    artifacts: dict,
    metadata: Optional[dict] = None
) -> dict:
    """
    Declara que un agente entrego y que entrego.
    artifacts: {nombre: {path: str, hash: str, required: bool}}
    """
    return {
        "process_id":  process_id,
        "from_agent":  from_agent.value,
        "to_agent":    to_agent.value,
        "committed_at": _now(),
        "verified_at":  None,
        "verified":    False,
        "artifacts":   artifacts,
        "metadata":    metadata or {},
        "issues":      []
    }


# ============================================================
# BUILDER -> PACKAGER
# ============================================================

def builder_commit(process_id: str, framework: str = "scor") -> dict:
    """
    Builder declara que ha construido el agente.
    Verifica que los archivos criticos existen y tienen contenido.
    """
    log.info(f"-> Builder commitment: {process_id}")

    # Rutas esperadas segun framework
    base = LIBRARY_PATH / framework
    agent_py   = base / "agents" / "code" / f"{process_id}_agent.py"
    builder_json = base / "agents" / f"{process_id}_builder.json"

    artifacts = {
        "agent_code": {
            "path":     str(agent_py),
            "hash":     _hash_file(agent_py),
            "exists":   agent_py.exists(),
            "size_kb":  round(agent_py.stat().st_size / 1024, 2) if agent_py.exists() else 0,
            "required": True
        },
        "builder_json": {
            "path":     str(builder_json),
            "hash":     _hash_file(builder_json),
            "exists":   builder_json.exists(),
            "required": True
        }
    }

    # Verificacion basica de contenido del agente
    issues = []
    if agent_py.exists():
        content = agent_py.read_text(encoding="utf-8", errors="replace")
        if len(content) < 500:
            issues.append("agent_code demasiado corto -- posible build incompleto")
        if "class" not in content and "def " not in content:
            issues.append("agent_code sin clases ni funciones -- posible codigo roto")
        if "GDPR" not in content and "gdpr" not in content.lower():
            issues.append("WARN: GDPR no mencionado en el agente")
    else:
        issues.append(f"FAIL: agent_code no encontrado: {agent_py}")

    commitment = _commitment_record(
        process_id, AgentRole.BUILDER, AgentRole.PACKAGER, artifacts,
        metadata={"framework": framework, "issues_count": len(issues)}
    )
    commitment["issues"] = issues

    # Guardar commitment
    commit_path = COMMITMENTS_DIR / f"{process_id}_builder_commit.json"
    with open(commit_path, "w", encoding="utf-8") as f:
        json.dump(commitment, f, indent=2, ensure_ascii=False)

    # Actualizar estado en Shield
    if issues and any("FAIL" in i for i in issues):
        shield.update_status(
            process_id, ProcessStatus.REJECTED, AgentRole.BUILDER,
            notes=f"Builder commitment fallido: {'; '.join(issues)}"
        )
        log.error(f"FAIL Builder commitment RECHAZADO: {process_id} -- {issues}")
    else:
        shield.update_status(
            process_id, ProcessStatus.COMMITTED, AgentRole.BUILDER,
            notes=f"Builder commitment OK. Issues menores: {len(issues)}"
        )
        if issues:
            log.warning(f"WARN Builder commitment con advertencias: {process_id} -- {issues}")
        else:
            log.info(f"OK Builder commitment: {process_id}")

    return commitment


def packager_verify_builder(process_id: str) -> tuple[bool, list]:
    """
    Packager verifica el commitment del Builder antes de procesar.
    Principio #2: el receptor verifica antes de actuar.
    """
    commit_path = COMMITMENTS_DIR / f"{process_id}_builder_commit.json"
    if not commit_path.exists():
        log.warning(f"WARN No hay commitment de Builder para {process_id}")
        return False, ["Sin commitment de Builder"]

    with open(commit_path, encoding="utf-8") as f:
        commitment = json.load(f)

    issues = []

    # Verificar hashes -- detecta modificaciones entre commit y verificacion
    for name, artifact in commitment["artifacts"].items():
        if not artifact["exists"]:
            if artifact["required"]:
                issues.append(f"FAIL: {name} no existe")
            continue
        current_hash = _hash_file(Path(artifact["path"]))
        if current_hash != artifact["hash"]:
            issues.append(f"FAIL: {name} modificado desde el commit (hash mismatch)")

    # Verificar issues criticos del commit original
    for issue in commitment.get("issues", []):
        if "FAIL" in issue:
            issues.append(f"Heredado del Builder: {issue}")

    # Marcar como verificado
    commitment["verified"]   = len(issues) == 0
    commitment["verified_at"] = _now()
    commitment["verification_issues"] = issues

    with open(commit_path, "w", encoding="utf-8") as f:
        json.dump(commitment, f, indent=2, ensure_ascii=False)

    if issues:
        log.warning(f"WARN Verificacion Packager FALLIDA: {process_id} -- {issues}")
    else:
        log.info(f"OK Verificacion Packager: {process_id}")

    return len(issues) == 0, issues


# ============================================================
# PACKAGER -> GUARDIAN
# ============================================================

def packager_commit(process_id: str, framework: str = "scor") -> dict:
    """
    Packager declara que ha generado el package completo.
    """
    log.info(f"-> Packager commitment: {process_id}")

    base = LIBRARY_PATH / framework
    package_json  = base / "packages" / f"{process_id}_package.json"
    sop_md        = base / "sops"     / f"{process_id}_sop.md"
    demo_script   = base / "packages" / f"{process_id}_demo_script.txt"
    integration   = base / "packages" / f"{process_id}_integration_guide.md"

    artifacts = {
        "package_json": {
            "path": str(package_json), "hash": _hash_file(package_json),
            "exists": package_json.exists(), "required": True
        },
        "sop_md": {
            "path": str(sop_md), "hash": _hash_file(sop_md),
            "exists": sop_md.exists(), "required": True
        },
        "demo_script": {
            "path": str(demo_script), "hash": _hash_file(demo_script),
            "exists": demo_script.exists(), "required": False
        },
        "integration_guide": {
            "path": str(integration), "hash": _hash_file(integration),
            "exists": integration.exists(), "required": False
        }
    }

    issues = []

    # Verificar package JSON valido
    if package_json.exists():
        try:
            with open(package_json, encoding="utf-8") as f:
                pkg = json.load(f)
            required_fields = ["process_id", "agent_name", "overall_score"]
            for field in required_fields:
                if field not in pkg:
                    issues.append(f"WARN: package_json sin campo '{field}'")
        except json.JSONDecodeError as e:
            issues.append(f"FAIL: package_json invalido -- {e}")
    else:
        issues.append(f"FAIL: package_json no encontrado")

    if not sop_md.exists():
        issues.append("FAIL: SOP no encontrado")

    commitment = _commitment_record(
        process_id, AgentRole.PACKAGER, AgentRole.GUARDIAN, artifacts,
        metadata={"framework": framework, "issues_count": len(issues)}
    )
    commitment["issues"] = issues

    commit_path = COMMITMENTS_DIR / f"{process_id}_packager_commit.json"
    with open(commit_path, "w", encoding="utf-8") as f:
        json.dump(commitment, f, indent=2, ensure_ascii=False)

    if issues and any("FAIL" in i for i in issues):
        shield.update_status(
            process_id, ProcessStatus.REJECTED, AgentRole.PACKAGER,
            notes=f"Packager commitment fallido: {'; '.join(issues)}"
        )
        log.error(f"FAIL Packager commitment RECHAZADO: {process_id}")
    else:
        shield.update_status(
            process_id, ProcessStatus.PACKAGED, AgentRole.PACKAGER,
            notes="Packager commitment OK"
        )
        log.info(f"OK Packager commitment: {process_id}")

    return commitment


def guardian_verify_packager(process_id: str) -> tuple[bool, list]:
    """Guardian verifica el commitment del Packager antes de certificar."""
    commit_path = COMMITMENTS_DIR / f"{process_id}_packager_commit.json"
    if not commit_path.exists():
        return False, ["Sin commitment de Packager"]

    with open(commit_path, encoding="utf-8") as f:
        commitment = json.load(f)

    issues = []
    for name, artifact in commitment["artifacts"].items():
        if not artifact["exists"] and artifact["required"]:
            issues.append(f"FAIL: {name} requerido pero no existe")
            continue
        if artifact["hash"] and artifact["exists"]:
            current = _hash_file(Path(artifact["path"]))
            if current != artifact["hash"]:
                issues.append(f"FAIL: {name} modificado desde el commit")

    for issue in commitment.get("issues", []):
        if "FAIL" in issue:
            issues.append(f"Heredado del Packager: {issue}")

    commitment["verified"]            = len(issues) == 0
    commitment["verified_at"]         = _now()
    commitment["verification_issues"] = issues

    with open(commit_path, "w", encoding="utf-8") as f:
        json.dump(commitment, f, indent=2, ensure_ascii=False)

    if issues:
        log.warning(f"WARN Verificacion Guardian FALLIDA: {process_id} -- {issues}")
    else:
        log.info(f"OK Verificacion Guardian: {process_id}")

    return len(issues) == 0, issues


# ============================================================
# GUARDIAN -> CERTIFIED / REJECTED
# ============================================================

def guardian_commit(
    process_id: str,
    certified: bool,
    score: float,
    framework: str = "scor",
    rejection_reasons: Optional[list] = None
) -> dict:
    """
    Guardian declara el resultado de la certificacion.
    Si rechaza, el feedback va directamente al Builder (Principio #4).
    """
    base = LIBRARY_PATH / framework
    cert_txt  = base / "certificates" / f"{process_id}_certificate.txt"
    guard_json = base / "certificates" / f"{process_id}_guardian.json"

    artifacts = {
        "certificate": {
            "path": str(cert_txt), "hash": _hash_file(cert_txt),
            "exists": cert_txt.exists(), "required": certified
        },
        "guardian_json": {
            "path": str(guard_json), "hash": _hash_file(guard_json),
            "exists": guard_json.exists(), "required": certified
        }
    }

    issues = rejection_reasons or []

    commitment = _commitment_record(
        process_id, AgentRole.GUARDIAN, AgentRole.AUDITOR, artifacts,
        metadata={
            "certified": certified,
            "score":     score,
            "framework": framework
        }
    )
    commitment["issues"] = issues

    commit_path = COMMITMENTS_DIR / f"{process_id}_guardian_commit.json"
    with open(commit_path, "w", encoding="utf-8") as f:
        json.dump(commitment, f, indent=2, ensure_ascii=False)

    if certified:
        shield.update_status(
            process_id, ProcessStatus.CERTIFIED, AgentRole.GUARDIAN,
            notes=f"Certificado. Score: {score}"
        )
        log.info(f"OK Guardian CERTIFIED: {process_id} (score: {score})")
    else:
        shield.update_status(
            process_id, ProcessStatus.REJECTED, AgentRole.GUARDIAN,
            notes=f"Rechazado. Score: {score}. Razones: {rejection_reasons}"
        )
        # Feedback directo al Builder (Principio #4)
        shield.add_feedback(
            process_id,
            from_agent=AgentRole.GUARDIAN,
            to_agent=AgentRole.BUILDER,
            feedback={
                "score":           score,
                "rejection_reasons": rejection_reasons or [],
                "action_required": "Reconstruir agente con los fixes indicados",
                "timestamp":       _now()
            }
        )
        log.warning(f"WARN Guardian REJECTED: {process_id} -- feedback enviado a Builder")

    return commitment


# ============================================================
# UTILIDAD -- verificar estado de commitments de un proceso
# ============================================================

def get_commitment_chain(process_id: str) -> dict:
    """Devuelve el estado completo de la cadena de commitments."""
    chain = {}
    for stage in ["builder", "packager", "guardian"]:
        path = COMMITMENTS_DIR / f"{process_id}_{stage}_commit.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                chain[stage] = json.load(f)
        else:
            chain[stage] = None
    return chain


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="CooperBench Shield -- Commitment Protocol")
    parser.add_argument("process_id", help="ID del proceso (ej. BPMN-OTC-001)")
    parser.add_argument("--chain",    action="store_true", help="Ver cadena de commitments")
    parser.add_argument("--builder-commit",  action="store_true")
    parser.add_argument("--packager-verify", action="store_true")
    parser.add_argument("--packager-commit", action="store_true")
    parser.add_argument("--guardian-verify", action="store_true")
    parser.add_argument("--framework", default="scor")
    args = parser.parse_args()

    pid = args.process_id

    if args.chain:
        chain = get_commitment_chain(pid)
        print(json.dumps(chain, indent=2, ensure_ascii=False))

    elif args.builder_commit:
        result = builder_commit(pid, args.framework)
        print(f"Issues: {result['issues']}")

    elif args.packager_verify:
        ok, issues = packager_verify_builder(pid)
        print(f"Verificacion: {'OK' if ok else 'FAIL'}")
        for i in issues:
            print(f"  - {i}")

    elif args.packager_commit:
        result = packager_commit(pid, args.framework)
        print(f"Issues: {result['issues']}")

    elif args.guardian_verify:
        ok, issues = guardian_verify_packager(pid)
        print(f"Verificacion: {'OK' if ok else 'FAIL'}")
        for i in issues:
            print(f"  - {i}")

    else:
        parser.print_help()
