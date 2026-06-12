"""
AGENTIC ZERO -- Scout Comercial v1.0
scout_comercial.py -- Orquestador principal

Punto de entrada unico del Scout Comercial.
Lee submissions de Formspree, clasifica, genera propuesta
y prepara el package para Herald.

Flujo:
  Formspree submission
        |
  scout_comercial.py
        |
  classifier.py -> AL1/AL2/AL3/AL4
        |
  AL1/AL2 -> proposal_generator.py -> propuesta auto
  AL3/AL4 -> package manual review -> alerta Alberto
        |
  output/proposals/{proposal_id}.json
        |
  Herald (secuencia outreach)

Ubicacion: F:/agentic-zero/commercial/scout_comercial/scout_comercial.py
"""

import json
import os
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

# Paths
ROOT         = Path(os.getenv("AGENTIC_ZERO_ROOT", "F:/agentic-zero"))
COMMERCIAL   = ROOT / "commercial" / "scout_comercial"
PROPOSALS    = COMMERCIAL / "proposals"
INBOX        = COMMERCIAL / "inbox"
PROCESSED    = COMMERCIAL / "processed"

for d in [PROPOSALS, INBOX, PROCESSED]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCOUT] %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("scout")

# Importar modulos locales
sys.path.insert(0, str(COMMERCIAL))
from classifier import classify, ClassificationResult
from proposal_generator import generate_proposal

# Formspree config
FORMSPREE_FORM_ID = os.getenv("FORMSPREE_FORM_ID", "xlgkgapl")
FORMSPREE_API_KEY = os.getenv("FORMSPREE_API_KEY", "")
FORMSPREE_API_URL = f"https://formspree.io/api/0/forms/{FORMSPREE_FORM_ID}/submissions"


# ============================================================
# FORMSPREE READER
# ============================================================

def fetch_formspree_submissions(limit: int = 20) -> list:
    """
    Descarga las ultimas submissions de Formspree via API.
    Requiere FORMSPREE_API_KEY en .env (plan paid de Formspree).
    Fallback: lee desde inbox/ si no hay API key.
    """
    if not FORMSPREE_API_KEY:
        log.info("Sin FORMSPREE_API_KEY -- leyendo desde inbox/")
        return _read_inbox()

    try:
        response = httpx.get(
            FORMSPREE_API_URL,
            headers={
                "Authorization": f"Bearer {FORMSPREE_API_KEY}",
                "Accept":        "application/json"
            },
            params={"page_size": limit},
            timeout=15.0
        )
        response.raise_for_status()
        data = response.json()
        submissions = data.get("submissions", [])
        log.info(f"OK {len(submissions)} submissions descargadas de Formspree")
        return [_normalize_formspree(s) for s in submissions]

    except Exception as e:
        log.error(f"Error Formspree API: {e} -- fallback a inbox/")
        return _read_inbox()


def _normalize_formspree(raw: dict) -> dict:
    """Normaliza una submission de Formspree al formato interno."""
    data = raw.get("data", {}) if isinstance(raw.get("data"), dict) else raw
    return {
        "submission_id":   raw.get("id", raw.get("submission_id", "")),
        "submitted_at":    raw.get("created_at", raw.get("submitted_at", "")),
        "name":            data.get("name", ""),
        "company":         data.get("company", ""),
        "email":           data.get("email", ""),
        "role":            data.get("role", "Not specified"),
        "sector":          data.get("sector", "Not specified"),
        "erp":             data.get("erp", "Not specified"),
        "volume":          _parse_int(data.get("volume", 0)),
        "team_size":       _parse_int(data.get("team_size", 0)),
        "timing":          data.get("timing", ""),
        "areas":           data.get("areas", ""),
        "process_mapping": data.get("process_mapping", ""),
        "autonomy_level":  data.get("autonomy_level", ""),
        "notes":           data.get("notes", ""),
        "raw":             raw
    }


def _parse_int(value) -> int:
    try:
        return int(str(value).split()[0].replace(',', ''))
    except Exception:
        return 0


def _read_inbox() -> list:
    """Lee submissions guardadas manualmente en inbox/."""
    submissions = []
    for f in sorted(INBOX.glob("*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                raw = json.load(fh)
            submissions.append(_normalize_formspree(raw))
            log.info(f"OK Leido desde inbox: {f.name}")
        except Exception as e:
            log.error(f"Error leyendo {f.name}: {e}")
    return submissions


# ============================================================
# PROCESADOR PRINCIPAL
# ============================================================

class ScoutComercial:

    def __init__(self):
        self.processed_ids = self._load_processed_ids()

    def _load_processed_ids(self) -> set:
        """Carga IDs ya procesados para evitar duplicados."""
        ids_file = COMMERCIAL / "state" / "processed_ids.json"
        ids_file.parent.mkdir(exist_ok=True)
        if ids_file.exists():
            try:
                with open(ids_file, encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def _save_processed_id(self, submission_id: str):
        ids_file = COMMERCIAL / "state" / "processed_ids.json"
        self.processed_ids.add(submission_id)
        with open(ids_file, "w", encoding="utf-8") as f:
            json.dump(list(self.processed_ids), f)

    def process_submission(self, lead: dict) -> dict:
        """
        Procesa una submission:
        1. Clasifica AL1-AL4
        2. Genera propuesta o deriva a manual
        3. Guarda el package para Herald
        """
        submission_id = lead.get("submission_id", "")
        company = lead.get("company", "Unknown")

        log.info(f"=== Scout procesando: {company} ({submission_id}) ===")

        # Evitar duplicados
        if submission_id and submission_id in self.processed_ids:
            log.info(f"Ya procesado: {submission_id} -- skip")
            return {"status": "already_processed", "submission_id": submission_id}

        # PASO 1 -- Clasificar
        classification = classify(
            erp=lead.get("erp", ""),
            volume=lead.get("volume", 0),
            process_mapping=lead.get("process_mapping", ""),
            sector=lead.get("sector", ""),
            team_size=lead.get("team_size", 0),
        )

        log.info(f"  Clasificacion: {classification.autonomy_level} -- {classification.recommended_tier}")
        log.info(f"  Procesos detectados: {classification.processes_detected}")
        log.info(f"  Auto-propuesta: {classification.auto_proposal}")

        # PASO 2 -- Generar propuesta o derivar
        proposal = generate_proposal(lead, classification)

        # PASO 3 -- Notificar si requiere revision humana
        if proposal.get("requires_human"):
            self._alert_human(proposal)

        # PASO 4 -- Marcar como procesado
        if submission_id:
            self._save_processed_id(submission_id)

        # PASO 5 -- Mover a processed si vino de inbox
        inbox_file = INBOX / f"{submission_id}.json"
        if inbox_file.exists():
            inbox_file.rename(PROCESSED / f"{submission_id}.json")

        log.info(f"OK {company}: {proposal['status']}")
        return proposal

    def process_all(self, limit: int = 20) -> list:
        """Descarga y procesa todas las submissions nuevas."""
        log.info("=== Scout Comercial v1.0 -- procesando submissions ===")
        submissions = fetch_formspree_submissions(limit)

        if not submissions:
            log.info("Sin submissions nuevas")
            return []

        results = []
        for lead in submissions:
            try:
                result = self.process_submission(lead)
                results.append(result)
            except Exception as e:
                log.error(f"Error procesando {lead.get('company')}: {e}")
                import traceback
                traceback.print_exc()

        self._print_summary(results)
        return results

    def process_manual(self, lead_data: dict) -> dict:
        """Procesa un lead introducido manualmente (testing o leads de otro canal)."""
        return self.process_submission(lead_data)

    def _alert_human(self, proposal: dict):
        """Genera alerta para revision humana (AL3/AL4)."""
        alert_path = COMMERCIAL / "state" / f"REVIEW_{proposal['proposal_id']}.json"
        alert = {
            "alert_type":    "HUMAN_REVIEW_REQUIRED",
            "proposal_id":   proposal["proposal_id"],
            "created_at":    datetime.now(timezone.utc).isoformat(),
            "company":       proposal["lead"].get("company"),
            "email":         proposal["lead"].get("email"),
            "al_level":      proposal["classification"]["autonomy_level"],
            "processes":     proposal["classification"].get("processes", []),
            "action":        proposal.get("human_action", ""),
            "urgency":       "normal"
        }
        with open(alert_path, "w", encoding="utf-8") as f:
            json.dump(alert, f, indent=2, ensure_ascii=False)
        log.warning(f"WARN Review requerido: {alert_path.name}")

    def _print_summary(self, results: list):
        auto   = [r for r in results if r.get("status") == "ready_for_herald"]
        manual = [r for r in results if r.get("status") == "requires_human_review"]
        skip   = [r for r in results if r.get("status") == "already_processed"]

        print(f"\n{'='*50}")
        print(f"  Scout Comercial v1.0 -- Resumen")
        print(f"{'='*50}")
        print(f"  Total procesados : {len(results)}")
        print(f"  Auto-propuesta   : {len(auto)}  (AL1/AL2 -> Herald)")
        print(f"  Revision manual  : {len(manual)} (AL3/AL4 -> Alberto)")
        print(f"  Ya procesados    : {len(skip)}")
        print(f"{'='*50}")
        if auto:
            print("  Propuestas listas para Herald:")
            for r in auto:
                c = r.get("classification", {})
                lead = r.get("lead", {})
                content = r.get("content", {})
                print(f"    {lead.get('company')} -- {c.get('autonomy_level')} "
                      f"-- EUR {c.get('setup_fee', 0):,.0f} setup")
        if manual:
            print("  Pendientes revision manual:")
            for r in manual:
                lead = r.get("lead", {})
                c = r.get("classification", {})
                print(f"    {lead.get('company')} -- {c.get('autonomy_level')} "
                      f"-- {lead.get('email')}")

    def get_pending_reviews(self) -> list:
        """Lista reviews pendientes para Alberto."""
        state_dir = COMMERCIAL / "state"
        reviews = []
        for f in state_dir.glob("REVIEW_*.json"):
            try:
                with open(f, encoding="utf-8") as fh:
                    reviews.append(json.load(fh))
            except Exception:
                pass
        return sorted(reviews, key=lambda x: x.get("created_at", ""))

    def get_proposals_ready(self) -> list:
        """Lista propuestas listas para Herald."""
        proposals = []
        for f in sorted(PROPOSALS.glob("*.json")):
            try:
                with open(f, encoding="utf-8") as fh:
                    p = json.load(fh)
                if p.get("status") == "ready_for_herald":
                    proposals.append(p)
            except Exception:
                pass
        return proposals


# ============================================================
# MANUAL LEAD INTAKE -- para leads de WhatsApp/telefono
# ============================================================

def intake_manual_lead(
    name: str,
    company: str,
    email: str,
    role: str,
    sector: str,
    erp: str,
    volume: int,
    team_size: int,
    process_mapping: str = "",
    timing: str = "1-3 months",
    notes: str = ""
) -> dict:
    """
    Procesa un lead captado fuera del formulario web.
    Uso: leads de WhatsApp, llamadas, referencias.
    """
    lead = {
        "submission_id":   f"MANUAL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "submitted_at":    datetime.now(timezone.utc).isoformat(),
        "name":            name,
        "company":         company,
        "email":           email,
        "role":            role,
        "sector":          sector,
        "erp":             erp,
        "volume":          volume,
        "team_size":       team_size,
        "timing":          timing,
        "process_mapping": process_mapping,
        "notes":           notes,
        "autonomy_level":  "",  # se calcula
        "source":          "manual"
    }
    scout = ScoutComercial()
    return scout.process_manual(lead)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scout Comercial v1.0 -- Agentic Zero")
    subparsers = parser.add_subparsers(dest="command")

    # Procesar todas las submissions
    subparsers.add_parser("run", help="Procesar todas las submissions nuevas de Formspree")

    # Lead manual
    manual_p = subparsers.add_parser("manual", help="Procesar un lead manual")
    manual_p.add_argument("--name",    required=True)
    manual_p.add_argument("--company", required=True)
    manual_p.add_argument("--email",   required=True)
    manual_p.add_argument("--role",    default="COO")
    manual_p.add_argument("--sector",  required=True)
    manual_p.add_argument("--erp",     required=True)
    manual_p.add_argument("--volume",  type=int, required=True)
    manual_p.add_argument("--team",    type=int, default=5)
    manual_p.add_argument("--mapping", default="")
    manual_p.add_argument("--timing",  default="1-3 months")
    manual_p.add_argument("--notes",   default="")

    # Ver estado
    subparsers.add_parser("status", help="Ver propuestas y reviews pendientes")

    args = parser.parse_args()
    scout = ScoutComercial()

    if args.command == "run":
        scout.process_all()

    elif args.command == "manual":
        result = intake_manual_lead(
            name=args.name, company=args.company, email=args.email,
            role=args.role, sector=args.sector, erp=args.erp,
            volume=args.volume, team_size=args.team,
            process_mapping=args.mapping, timing=args.timing, notes=args.notes
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "status":
        reviews   = scout.get_pending_reviews()
        proposals = scout.get_proposals_ready()
        print(f"\nReviews pendientes (AL3/AL4): {len(reviews)}")
        for r in reviews:
            print(f"  {r.get('company')} -- {r.get('al_level')} -- {r.get('email')}")
        print(f"\nPropuestas listas para Herald: {len(proposals)}")
        for p in proposals:
            lead = p.get('lead', {})
            c = p.get('classification', {})
            print(f"  {lead.get('company')} -- {c.get('autonomy_level')} -- {p.get('proposal_id')}")

    else:
        parser.print_help()
