"""
AGENTIC ZERO -- Scout Comercial v1.0
proposal_generator.py -- Generador de propuestas AL1/AL2

Genera propuestas comerciales personalizadas para leads AL1 y AL2
usando los datos del audit y la biblioteca de procesos certificados.
AL3/AL4 se derivan a revision humana.

Usa xAI grok-3-mini para personalizar el contenido de la propuesta.

Ubicacion: F:/agentic-zero/commercial/scout_comercial/proposal_generator.py
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import httpx
from dotenv import load_dotenv
from classifier import ClassificationResult

load_dotenv()

log = logging.getLogger("scout.proposal")

XAI_API_KEY  = os.getenv("XAI_API_KEY", "")
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_MODEL    = "grok-3-mini"

ROOT          = Path(os.getenv("AGENTIC_ZERO_ROOT", "F:/agentic-zero"))
LIBRARY_PATH  = Path(os.getenv("LIBRARY_PATH", "F:/agentic-zero/library"))
PROPOSALS_DIR = ROOT / "commercial" / "scout_comercial" / "proposals"
PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_process_package(process_id: str) -> Optional[dict]:
    """Carga el package de un proceso de biblioteca si existe."""
    for subdir in ["scor", "bpmn", "iso", "sector_specific", "frameworks"]:
        path = LIBRARY_PATH / subdir / "packages" / f"{process_id}_package.json"
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return None


def _build_proposal_prompt(lead: dict, classification: ClassificationResult) -> str:
    """Construye el prompt para generar la propuesta personalizada."""

    # Cargar info de procesos detectados
    process_info = []
    for pid in classification.processes_detected[:3]:  # max 3 para no saturar
        pkg = _load_process_package(pid)
        if pkg:
            process_info.append({
                "id":    pid,
                "name":  pkg.get("agent_name", pid),
                "score": pkg.get("overall_score", 0),
                "automation": pkg.get("automation_potential", 0.8)
            })

    # ROI estimado basado en team_size y volumen
    team_size   = lead.get("team_size", 5)
    volume      = lead.get("volume", 50)
    hourly_cost = 25  # EUR/hora promedio operaciones supply chain
    hours_saved = min(team_size * 4, 20)  # horas/semana ahorradas estimadas
    annual_savings = hours_saved * 52 * hourly_cost
    roi_ratio   = round(annual_savings / (classification.setup_fee + classification.monthly_fee * 12), 1)
    payback_months = round((classification.setup_fee + classification.monthly_fee) / (annual_savings / 12), 1)

    return f"""You are Agentic Zero's commercial AI. Generate a personalized commercial proposal in JSON.

LEAD DATA:
  Name:           {lead.get('name', '')}
  Company:        {lead.get('company', '')}
  Role:           {lead.get('role', '')}
  Sector:         {lead.get('sector', '')}
  ERP:            {lead.get('erp', '')}
  Volume:         {volume} orders/day
  Team size:      {team_size} people
  Timing:         {lead.get('timing', '')}

CLASSIFICATION:
  Level:          {classification.autonomy_level}
  Tier:           {classification.recommended_tier}
  Processes:      {classification.processes_detected}
  Cluster:        {classification.cluster_detected}

PRICING:
  Setup fee:      EUR {classification.setup_fee:,.0f}
  Monthly:        EUR {classification.monthly_fee:,.0f}/month
  Annual:         EUR {classification.annual_fee:,.0f}/year

ROI ESTIMATE:
  Annual savings: EUR {annual_savings:,.0f}
  ROI ratio:      {roi_ratio}x
  Payback:        {payback_months} months

CERTIFIED PROCESSES IN LIBRARY:
{json.dumps(process_info, indent=2)}

Generate a JSON proposal with this exact structure:
{{
  "executive_summary": "2-3 sentences personalized to their sector and ERP",
  "pain_points_addressed": ["specific pain point 1", "specific pain point 2", "specific pain point 3"],
  "solution_description": "1 paragraph describing exactly what the agent will do for their specific process",
  "roi_narrative": "1 paragraph explaining the ROI in their specific context (sector, volume, team)",
  "key_differentiators": ["differentiator 1", "differentiator 2", "differentiator 3"],
  "implementation_steps": [
    {{"step": 1, "title": "step title", "duration": "X days", "description": "what happens"}},
    {{"step": 2, "title": "step title", "duration": "X days", "description": "what happens"}},
    {{"step": 3, "title": "step title", "duration": "X days", "description": "what happens"}}
  ],
  "subject_line": "email subject line for the outreach",
  "opening_hook": "first sentence of the outreach email, personalized to their situation"
}}

Return ONLY valid JSON. No markdown. No explanation."""


def generate_proposal(lead: dict, classification: ClassificationResult) -> dict:
    """
    Genera una propuesta comercial personalizada usando xAI.

    Args:
        lead:           datos del formulario Formspree
        classification: resultado del clasificador AL1-AL4

    Returns:
        dict con la propuesta completa lista para usar en Herald
    """
    if not classification.auto_proposal:
        log.info(f"AL3/AL4 detectado -- propuesta manual requerida para {lead.get('company')}")
        return _manual_review_package(lead, classification)

    log.info(f"Generando propuesta {classification.autonomy_level} para {lead.get('company')}")

    prompt = _build_proposal_prompt(lead, classification)

    try:
        response = httpx.post(
            f"{XAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {XAI_API_KEY}",
                "Content-Type":  "application/json"
            },
            json={
                "model":       XAI_MODEL,
                "messages":    [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens":  1500
            },
            timeout=30.0
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]

        # Limpiar markdown si lo hay
        clean = raw.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

        proposal_content = json.loads(clean.strip())
        log.info(f"OK Propuesta generada para {lead.get('company')}")

    except Exception as e:
        log.error(f"Error generando propuesta con xAI: {e}")
        proposal_content = _fallback_proposal(lead, classification)

    # Package completo
    proposal = {
        "proposal_id":    f"AZ-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "generated_at":   _now(),
        "lead":           lead,
        "classification": {
            "autonomy_level":   classification.autonomy_level,
            "recommended_tier": classification.recommended_tier,
            "deploy_time":      classification.deploy_time,
            "setup_fee":        classification.setup_fee,
            "monthly_fee":      classification.monthly_fee,
            "annual_fee":       classification.annual_fee,
            "processes":        classification.processes_detected,
            "cluster":          classification.cluster_detected,
            "rationale":        classification.rationale,
        },
        "content":        proposal_content,
        "status":         "ready_for_herald",
        "requires_human": False,
    }

    # Guardar propuesta
    company_slug = lead.get('company', 'unknown').lower().replace(' ', '_')[:20]
    filename = f"{proposal['proposal_id']}_{company_slug}.json"
    with open(PROPOSALS_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(proposal, f, indent=2, ensure_ascii=False)

    log.info(f"OK Propuesta guardada: {filename}")
    return proposal


def _manual_review_package(lead: dict, classification: ClassificationResult) -> dict:
    """Package para leads AL3/AL4 que requieren revision humana."""
    return {
        "proposal_id":    f"AZ-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "generated_at":   _now(),
        "lead":           lead,
        "classification": {
            "autonomy_level":   classification.autonomy_level,
            "recommended_tier": classification.recommended_tier,
            "rationale":        classification.rationale,
            "processes":        classification.processes_detected,
        },
        "content":        None,
        "status":         "requires_human_review",
        "requires_human": True,
        "human_action":   (
            f"Lead {classification.autonomy_level} de {lead.get('company')} "
            f"requiere evaluacion manual. "
            f"Sector: {lead.get('sector')} - ERP: {lead.get('erp')} - "
            f"Procesos: {classification.processes_detected}. "
            f"Preparar propuesta Enterprise personalizada."
        )
    }


def _fallback_proposal(lead: dict, classification: ClassificationResult) -> dict:
    """Propuesta de fallback si xAI no esta disponible."""
    company = lead.get('company', 'your company')
    sector  = lead.get('sector', 'your sector')
    erp     = lead.get('erp', 'your ERP')

    return {
        "executive_summary": (
            f"Agentic Zero can automate your core supply chain operations at {company}, "
            f"delivering certified AI agents integrated with {erp} in the {sector} sector. "
            f"Our {classification.recommended_tier} package includes a pre-certified agent "
            f"deployed in {classification.deploy_time}."
        ),
        "pain_points_addressed": [
            "Manual processing consuming team capacity",
            "Error rates in order/transaction handling",
            "Lack of real-time visibility and compliance documentation"
        ],
        "solution_description": (
            f"We deploy a certified autonomous agent that handles your end-to-end process "
            f"integrated directly with {erp}. The agent operates 24/7, logs every decision "
            f"for EU AI Act compliance, and delivers measurable ROI from day one."
        ),
        "roi_narrative": (
            f"Based on your declared volume and team size, we estimate significant "
            f"annual savings within the first year. Full ROI report delivered at 30, "
            f"60 and 90 days post-deployment."
        ),
        "key_differentiators": [
            "189+ pre-certified processes -- no build from scratch",
            "EU AI Act + ISO 42001 + GDPR compliance embedded",
            "ROI measured and documented at 30/60/90 days"
        ],
        "implementation_steps": [
            {"step": 1, "title": "Technical intake", "duration": "1 day",
             "description": "Collect ERP credentials and process specs"},
            {"step": 2, "title": "Agent build and certification", "duration": "3-5 days",
             "description": "Build, test and Guardian-certify the agent"},
            {"step": 3, "title": "Deploy and activate", "duration": "1-2 days",
             "description": "Deploy to your environment, validate and go live"}
        ],
        "subject_line": f"Your {classification.recommended_tier} agent for {company} -- ready in {classification.deploy_time}",
        "opening_hook": f"Hi, I noticed {company} is looking to automate supply chain operations in {sector}."
    }


# CLI
if __name__ == "__main__":
    import argparse
    from classifier import classify

    parser = argparse.ArgumentParser(description="Scout Comercial -- Proposal Generator")
    parser.add_argument("--company",  default="Test Company")
    parser.add_argument("--name",     default="Test User")
    parser.add_argument("--email",    default="test@test.com")
    parser.add_argument("--role",     default="COO")
    parser.add_argument("--sector",   default="distribution")
    parser.add_argument("--erp",      default="SAP ECC")
    parser.add_argument("--volume",   type=int, default=50)
    parser.add_argument("--team",     type=int, default=5)
    parser.add_argument("--mapping",  default="Order Management: Order Entry [BPMN-OTC-001]")
    args = parser.parse_args()

    lead = {
        "name":            args.name,
        "company":         args.company,
        "email":           args.email,
        "role":            args.role,
        "sector":          args.sector,
        "erp":             args.erp,
        "volume":          args.volume,
        "team_size":       args.team,
        "process_mapping": args.mapping,
        "timing":          "1-3 months",
    }

    classification = classify(args.erp, args.volume, args.mapping, args.sector)
    print(f"Clasificacion: {classification.autonomy_level} -- {classification.recommended_tier}")

    proposal = generate_proposal(lead, classification)
    print(f"\nPropuesta ID: {proposal['proposal_id']}")
    print(f"Status: {proposal['status']}")
    if proposal.get('content'):
        print(f"Subject: {proposal['content'].get('subject_line', '')}")
        print(f"Hook: {proposal['content'].get('opening_hook', '')}")
