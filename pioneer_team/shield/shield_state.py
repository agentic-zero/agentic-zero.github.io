"""
AGENTIC ZERO -- CooperBench Shield v1.0
shield_state.py -- Swarm State Manager

Principio CooperBench #3: Periodic Merges
Estado compartido sincronizado entre todos los workers del Pioneer Team.
Cada agente puede leer el estado global y escribir su propio estado
sin interferir con otros procesos (multi-tenant safe).

Basado en: Zhu & Yang, CooperBench, ICLR 2026
Ubicacion: F:/agentic-zero/pioneer_team/shield/shield_state.py
"""

import json
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

log = logging.getLogger("shield.state")

ROOT = Path(os.getenv("AGENTIC_ZERO_ROOT", "F:/agentic-zero"))
SHIELD_DIR = ROOT / "pioneer_team" / "shield" / "state"
SHIELD_DIR.mkdir(parents=True, exist_ok=True)

SWARM_STATE_PATH = SHIELD_DIR / "swarm_state.json"
LOCK_TIMEOUT = 5.0  # segundos maximos esperando lock


class AgentRole(str, Enum):
    SCOUT     = "scout"
    ARCHITECT = "architect"
    BUILDER   = "builder"
    PACKAGER  = "packager"
    GUARDIAN  = "guardian"
    AUDITOR   = "auditor"


class ProcessStatus(str, Enum):
    PENDING     = "pending"
    IN_PROGRESS = "in_progress"
    COMMITTED   = "committed"      # Builder entrego, esperando Packager
    PACKAGED    = "packaged"       # Packager entrego, esperando Guardian
    CERTIFIED   = "certified"      # Guardian aprobo
    REVIEW      = "review"         # Requiere revision humana
    REJECTED    = "rejected"       # Guardian rechazo -- feedback a Builder
    RETRYING    = "retrying"       # Builder recibio feedback, reintentando
    COMPLETED   = "completed"      # Auditado y aprobado
    FAILED      = "failed"         # Fallo definitivo


# ============================================================
# SWARM STATE -- estructura de datos
# ============================================================

def _empty_state() -> dict:
    return {
        "version":      "1.0",
        "updated_at":   _now(),
        "processes":    {},   # process_id -> ProcessRecord
        "agents":       {},   # agent_role -> AgentRecord
        "metrics": {
            "total_processed":   0,
            "total_certified":   0,
            "total_rejected":    0,
            "total_retried":     0,
            "avg_cycle_seconds": 0.0,
        }
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _process_record(
    process_id: str,
    status: ProcessStatus,
    agent: AgentRole,
    metadata: Optional[dict] = None
) -> dict:
    return {
        "process_id":   process_id,
        "status":       status.value,
        "current_agent": agent.value,
        "started_at":   _now(),
        "updated_at":   _now(),
        "history":      [],
        "metadata":     metadata or {},
        "retry_count":  0,
        "feedback":     [],
    }


# ============================================================
# FILE LOCK -- operaciones atomicas (Windows compatible)
# ============================================================

class _FileLock:
    """Lock de archivo compatible con Windows (no usa fcntl)."""

    def __init__(self, path: Path):
        self.lock_path = path.with_suffix(".lock")
        self._acquired = False

    def __enter__(self):
        deadline = time.time() + LOCK_TIMEOUT
        while time.time() < deadline:
            try:
                # Crear lock file exclusivo
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                time.sleep(0.05)
        raise TimeoutError(f"No se pudo adquirir lock en {LOCK_TIMEOUT}s")

    def __exit__(self, *args):
        if self._acquired and self.lock_path.exists():
            try:
                self.lock_path.unlink()
            except Exception:
                pass


# ============================================================
# SHIELD STATE -- API publica
# ============================================================

class ShieldState:
    """
    Gestor de estado compartido del Swarm.
    Thread-safe y multi-proceso via file locking.
    """

    def __init__(self, state_path: Path = SWARM_STATE_PATH):
        self.path = state_path

    def _load(self) -> dict:
        if not self.path.exists():
            return _empty_state()
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            log.warning("WARN swarm_state.json corrupto -- reiniciando")
            return _empty_state()

    def _save(self, state: dict):
        state["updated_at"] = _now()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    # -- Registro de proceso ------------------------------------------

    def register_process(
        self,
        process_id: str,
        agent: AgentRole,
        metadata: Optional[dict] = None
    ) -> dict:
        """Registra un proceso nuevo en el estado compartido."""
        with _FileLock(self.path):
            state = self._load()
            if process_id not in state["processes"]:
                state["processes"][process_id] = _process_record(
                    process_id, ProcessStatus.PENDING, agent, metadata
                )
                log.info(f"OK Proceso registrado: {process_id} ({agent.value})")
            self._save(state)
            return state["processes"][process_id]

    def update_status(
        self,
        process_id: str,
        status: ProcessStatus,
        agent: AgentRole,
        notes: str = ""
    ) -> bool:
        """Actualiza el estado de un proceso con historial completo."""
        with _FileLock(self.path):
            state = self._load()
            if process_id not in state["processes"]:
                log.warning(f"WARN Proceso no encontrado: {process_id}")
                return False

            record = state["processes"][process_id]
            prev_status = record["status"]

            # Historial
            record["history"].append({
                "from_status": prev_status,
                "to_status":   status.value,
                "agent":       agent.value,
                "timestamp":   _now(),
                "notes":       notes
            })

            record["status"]       = status.value
            record["current_agent"] = agent.value
            record["updated_at"]   = _now()

            # Metricas globales
            if status == ProcessStatus.CERTIFIED:
                state["metrics"]["total_certified"] += 1
            elif status == ProcessStatus.REJECTED:
                state["metrics"]["total_rejected"] += 1
            elif status == ProcessStatus.RETRYING:
                state["metrics"]["total_retried"] += 1
                record["retry_count"] += 1

            self._save(state)
            log.info(f"OK {process_id}: {prev_status} -> {status.value} ({agent.value})")
            return True

    def add_feedback(
        self,
        process_id: str,
        from_agent: AgentRole,
        to_agent: AgentRole,
        feedback: dict
    ) -> bool:
        """
        Canal de feedback directo entre agentes (Principio #4).
        Guardian -> Builder: motivo de rechazo + que hay que corregir.
        """
        with _FileLock(self.path):
            state = self._load()
            if process_id not in state["processes"]:
                return False

            state["processes"][process_id]["feedback"].append({
                "from_agent": from_agent.value,
                "to_agent":   to_agent.value,
                "timestamp":  _now(),
                "content":    feedback
            })
            self._save(state)
            log.info(f"OK Feedback: {from_agent.value} -> {to_agent.value} ({process_id})")
            return True

    def get_feedback_for(
        self,
        process_id: str,
        agent: AgentRole
    ) -> list:
        """Recupera feedback pendiente para un agente especifico."""
        state = self._load()
        if process_id not in state["processes"]:
            return []
        return [
            f for f in state["processes"][process_id].get("feedback", [])
            if f["to_agent"] == agent.value
        ]

    def get_process(self, process_id: str) -> Optional[dict]:
        """Estado actual de un proceso."""
        state = self._load()
        return state["processes"].get(process_id)

    def get_active_processes(self) -> list:
        """Procesos en curso (no completados ni fallidos)."""
        state = self._load()
        terminal = {ProcessStatus.COMPLETED.value, ProcessStatus.FAILED.value}
        return [
            p for p in state["processes"].values()
            if p["status"] not in terminal
        ]

    def get_retry_candidates(self, max_retries: int = 3) -> list:
        """Procesos rechazados con feedback pendiente y retries disponibles."""
        state = self._load()
        return [
            p for p in state["processes"].values()
            if p["status"] == ProcessStatus.REJECTED.value
            and p["retry_count"] < max_retries
            and len(p["feedback"]) > 0
        ]

    def register_agent(self, role: AgentRole, metadata: Optional[dict] = None):
        """Registra un worker activo en el estado compartido."""
        with _FileLock(self.path):
            state = self._load()
            state["agents"][role.value] = {
                "role":       role.value,
                "started_at": _now(),
                "last_seen":  _now(),
                "metadata":   metadata or {}
            }
            self._save(state)

    def heartbeat(self, role: AgentRole):
        """Actualiza el timestamp de un worker activo."""
        with _FileLock(self.path):
            state = self._load()
            if role.value in state["agents"]:
                state["agents"][role.value]["last_seen"] = _now()
                self._save(state)

    def get_summary(self) -> dict:
        """Resumen del estado global del Swarm."""
        state = self._load()
        processes = state["processes"]

        by_status = {}
        for p in processes.values():
            s = p["status"]
            by_status[s] = by_status.get(s, 0) + 1

        return {
            "total_processes":  len(processes),
            "by_status":        by_status,
            "active_agents":    list(state["agents"].keys()),
            "metrics":          state["metrics"],
            "updated_at":       state["updated_at"]
        }

    def print_summary(self):
        """Imprime resumen legible del estado del Swarm."""
        s = self.get_summary()
        print("\n" + "=" * 50)
        print("  CooperBench Shield -- Swarm State")
        print("=" * 50)
        print(f"  Total procesos  : {s['total_processes']}")
        for status, count in s["by_status"].items():
            print(f"  {status:<18}: {count}")
        print(f"  Agentes activos : {', '.join(s['active_agents']) or 'ninguno'}")
        print(f"  Certificados    : {s['metrics']['total_certified']}")
        print(f"  Rechazados      : {s['metrics']['total_rejected']}")
        print(f"  Retriados       : {s['metrics']['total_retried']}")
        print("=" * 50)


# Instancia global
shield = ShieldState()


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CooperBench Shield -- Swarm State")
    parser.add_argument("--status",  action="store_true", help="Ver estado del Swarm")
    parser.add_argument("--process", help="Ver estado de un proceso especifico")
    parser.add_argument("--retry",   action="store_true", help="Listar candidatos a retry")
    parser.add_argument("--reset",   action="store_true", help="Resetear estado (cuidado)")
    args = parser.parse_args()

    if args.status:
        shield.print_summary()

    elif args.process:
        p = shield.get_process(args.process)
        if p:
            print(json.dumps(p, indent=2, ensure_ascii=False))
        else:
            print(f"Proceso no encontrado: {args.process}")

    elif args.retry:
        candidates = shield.get_retry_candidates()
        print(f"Candidatos a retry: {len(candidates)}")
        for c in candidates:
            print(f"  {c['process_id']} -- retries: {c['retry_count']} -- feedback: {len(c['feedback'])}")

    elif args.reset:
        confirm = input("Resetear swarm_state.json? (si/no): ")
        if confirm.lower() == "si":
            shield._save(_empty_state())
            print("OK Estado reseteado")
        else:
            print("Cancelado")

    else:
        shield.print_summary()
