"""
AGENTIC ZERO — PIONEER TEAM
Agent X: FUNCTIONAL TRANSLATOR
Role: Translate customer AUDIT inputs into a Functional Analysis Draft
Input: AUDIT ZERO JSON + Fast Track JSON + optional documentation text
Output:
  1) Functional Analysis Draft JSON
  2) Architect-compatible ProcessEntry JSON in library/sector_specific/processes

Design goal:
- Do NOT modify scout.py or architect.py.
- Do NOT break the existing Pioneer Team structure.
- Produce a process JSON compatible with architect.py local_validate().
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from loguru import logger

try:
    import litellm
except Exception:  # Allows local/offline deterministic mode
    litellm = None

load_dotenv()

# ── LOGGING ───────────────────────────────────────────────────────────────────
logger.add(
    "logs/functional_translator_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
FUNCTIONAL_TRANSLATOR_CONFIG = {
    "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
    "max_tokens": 6000,
    "temperature": 0.1,
    "library_path": os.getenv("LIBRARY_PATH", "library"),
    "output_path": os.getenv("FUNCTIONAL_ANALYSIS_PATH", "library/functional_analysis"),
}

# ── MODELS ────────────────────────────────────────────────────────────────────
class MissingInformation(BaseModel):
    field: str
    reason: str
    required_for: str
    severity: str = "medium"  # low / medium / high / critical

class BusinessContext(BaseModel):
    company: str = ""
    sector: str = ""
    erp: str = ""
    volume: str = ""
    team_size: str = ""
    documentation_score: float = 0.0
    recommended_route: str = ""

class ProcessContext(BaseModel):
    process_name: str = ""
    domains: list[str] = Field(default_factory=list)
    subprocesses: list[str] = Field(default_factory=list)
    frequency: str = ""
    criticality: str = ""
    trigger: str = ""
    end_condition: str = ""

class ProcedureStep(BaseModel):
    step_id: str
    name: str
    owner: str = ""
    system: str = ""
    input: list[str] = Field(default_factory=list)
    output: list[str] = Field(default_factory=list)
    business_rule: str = ""
    confidence: float = 0.5

class FunctionalAnalysisDraft(BaseModel):
    functional_analysis_id: str
    created_at: str
    source: str = "Functional Translator"
    business_context: BusinessContext
    process_context: ProcessContext
    procedure_overview: str = ""
    business_process_flow: list[ProcedureStep] = Field(default_factory=list)
    data_requirements: dict[str, list[str]] = Field(default_factory=dict)
    business_rules: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    systems: list[str] = Field(default_factory=list)
    autonomy_boundaries: dict[str, Any] = Field(default_factory=dict)
    kpis: list[str] = Field(default_factory=list)
    compliance_flags: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    missing_information: list[MissingInformation] = Field(default_factory=list)
    ready_for_architect: bool = False

# ── UTILITIES ─────────────────────────────────────────────────────────────────
def _safe_slug(value: str) -> str:
    value = (value or "process").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "process"

def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, dict):
        out: list[str] = []
        for v in value.values():
            out.extend(_as_list(v))
        return out
    if isinstance(value, str):
        if not value.strip():
            return []
        if "," in value and len(value) < 300:
            return [v.strip() for v in value.split(",") if v.strip()]
        return [value.strip()]
    return [str(value).strip()]

def load_json_file(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_text_file(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

# ── NORMALIZATION ─────────────────────────────────────────────────────────────
def normalize_audit_zero(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize different possible AUDIT ZERO payload shapes into a common dict."""
    return {
        "company": raw.get("company") or raw.get("Company") or raw.get("name", ""),
        "sector": raw.get("sector") or raw.get("industry") or "",
        "erp": raw.get("erp") or raw.get("system") or raw.get("core_system", ""),
        "volume": raw.get("volume") or raw.get("daily_volume") or "",
        "team_size": raw.get("team_size") or raw.get("fte") or "",
        "domains": _as_list(raw.get("domains") or raw.get("areas") or raw.get("selected_domains")),
        "subprocesses": _as_list(raw.get("subprocesses") or raw.get("subcats") or raw.get("selected_subprocesses")),
        "documentation_score": float(raw.get("documentation_score") or 0),
        "recommended_route": raw.get("recommended_route") or raw.get("recommended_path") or raw.get("route") or "",
        "process_detail": raw.get("process_detail") or raw.get("notes") or "",
        "business_rules": _as_list(raw.get("business_rules")),
        "critical_exceptions": _as_list(raw.get("critical_exceptions")),
        "data_used": _as_list(raw.get("data_used")),
        "systems_involved": _as_list(raw.get("systems_involved")),
    }

def normalize_fast_track(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize Fast Track payload into common fields."""
    return {
        "business_rules": _as_list(raw.get("business_rules")),
        "critical_exceptions": _as_list(raw.get("critical_exceptions")),
        "systems": _as_list(raw.get("systems")),
        "data_objects": _as_list(raw.get("data_objects")),
        "autonomy_boundaries": raw.get("autonomy_boundaries") or {},
    }

# ── DETERMINISTIC TRANSLATION ─────────────────────────────────────────────────
def deterministic_translate(
    audit_zero: dict[str, Any],
    fast_track: Optional[dict[str, Any]] = None,
    documentation_text: str = "",
) -> FunctionalAnalysisDraft:
    """Create a Functional Analysis Draft without LLM. Safe fallback and test mode."""
    az = normalize_audit_zero(audit_zero or {})
    ft = normalize_fast_track(fast_track or {})

    process_name = (
        (az["subprocesses"][0] if az["subprocesses"] else "")
        or (az["domains"][0] if az["domains"] else "")
        or "Customer Process"
    )

    business_rules = []
    business_rules.extend(az.get("business_rules", []))
    business_rules.extend(ft.get("business_rules", []))

    exceptions = []
    exceptions.extend(az.get("critical_exceptions", []))
    exceptions.extend(ft.get("critical_exceptions", []))

    systems = []
    systems.extend(az.get("systems_involved", []))
    systems.extend(ft.get("systems", []))
    systems = sorted(set(systems))

    data_objects = []
    data_objects.extend(az.get("data_used", []))
    data_objects.extend(ft.get("data_objects", []))
    data_objects = sorted(set(data_objects))

    steps: list[ProcedureStep] = []
    if az["subprocesses"]:
        for i, sub in enumerate(az["subprocesses"], start=1):
            steps.append(
                ProcedureStep(
                    step_id=f"STEP-{i:02d}",
                    name=sub,
                    system=az["erp"],
                    business_rule=business_rules[0] if business_rules else "",
                    confidence=0.55,
                )
            )
    elif documentation_text:
        rough_phases = re.split(r"\s*(?:→|->|\n\d+\.|\n-)\s*", documentation_text[:2000])
        rough_phases = [p.strip() for p in rough_phases if 5 <= len(p.strip()) <= 120][:10]
        for i, phase in enumerate(rough_phases, start=1):
            steps.append(ProcedureStep(step_id=f"STEP-{i:02d}", name=phase, system=az["erp"], confidence=0.45))

    missing: list[MissingInformation] = []
    if not az["domains"]:
        missing.append(MissingInformation(field="domains", reason="No process domain provided in AUDIT ZERO", required_for="process classification", severity="high"))
    if not steps:
        missing.append(MissingInformation(field="business_process_flow", reason="No subprocesses or usable process flow detected", required_for="procedure steps and blueprint generation", severity="critical"))
    if not systems:
        missing.append(MissingInformation(field="systems", reason="No systems involved were provided or inferred", required_for="integration design", severity="high"))
    if not data_objects:
        missing.append(MissingInformation(field="data_requirements", reason="No business data objects were provided or inferred", required_for="agent data model", severity="high"))
    if not business_rules:
        missing.append(MissingInformation(field="business_rules", reason="No explicit business rules provided", required_for="decision logic", severity="high"))
    if not exceptions:
        missing.append(MissingInformation(field="exceptions", reason="No exceptions provided", required_for="safe autonomous execution", severity="medium"))

    score_parts = [
        1 if az["domains"] else 0,
        1 if steps else 0,
        1 if systems else 0,
        1 if data_objects else 0,
        1 if business_rules else 0,
        1 if exceptions else 0,
        min(1.0, az["documentation_score"] / 100.0),
    ]
    confidence = round(sum(score_parts) / len(score_parts), 2)

    process_id = f"FA-{_safe_slug(az['company'])}-{_safe_slug(process_name)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return FunctionalAnalysisDraft(
        functional_analysis_id=process_id,
        created_at=datetime.now().isoformat(),
        business_context=BusinessContext(
            company=az["company"],
            sector=az["sector"],
            erp=az["erp"],
            volume=str(az["volume"]),
            team_size=str(az["team_size"]),
            documentation_score=az["documentation_score"],
            recommended_route=az["recommended_route"],
        ),
        process_context=ProcessContext(
            process_name=process_name,
            domains=az["domains"],
            subprocesses=az["subprocesses"],
        ),
        procedure_overview=az.get("process_detail", "") or f"Functional analysis draft for {process_name}",
        business_process_flow=steps,
        data_requirements={"input_objects": data_objects, "output_objects": [], "documents": []},
        business_rules=sorted(set(business_rules)),
        exceptions=sorted(set(exceptions)),
        systems=systems,
        autonomy_boundaries=ft.get("autonomy_boundaries", {}),
        kpis=[],
        compliance_flags=[],
        confidence=confidence,
        missing_information=missing,
        ready_for_architect=confidence >= 0.55 and not any(m.severity == "critical" for m in missing),
    )

# ── LLM TRANSLATION ───────────────────────────────────────────────────────────
def build_functional_translation_prompt(audit_zero: dict[str, Any], fast_track: Optional[dict[str, Any]], documentation_text: str) -> str:
    return f"""You are the Functional Translator Agent for Agentic Zero -- an expert business
process analyst who specializes in extracting EVERY operational detail from raw, unstructured
customer descriptions and converting them into a precise Functional Analysis.

Your single most important skill: you NEVER summarize away detail. Customers describe their
process in dense, run-on sentences mixing systems, transaction codes, thresholds and exceptions.
A mediocre analyst produces 2-3 generic steps. YOU produce one step per distinct operation,
because that is what the Agent Developer needs to build a real autonomous agent -- not a vague
description of one.

EXTRACTION METHOD (follow this order, do not skip steps):
1. Read every field of AUDIT ZERO INPUT, especially free-text fields like "notes" or
   "process_mapping" -- these usually contain the highest-density information, written by the
   customer in their own words, often as a single run-on paragraph.
2. Underline (mentally) every: system name, module (SD/MM/FI/WM...), transaction code
   (FD32, VK11, VL01N, VF01...), API/connector mentioned, numeric threshold (percentages, days,
   currency amounts, volumes), order/document type code, and named contact/role.
3. Each transaction code or distinct system operation found becomes its OWN step in
   business_process_flow. Do NOT merge "credit check" and "price validation" into one step just
   because they appear in the same sentence -- if the customer named two different SAP
   transactions, that is two steps.
4. Each numeric threshold or conditional ("if X exceeds Y, then Z") becomes an entry in
   business_rules AND drives the "business_rule" field of the relevant step -- never leave a
   stated threshold out.
5. Order/document type codes (e.g. ZEST, ZURG, ZINT, ZDEV) become part of process_context and
   inform step-level logic, not just a passing mention.
6. Only after steps 1-5 are exhausted, fill domains, kpis, compliance_flags and the rest.

EXAMPLE OF THE EXPECTED GRANULARITY (illustrative -- a transport company mentioning SAP FD32
credit checks, VK11 pricing with tolerance, and TMS capacity in their notes):

WRONG (too coarse -- do NOT produce this):
{{"business_process_flow": [
  {{"step_id": "STEP-01", "name": "Order Management and Validation", "system": "SAP",
    "business_rule": "Validate orders against business rules", "confidence": 0.6}}
]}}

RIGHT (one step per distinct operation found in the text):
{{"business_process_flow": [
  {{"step_id": "STEP-01", "name": "Order Received", "system": "SAP SD -- VBAK/VBAP",
    "business_rule": "Classify by order type code", "confidence": 0.9}},
  {{"step_id": "STEP-02", "name": "Credit Check", "system": "SAP FI -- FD32",
    "business_rule": "Block if overdue invoices exceed the stated threshold", "confidence": 0.9}},
  {{"step_id": "STEP-03", "name": "Price Validation", "system": "SAP SD -- VK11",
    "business_rule": "Block if quoted price deviates beyond the stated tolerance", "confidence": 0.9}},
  {{"step_id": "STEP-04", "name": "Capacity Check", "system": "TMS external API",
    "business_rule": "Check available capacity for the requested route/date", "confidence": 0.85}}
]}}
Notice: 4 distinct steps from one dense paragraph, each tied to a specific system/transaction,
each carrying its own concrete business_rule with the numeric threshold preserved.

Do NOT invent facts that are not stated or reasonably inferable. If something is genuinely
absent, add it to missing_information instead of guessing -- but do not use missing_information
as an excuse to skip detail that IS present in the text.

AUDIT ZERO INPUT:
{json.dumps(audit_zero, indent=2, ensure_ascii=False)}

FAST TRACK INPUT:
{json.dumps(fast_track or {}, indent=2, ensure_ascii=False)}

DOCUMENTATION TEXT / PROCESS MAP EXTRACTION:
{documentation_text[:12000]}

Return ONLY a valid JSON object with this exact structure:
{{
  "business_context": {{"company": "", "sector": "", "erp": "", "volume": "", "team_size": "", "documentation_score": 0, "recommended_route": ""}},
  "process_context": {{"process_name": "", "domains": [], "subprocesses": [], "frequency": "", "criticality": "", "trigger": "", "end_condition": ""}},
  "procedure_overview": "",
  "business_process_flow": [{{"step_id": "STEP-01", "name": "", "owner": "", "system": "", "input": [], "output": [], "business_rule": "", "confidence": 0.0}}],
  "data_requirements": {{"input_objects": [], "output_objects": [], "documents": []}},
  "business_rules": [],
  "exceptions": [],
  "systems": [],
  "autonomy_boundaries": {{}},
  "kpis": [],
  "compliance_flags": [],
  "confidence": 0.0,
  "missing_information": [{{"field": "", "reason": "", "required_for": "", "severity": "low/medium/high/critical"}}],
  "ready_for_architect": true
}}

Rules:
- The output is internal and must be useful for architect.py.
- One step per distinct system operation/transaction code found in the text -- never collapse
  multiple named operations into a single generic step.
- Every numeric threshold mentioned in the source text (percentages, days, amounts) must appear
  verbatim inside the business_rule of its corresponding step, not be paraphrased away.
- Mark critical missing information when Agent Developer could not safely build automation.
- Confidence must reflect completeness and inference quality -- a translation that ignored
  available detail in favor of brevity should score LOWER, not higher.
"""

def call_llm(prompt: str) -> str:
    if litellm is None:
        raise RuntimeError("litellm not installed. Use deterministic mode.")
    response = litellm.completion(
        model=FUNCTIONAL_TRANSLATOR_CONFIG["model"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=FUNCTIONAL_TRANSLATOR_CONFIG["max_tokens"],
        temperature=FUNCTIONAL_TRANSLATOR_CONFIG["temperature"],
        api_key=os.getenv("GROQ_API_KEY"),
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    return content

def llm_translate(audit_zero: dict[str, Any], fast_track: Optional[dict[str, Any]] = None, documentation_text: str = "") -> FunctionalAnalysisDraft:
    prompt = build_functional_translation_prompt(audit_zero, fast_track, documentation_text)
    raw = call_llm(prompt)
    parsed = json.loads(raw)
    fa_id = f"FA-{_safe_slug(parsed.get('business_context', {}).get('company', 'company'))}-{_safe_slug(parsed.get('process_context', {}).get('process_name', 'process'))}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return FunctionalAnalysisDraft(functional_analysis_id=fa_id, created_at=datetime.now().isoformat(), **parsed)

# ── ARCHITECT COMPATIBILITY ───────────────────────────────────────────────────
def to_architect_process_entry(analysis: FunctionalAnalysisDraft) -> dict[str, Any]:
    """Convert Functional Analysis into architect.py-compatible ProcessEntry dict."""
    process_name = analysis.process_context.process_name or "Customer Process"
    domain = analysis.process_context.domains[0] if analysis.process_context.domains else "Customer Process"

    inputs = analysis.data_requirements.get("input_objects", [])
    outputs = analysis.data_requirements.get("output_objects", [])
    if not outputs and analysis.business_process_flow:
        outputs = [out for step in analysis.business_process_flow for out in step.output if out]

    description = analysis.procedure_overview or f"Customer-specific process: {process_name}"
    if len(description) < 30:
        description = f"{description}. Functional analysis generated from AUDIT ZERO and customer process documentation."

    compliance_flags = analysis.compliance_flags[:]
    if analysis.business_context.sector.lower() in ["pharma", "defense", "chemical", "medtech", "food"]:
        compliance_flags.append(f"Review required for {analysis.business_context.sector}")

    return {
        "process_id": analysis.functional_analysis_id,
        "name": process_name,
        "framework": "CUSTOMER_FUNCTIONAL_ANALYSIS",
        "domain": domain,
        "level": "L3" if analysis.confidence >= 0.7 else "L4",
        "description": description,
        "inputs": inputs or ["customer provided process input"],
        "outputs": outputs or ["functional process output"],
        "kpis": analysis.kpis or ["cycle time", "error rate", "automation rate"],
        "related_processes": analysis.process_context.subprocesses,
        "sector_applicability": [analysis.business_context.sector] if analysis.business_context.sector else ["all"],
        "compliance_flags": sorted(set(compliance_flags)),
        "source": "Functional Translator — AUDIT ZERO",
        "confidence": analysis.confidence,
    }

# ── WRITERS ───────────────────────────────────────────────────────────────────
def save_functional_analysis(analysis: FunctionalAnalysisDraft) -> Path:
    out_dir = Path(FUNCTIONAL_TRANSLATOR_CONFIG["output_path"])
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / f"{analysis.functional_analysis_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(analysis.model_dump(), f, indent=2, ensure_ascii=False)
    logger.info(f"Functional Analysis saved: {filename}")
    return filename

def save_for_architect(analysis: FunctionalAnalysisDraft) -> Path:
    library_path = Path(FUNCTIONAL_TRANSLATOR_CONFIG["library_path"])
    processes_dir = library_path / "sector_specific" / "processes"
    processes_dir.mkdir(parents=True, exist_ok=True)
    process_entry = to_architect_process_entry(analysis)
    filename = processes_dir / f"{process_entry['process_id']}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(process_entry, f, indent=2, ensure_ascii=False)
    logger.info(f"Architect-compatible process saved: {filename}")
    return filename

# ── MAIN API ──────────────────────────────────────────────────────────────────
def translate_to_functional_analysis(
    audit_zero: dict[str, Any],
    fast_track: Optional[dict[str, Any]] = None,
    documentation_text: str = "",
    use_llm: bool = False,
    export_for_architect: bool = True,
) -> FunctionalAnalysisDraft:
    logger.info("Functional Translator starting")
    if use_llm:
        try:
            analysis = llm_translate(audit_zero, fast_track, documentation_text)
        except Exception as e:
            logger.warning(f"LLM translation failed, falling back deterministic: {e}")
            analysis = deterministic_translate(audit_zero, fast_track, documentation_text)
    else:
        analysis = deterministic_translate(audit_zero, fast_track, documentation_text)

    save_functional_analysis(analysis)
    if export_for_architect:
        save_for_architect(analysis)

    logger.success(f"Functional Translator complete | confidence={analysis.confidence} | ready_for_architect={analysis.ready_for_architect}")
    return analysis

# ── CLI ───────────────────────────────────────────────────────────────────────
def run_functional_translator(audit_path: str, fast_track_path: Optional[str] = None, documentation_path: Optional[str] = None, use_llm: bool = False):
    audit_zero = load_json_file(audit_path)
    fast_track = load_json_file(fast_track_path) if fast_track_path else None
    documentation_text = load_text_file(documentation_path) if documentation_path else ""
    result = translate_to_functional_analysis(audit_zero, fast_track, documentation_text, use_llm, export_for_architect=True)

    print("\n✅ Functional Translator complete")
    print(f"   Functional Analysis ID: {result.functional_analysis_id}")
    print(f"   Confidence: {result.confidence}")
    print(f"   Ready for Architect: {result.ready_for_architect}")
    if result.missing_information:
        print("\n⚠️ Missing information:")
        for item in result.missing_information:
            print(f"   → {item.field}: {item.reason} [{item.severity}]")
    print("\nNext:")
    print("   python architect.py CUSTOMER --local")
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agentic Zero — Functional Translator")
    parser.add_argument("--audit", required=True, help="Path to AUDIT ZERO JSON")
    parser.add_argument("--fast-track", default=None, help="Path to Fast Track JSON")
    parser.add_argument("--documentation", default=None, help="Path to extracted documentation text")
    parser.add_argument("--llm", action="store_true", help="Use LLM translation instead of deterministic mode")
    args = parser.parse_args()
    run_functional_translator(args.audit, args.fast_track, args.documentation, args.llm)
