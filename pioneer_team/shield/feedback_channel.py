"""
AGENTIC ZERO -- CooperBench Shield v1.0
feedback_channel.py -- Inter-Agent Feedback Channel

Principio CooperBench #4: Strong Inter-Agent Channels
Canal directo Guardian -> Builder cuando hay HOLD o REJECT.
El Builder recibe el motivo exacto y puede relanzar automaticamente.

Principio CooperBench #1: Reward Coordination
El sistema premia los ciclos cortos de correccion -- si el Builder
corrige en el primer retry, el proceso se completa sin intervencion humana.

Sin este canal: Guardian rechaza -> job va a review_queue -> espera manual.
Con este canal: Guardian rechaza -> Builder recibe feedback -> reintenta automaticamente.

Basado en: Zhu & Yang, CooperBench, ICLR 2026
Ubicacion: F:/agentic-zero/pioneer_team/shield/feedback_channel.py
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from shield_state import ShieldState, AgentRole, ProcessStatus, shield

log = logging.getLogger("shield.feedback")

ROOT        = Path(os.getenv("AGENTIC_ZERO_ROOT", "F:/agentic-zero"))
LIBRARY_PATH = Path(os.getenv("LIBRARY_PATH", "F:/agentic-zero/library"))
QUEUE_PATH  = ROOT / "core" / "queue"
BUILDER_PATH = ROOT / "pioneer_team" / "builder"
FEEDBACK_LOG = ROOT / "pioneer_team" / "shield" / "state" / "feedback_log.json"
FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)

MAX_AUTO_RETRIES = 2   # maximo de retries automaticos antes de escalar a humano


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# FEEDBACK ANALYZER -- interpreta el rechazo y genera el fix
# ============================================================

KNOWN_FIXES = {
    "GDPR": {
        "description": "Agente sin compliance GDPR",
        "fix_prompt_addition": (
            "CRITICAL: Include explicit GDPR compliance in the agent code. "
            "Add: lawful_basis check, data_minimization, retention_policy, "
            "right_to_erasure handler, and audit_log for all personal data operations. "
            "Every data access must be logged with timestamp and legal basis."
        ),
        "severity": "high"
    },
    "EU AI Act": {
        "description": "Agente sin compliance EU AI Act",
        "fix_prompt_addition": (
            "CRITICAL: Include EU AI Act compliance. Add: risk_classification "
            "(limited risk for this process type), transparency_notice, "
            "human_oversight_checkpoint, and explainability_log for every "
            "automated decision. Document ART.9 risk management measures."
        ),
        "severity": "high"
    },
    "ISO 42001": {
        "description": "Score ISO 42001 insuficiente",
        "fix_prompt_addition": (
            "Include ISO/IEC 42001:2023 controls: AI_objectives alignment, "
            "performance_monitoring hooks, continual_improvement log, "
            "and documented AI policy reference in the agent header."
        ),
        "severity": "medium"
    },
    "score_low": {
        "description": "Score general insuficiente",
        "fix_prompt_addition": (
            "Improve overall quality: add comprehensive error handling, "
            "input validation, output verification, detailed logging, "
            "and inline documentation for every function. "
            "Ensure all business rules are explicitly coded, not implied."
        ),
        "severity": "medium"
    },
    "codigo_roto": {
        "description": "Codigo sin clases ni funciones validas",
        "fix_prompt_addition": (
            "Generate a complete, executable Python agent class with: "
            "__init__, execute(), validate_input(), log_action(), "
            "and handle_error() methods. Do not generate pseudocode or placeholders."
        ),
        "severity": "critical"
    },
    "json_invalido": {
        "description": "Package JSON invalido o corrupto",
        "fix_prompt_addition": (
            "Ensure all JSON outputs are valid and complete. "
            "Every required field must be present and non-null. "
            "Validate JSON structure before returning."
        ),
        "severity": "high"
    }
}


def analyze_rejection(rejection_reasons: list, score: float) -> dict:
    """
    Analiza los motivos de rechazo y genera el plan de fix.
    Principio #1: el sistema identifica exactamente que hay que corregir.
    """
    fixes_needed = []
    severity = "low"

    severity_order = {"critical": 3, "high": 2, "medium": 1, "low": 0}

    for reason in rejection_reasons:
        reason_lower = reason.lower()
        matched = False
        for key, fix_data in KNOWN_FIXES.items():
            if key.lower() in reason_lower:
                fixes_needed.append({
                    "issue":              key,
                    "description":        fix_data["description"],
                    "fix_prompt_addition": fix_data["fix_prompt_addition"],
                    "severity":           fix_data["severity"]
                })
                # Tomar la severidad mas alta
                if severity_order.get(fix_data["severity"], 0) > severity_order.get(severity, 0):
                    severity = fix_data["severity"]
                matched = True
                break
        if not matched:
            fixes_needed.append({
                "issue":              "unknown",
                "description":        reason,
                "fix_prompt_addition": f"Fix the following issue: {reason}",
                "severity":           "medium"
            })

    if score < 0.75 and not any(f["issue"] == "score_low" for f in fixes_needed):
        fixes_needed.append({
            "issue":              "score_low",
            "description":        f"Score {score} insuficiente (minimo 0.75)",
            "fix_prompt_addition": KNOWN_FIXES["score_low"]["fix_prompt_addition"],
            "severity":           "medium"
        })

    return {
        "fixes_needed":     fixes_needed,
        "overall_severity": severity,
        "auto_fixable":     severity != "critical" or len(fixes_needed) <= 2,
        "combined_prompt":  "\n\n".join(f["fix_prompt_addition"] for f in fixes_needed)
    }


# ============================================================
# FEEDBACK CHANNEL -- logica principal
# ============================================================

class FeedbackChannel:
    """
    Canal directo Guardian -> Builder.
    Gestiona el ciclo de feedback y retry automatico.
    """

    def __init__(self, state: ShieldState = shield):
        self.state = state

    def _log_feedback(self, process_id: str, entry: dict):
        """Persiste el feedback en el log."""
        log_data = []
        if FEEDBACK_LOG.exists():
            try:
                with open(FEEDBACK_LOG, encoding="utf-8") as f:
                    log_data = json.load(f)
            except Exception:
                log_data = []
        log_data.append(entry)
        with open(FEEDBACK_LOG, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

    def process_rejection(
        self,
        process_id: str,
        score: float,
        rejection_reasons: list,
        framework: str = "scor",
        auto_retry: bool = True
    ) -> dict:
        """
        Procesa un rechazo del Guardian:
        1. Analiza los motivos
        2. Genera el plan de fix
        3. Decide si puede hacer retry automatico o escala al humano
        4. Si auto_retry: relanza el Builder con el fix
        """
        log.info(f"-> Procesando rechazo: {process_id} (score: {score})")

        # Verificar historial de retries
        process_record = self.state.get_process(process_id)
        retry_count = process_record.get("retry_count", 0) if process_record else 0

        # Analizar que hay que corregir
        analysis = analyze_rejection(rejection_reasons, score)

        feedback_entry = {
            "process_id":       process_id,
            "timestamp":        _now(),
            "score":            score,
            "rejection_reasons": rejection_reasons,
            "retry_count":      retry_count,
            "analysis":         analysis,
            "action_taken":     None
        }

        if retry_count >= MAX_AUTO_RETRIES:
            # Escalar a revision humana
            action = "escalated_to_human"
            log.warning(
                f"WARN {process_id}: {retry_count} retries agotados -- "
                f"escalando a revision humana"
            )
            self.state.update_status(
                process_id, ProcessStatus.REVIEW, AgentRole.GUARDIAN,
                notes=f"Auto-retries agotados ({retry_count}/{MAX_AUTO_RETRIES}). "
                      f"Requiere revision manual. Score: {score}"
            )
            self._notify_human(process_id, analysis, retry_count)

        elif not analysis["auto_fixable"]:
            # Problema critico -- escalar
            action = "escalated_critical"
            log.warning(f"WARN {process_id}: problema critico -- revision humana necesaria")
            self.state.update_status(
                process_id, ProcessStatus.REVIEW, AgentRole.GUARDIAN,
                notes=f"Severidad critica. Revision manual requerida. Score: {score}"
            )
            self._notify_human(process_id, analysis, retry_count)

        elif auto_retry:
            # Retry automatico con fix
            action = "auto_retry"
            log.info(f"-> Auto-retry {retry_count + 1}/{MAX_AUTO_RETRIES}: {process_id}")
            self.state.update_status(
                process_id, ProcessStatus.RETRYING, AgentRole.BUILDER,
                notes=f"Auto-retry {retry_count + 1}. Fixes: {[f['issue'] for f in analysis['fixes_needed']]}"
            )
            self._trigger_builder_retry(process_id, analysis, framework)

        else:
            # Feedback registrado, retry manual
            action = "feedback_registered"
            log.info(f"OK Feedback registrado para {process_id} -- retry manual requerido")

        feedback_entry["action_taken"] = action
        self._log_feedback(process_id, feedback_entry)

        return {
            "process_id": process_id,
            "action":     action,
            "analysis":   analysis,
            "retry_count": retry_count
        }

    def _trigger_builder_retry(
        self,
        process_id: str,
        analysis: dict,
        framework: str
    ):
        """
        Relanza el Builder con el fix prompt adicional.
        Escribe un archivo de fix-context que el Builder lee al arrancar.
        """
        fix_context_path = (
            ROOT / "pioneer_team" / "shield" / "state" /
            f"{process_id}_fix_context.json"
        )
        fix_context = {
            "process_id":      process_id,
            "framework":       framework,
            "retry_at":        _now(),
            "fixes_needed":    analysis["fixes_needed"],
            "combined_prompt": analysis["combined_prompt"],
            "severity":        analysis["overall_severity"]
        }
        with open(fix_context_path, "w", encoding="utf-8") as f:
            json.dump(fix_context, f, indent=2, ensure_ascii=False)

        log.info(f"OK Fix context escrito: {fix_context_path.name}")

        # Intentar relanzar via queue_system
        try:
            queue_script = QUEUE_PATH / "queue_system.py"
            if queue_script.exists():
                result = subprocess.run(
                    [sys.executable, str(queue_script),
                     "--pipeline", process_id,
                     "--framework", framework],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(QUEUE_PATH)
                )
                if result.returncode == 0:
                    log.info(f"OK Builder relanzado via queue: {process_id}")
                else:
                    log.warning(
                        f"WARN Queue relaunch fallo: {result.stderr[:200]}. "
                        f"Fix context disponible para retry manual."
                    )
            else:
                log.info(f"OK Fix context listo. Relanzar manualmente: "
                         f"python queue_system.py --pipeline {process_id}")
        except Exception as e:
            log.warning(f"WARN Auto-relaunch no disponible: {e}. Fix context guardado.")

    def _notify_human(self, process_id: str, analysis: dict, retry_count: int):
        """
        Genera notificacion para revision humana.
        Escribe en el review log con toda la informacion necesaria.
        """
        review_path = (
            ROOT / "pioneer_team" / "shield" / "state" /
            f"{process_id}_review_required.json"
        )
        review_data = {
            "process_id":       process_id,
            "requires_review":  True,
            "created_at":       _now(),
            "retry_count":      retry_count,
            "analysis":         analysis,
            "human_action": (
                "Revisar el agente generado y aplicar los fixes manuales indicados. "
                "Una vez corregido, ejecutar: "
                f"python queue_system.py --pipeline {process_id}"
            )
        }
        with open(review_path, "w", encoding="utf-8") as f:
            json.dump(review_data, f, indent=2, ensure_ascii=False)
        log.info(f"OK Review file generado: {review_path.name}")

    def get_pending_feedback(self, agent: AgentRole) -> list:
        """Recupera todos los feedbacks pendientes para un agente."""
        active = self.state.get_active_processes()
        pending = []
        for process in active:
            fb = self.state.get_feedback_for(process["process_id"], agent)
            if fb:
                pending.append({
                    "process_id": process["process_id"],
                    "feedback":   fb
                })
        return pending

    def get_fix_context(self, process_id: str) -> Optional[dict]:
        """El Builder lee esto al arrancar un retry."""
        fix_path = (
            ROOT / "pioneer_team" / "shield" / "state" /
            f"{process_id}_fix_context.json"
        )
        if not fix_path.exists():
            return None
        with open(fix_path, encoding="utf-8") as f:
            return json.load(f)

    def print_channel_status(self):
        """Resumen del canal de feedback."""
        retry_candidates = self.state.get_retry_candidates()
        active = self.state.get_active_processes()
        in_retry = [p for p in active if p["status"] == ProcessStatus.RETRYING.value]

        print("\n" + "=" * 50)
        print("  CooperBench Shield -- Feedback Channel")
        print("=" * 50)
        print(f"  Candidatos retry   : {len(retry_candidates)}")
        print(f"  En retry activo    : {len(in_retry)}")
        print(f"  Max auto-retries   : {MAX_AUTO_RETRIES}")
        if retry_candidates:
            print("\n  Procesos con feedback pendiente:")
            for p in retry_candidates:
                print(f"    {p['process_id']} -- retries: {p['retry_count']}/{MAX_AUTO_RETRIES}")
        print("=" * 50)


# Instancia global
feedback_channel = FeedbackChannel()


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="CooperBench Shield -- Feedback Channel"
    )
    parser.add_argument("--status",    action="store_true", help="Estado del canal")
    parser.add_argument("--pending",   help="Feedbacks pendientes para un agente (builder/guardian...)")
    parser.add_argument("--fix-context", help="Ver fix context de un proceso")
    parser.add_argument("--simulate",  help="Simular rechazo de un proceso (test)")
    args = parser.parse_args()

    if args.status:
        feedback_channel.print_channel_status()

    elif args.pending:
        try:
            role = AgentRole(args.pending)
            pending = feedback_channel.get_pending_feedback(role)
            print(f"Feedbacks pendientes para {role.value}: {len(pending)}")
            for p in pending:
                print(f"  {p['process_id']}: {len(p['feedback'])} mensajes")
        except ValueError:
            print(f"Rol no valido: {args.pending}. Usa: builder, packager, guardian, auditor")

    elif args.fix_context:
        ctx = feedback_channel.get_fix_context(args.fix_context)
        if ctx:
            print(json.dumps(ctx, indent=2, ensure_ascii=False))
        else:
            print(f"Sin fix context para: {args.fix_context}")

    elif args.simulate:
        print(f"Simulando rechazo para: {args.simulate}")
        shield.register_process(args.simulate, AgentRole.GUARDIAN)
        result = feedback_channel.process_rejection(
            process_id=args.simulate,
            score=0.65,
            rejection_reasons=[
                "GDPR compliance missing",
                "EU AI Act ART.9 not documented",
                "overall score 0.65 below threshold"
            ],
            framework="scor",
            auto_retry=False  # no relanzar en simulacion
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        feedback_channel.print_channel_status()
