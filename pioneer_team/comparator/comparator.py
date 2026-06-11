"""
AGENTIC ZERO - Multi-Model Comparador v1.0
==========================================
Lanza la misma especificacion de proceso a 3 LLMs en paralelo,
genera ontologia de consenso certificada y la anexa al pipeline.

Modelos:
  - xai/grok-3-mini       (xAI API - modelo principal)
  - gemini-1.5-flash      (Google Generative AI - free tier)
  - claude-haiku-4-5      (Anthropic API - $5 creditos)

Ubicacion: F:/agentic-zero/pioneer_team/comparator/comparator.py
Autor: Agentic Zero - Alberto Munoz Waissen
"""

import os
import json
import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# -- Imports LLM clients ------------------------------------------------------
import httpx
from google import genai as google_genai
from google.genai import types as genai_types
import anthropic

load_dotenv()

# -- Configuracion ------------------------------------------------------------
XAI_API_KEY        = os.getenv("XAI_API_KEY", "")
XAI_BASE_URL       = "https://api.x.ai/v1"
XAI_MODEL          = "grok-3-mini"

GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL       = "gemini-2.5-flash"

ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL    = "claude-haiku-4-5-20251001"

LIBRARY_PATH       = Path(os.getenv("LIBRARY_PATH", "F:/agentic-zero/library"))
COMPARATOR_LOG_DIR = LIBRARY_PATH / "comparator_logs"
COMPARATOR_LOG_DIR.mkdir(parents=True, exist_ok=True)

RATE_LIMIT_DELAY   = 2.0   # segundos entre llamadas (safe para todos los tiers)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [COMPARATOR] %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("comparator")


# ============================================================================
# PROMPT FACTORY
# ============================================================================

def build_comparison_prompt(process_spec: dict) -> str:
    """
    Genera el prompt estandar que reciben los 3 modelos.
    Mismo prompt -> comparacion justa.
    """
    process_id   = process_spec.get("process_id", "UNKNOWN")
    name         = process_spec.get("name", "")
    framework    = process_spec.get("framework", "BPMN+SCOR")
    sector       = process_spec.get("sector", "general")
    erp          = process_spec.get("erp", "SAP")
    description  = process_spec.get("description", "")

    return f"""You are an expert in business process automation for regulated supply chains.

Analyze the following business process and return a structured JSON object.
Return ONLY valid JSON. No markdown. No explanation. No preamble.

PROCESS SPECIFICATION:
  process_id:  {process_id}
  name:        {name}
  framework:   {framework}
  sector:      {sector}
  erp:         {erp}
  description: {description}

Return this exact JSON structure:
{{
  "process_id": "{process_id}",
  "model_name": "<your model identifier>",
  "steps": [
    {{
      "step_id": "S01",
      "name": "<step name>",
      "description": "<what happens>",
      "automation_potential": <0.0-1.0>,
      "actor": "agent|human|hybrid",
      "erp_touchpoints": ["<module>"],
      "data_inputs": ["<input>"],
      "data_outputs": ["<output>"]
    }}
  ],
  "automation_zones": {{
    "fully_automatable": ["<step_id>"],
    "hybrid": ["<step_id>"],
    "human_required": ["<step_id>"]
  }},
  "risk_flags": [
    {{
      "flag": "<risk name>",
      "severity": "low|medium|high",
      "mitigation": "<how to handle>"
    }}
  ],
  "integration_map": {{
    "erp_modules": ["<module>"],
    "api_type": "RFC/BAPI|REST|SOAP|GraphQL",
    "data_format": "<format>",
    "auth_method": "<method>"
  }},
  "compliance_notes": {{
    "eu_ai_act_risk": "minimal|limited|high",
    "gdpr_data_touched": true,
    "gdpr_lawful_basis": "<basis>",
    "iso_42001_applicable": true,
    "audit_trail_required": true
  }},
  "overall_automation_score": <0.0-1.0>,
  "confidence": <0.0-1.0>
}}"""


# ============================================================================
# LLM CALLERS - uno por modelo
# ============================================================================

async def call_xai(prompt: str) -> dict:
    """Llama a xAI grok-3-mini via API REST."""
    log.info("-> xAI grok-3-mini: enviando prompt...")
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": XAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4000
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{XAI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        result = _parse_json_safe(raw, "grok-3-mini")
        log.info("OK xAI grok-3-mini: respuesta recibida")
        return result


async def call_gemini(prompt: str) -> dict:
    """Llama a Gemini 1.5 Flash via nuevo SDK google.genai."""
    log.info("-> Gemini 1.5 Flash: enviando prompt...")
    await asyncio.sleep(RATE_LIMIT_DELAY)

    loop = asyncio.get_event_loop()
    def _sync_call():
        client = google_genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=4000,
                response_mime_type="application/json"
            )
        )
        return response.text

    raw = await loop.run_in_executor(None, _sync_call)
    result = _parse_json_safe(raw, "gemini-1.5-flash")
    result["model_name"] = "gemini-1.5-flash"
    log.info("OK Gemini 1.5 Flash: respuesta recibida")
    return result


async def call_claude_haiku(prompt: str) -> dict:
    """Llama a Claude Haiku via Anthropic SDK."""
    log.info("-> Claude Haiku: enviando prompt...")
    await asyncio.sleep(RATE_LIMIT_DELAY * 2)

    loop = asyncio.get_event_loop()
    def _sync_call():
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    raw = await loop.run_in_executor(None, _sync_call)
    result = _parse_json_safe(raw, "claude-haiku-4-5")
    result["model_name"] = "claude-haiku-4-5"
    log.info("OK Claude Haiku: respuesta recibida")
    return result


def _parse_json_safe(raw: str, model_name: str) -> dict:
    """Parsea JSON de forma segura, limpiando markdown si lo hay."""
    # Limpiar backticks de markdown
    clean = raw.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        clean = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])
    clean = clean.strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        log.warning(f"WARN {model_name}: JSON invalido - {e}. Retornando estructura vacia.")
        return {
            "model_name": model_name,
            "parse_error": str(e),
            "raw_response": raw[:500],
            "steps": [],
            "automation_zones": {},
            "risk_flags": [],
            "integration_map": {},
            "compliance_notes": {},
            "overall_automation_score": 0.0,
            "confidence": 0.0
        }


# ============================================================================
# COMPARATOR - orquestador principal
# ============================================================================

class MultiModelComparator:

    def __init__(self):
        self._validate_api_keys()

    def _validate_api_keys(self):
        missing = []
        if not XAI_API_KEY:       missing.append("XAI_API_KEY")
        if not GEMINI_API_KEY:    missing.append("GEMINI_API_KEY")
        if not ANTHROPIC_API_KEY: missing.append("ANTHROPIC_API_KEY")
        if missing:
            log.warning(f"WARN API keys no configuradas: {', '.join(missing)}")
            log.warning("  El comparador operara con los modelos disponibles.")

    async def compare(self, process_spec: dict) -> dict:
        """
        Lanza los 3 modelos en paralelo y devuelve el resultado completo.
        Si un modelo falla, continua con los disponibles.
        """
        process_id = process_spec.get("process_id", "UNKNOWN")
        log.info(f"=== Multi-Model Comparador: {process_id} ===")
        start = time.time()

        prompt = build_comparison_prompt(process_spec)

        # Lanzar en paralelo - gather con return_exceptions para no romper si uno falla
        tasks = []
        model_names = []

        if XAI_API_KEY:
            tasks.append(call_xai(prompt))
            model_names.append("grok-3-mini")

        if GEMINI_API_KEY:
            tasks.append(call_gemini(prompt))
            model_names.append("gemini-1.5-flash")

        if ANTHROPIC_API_KEY:
            tasks.append(call_claude_haiku(prompt))
            model_names.append("claude-haiku-4-5")

        if not tasks:
            raise RuntimeError("No hay API keys configuradas. El comparador requiere al menos 1 modelo.")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separar exitos de errores
        model_outputs = {}
        errors = {}
        for name, result in zip(model_names, results):
            if isinstance(result, Exception):
                log.error(f"FAIL {name}: error - {result}")
                errors[name] = str(result)
            else:
                model_outputs[name] = result

        elapsed = round(time.time() - start, 2)
        log.info(f"OK Modelos completados: {len(model_outputs)}/{len(tasks)} en {elapsed}s")

        return {
            "process_id": process_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": elapsed,
            "models_queried": model_names,
            "models_succeeded": list(model_outputs.keys()),
            "models_failed": errors,
            "model_outputs": model_outputs
        }

    def run(self, process_spec: dict) -> dict:
        """Punto de entrada sincrono para integracion con pipeline existente."""
        return asyncio.run(self.compare(process_spec))

    def run_and_save(self, process_spec: dict) -> dict:
        """
        Ejecuta el comparador, guarda el log y devuelve el resultado completo
        listo para pasar al consensus_engine.
        """
        result = self.run(process_spec)
        process_id = process_spec.get("process_id", "UNKNOWN")

        # Guardar log completo
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_path = COMPARATOR_LOG_DIR / f"{process_id}_comparator_{ts}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        log.info(f"OK Log guardado: {log_path}")
        return result


# ============================================================================
# CLI - uso directo
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero Multi-Model Comparador")
    parser.add_argument("process_id", help="ID del proceso (ej. BPMN-OTC-001)")
    parser.add_argument("--name", default="", help="Nombre del proceso")
    parser.add_argument("--framework", default="BPMN+SCOR", help="Framework")
    parser.add_argument("--sector", default="distribution", help="Sector")
    parser.add_argument("--erp", default="SAP ECC + HANA", help="ERP del cliente")
    parser.add_argument("--description", default="", help="Descripcion adicional")
    args = parser.parse_args()

    spec = {
        "process_id":  args.process_id,
        "name":        args.name or args.process_id,
        "framework":   args.framework,
        "sector":      args.sector,
        "erp":         args.erp,
        "description": args.description
    }

    comparator = MultiModelComparator()
    result = comparator.run_and_save(spec)

    print(f"\n{'='*60}")
    print(f"  Modelos consultados : {result['models_queried']}")
    print(f"  Modelos exitosos    : {result['models_succeeded']}")
    print(f"  Tiempo              : {result['elapsed_seconds']}s")
    if result['models_failed']:
        print(f"  Errores             : {result['models_failed']}")
    print(f"{'='*60}")
    print("  Pasando a consensus_engine...")

