"""
AGENTIC ZERO — PIONEER TEAM
Agent 2: ARCHITECT
Role: Validate Scout processes and create sector variants
Input: ProcessEntry from Scout (JSON files from library)
Output: Validated processes + sector-specific variants

Architecture: API-first, queue-ready, zero-cost (Groq free tier)

Responsibilities:
- Validate Scout process accuracy and completeness
- Detect duplicate or overly similar processes
- Create sector variants (pharma != defense != food for same SCOR process)
- Flag processes requiring human review (regulated, critical)
- Enrich ontology with domain-specific knowledge
- Mark processes ready for Builder
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from loguru import logger
import litellm

load_dotenv()

# ── LOGGING ───────────────────────────────────────────────────────────────────
logger.add(
    "logs/architect_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


# ── MODELS ────────────────────────────────────────────────────────────────────
class ValidationResult(BaseModel):
    """Architect validation of a Scout process"""

    process_id: str
    is_valid: bool
    quality_score: float  # 0.0 - 1.0
    issues: list[str]  # List of detected issues
    suggestions: list[str]  # Improvement suggestions
    duplicate_of: Optional[str]  # process_id if duplicate detected
    requires_human_review: bool  # True for regulated/critical processes


class SectorVariant(BaseModel):
    """Sector-specific variant of a base process"""

    variant_id: str  # e.g. SCOR-P1.1-PHARMA
    base_process_id: str  # Original process_id
    sector: str  # pharma / defense / chemical / food / automotive
    name: str
    description: str
    sector_specific_inputs: list[str]
    sector_specific_outputs: list[str]
    sector_specific_kpis: list[str]
    regulatory_requirements: list[str]
    compliance_frameworks: list[str]  # GxP, AS9100, HACCP, etc.
    automation_complexity: str  # low / medium / high / very_high
    notes: str
    confidence: float


class ArchitectResult(BaseModel):
    """Complete output from Architect for a set of processes"""

    architect_timestamp: str
    framework: str
    processes_reviewed: int
    processes_valid: int
    processes_flagged: int
    variants_created: int
    validations: list[ValidationResult]
    variants: list[SectorVariant]
    ready_for_builder: list[str]  # process_ids ready for next stage
    needs_human_review: list[str]  # process_ids requiring human validation
    notes: str


# ── ARCHITECT CONFIGURATION ──────────────────────────────────────────────────
ARCHITECT_CONFIG = {
    "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
    "max_tokens": 6000,
    "temperature": 0.1,
    "rate_limit_rpm": 1,
    "rate_limit_rpd": 1400,
}

# ── SECTOR KNOWLEDGE BASE ─────────────────────────────────────────────────────
REGULATED_SECTORS = {
    "pharma": {
        "frameworks": [
            "GxP",
            "GMP",
            "GDP",
            "GCP",
            "ICH Q10",
            "GAMP 5",
            "21 CFR Part 11",
        ],
        "compliance_level": "very_high",
        "key_requirements": [
            "batch traceability",
            "audit trail mandatory",
            "electronic signatures",
            "validation documentation",
            "deviation management",
            "CAPA process",
        ],
        "automation_notes": "All automated decisions must be validated and documented per GxP",
    },
    "defense": {
        "frameworks": ["AS9100", "ARP4761", "MIL-STD-1388", "ITAR", "NATO STANAG"],
        "compliance_level": "very_high",
        "key_requirements": [
            "configuration management",
            "security classification",
            "export control",
            "first article inspection",
            "traceability to requirements",
        ],
        "automation_notes": "Classified processes require special handling and access control",
    },
    "chemical": {
        "frameworks": ["REACH", "HARPC", "ISO 14001", "ADR/RID", "OSHA PSM"],
        "compliance_level": "high",
        "key_requirements": [
            "hazardous material handling",
            "safety data sheets",
            "environmental reporting",
            "process safety management",
            "emergency response plans",
        ],
        "automation_notes": "Safety-critical decisions require human oversight",
    },
    "food": {
        "frameworks": ["HACCP", "FSMA", "BRC", "IFS", "ISO 22000", "FSSC 22000"],
        "compliance_level": "high",
        "key_requirements": [
            "critical control points",
            "allergen management",
            "cold chain integrity",
            "supplier verification",
            "recall procedures",
        ],
        "automation_notes": "Food safety decisions at CCPs require validated logic",
    },
    "automotive": {
        "frameworks": ["IATF 16949", "APQP", "PPAP", "FMEA", "MSA", "SPC"],
        "compliance_level": "medium",
        "key_requirements": [
            "customer-specific requirements",
            "production part approval",
            "statistical process control",
            "supplier development",
            "warranty management",
        ],
        "automation_notes": "PPAP processes require formal approval workflows",
    },
    "medtech": {
        "frameworks": [
            "ISO 13485",
            "MDR EU 2017/745",
            "IVDR EU 2017/746",
            "FDA 21 CFR 820",
        ],
        "compliance_level": "very_high",
        "key_requirements": [
            "design history file",
            "device master record",
            "complaint handling",
            "post-market surveillance",
            "UDI traceability",
        ],
        "automation_notes": "Any automated quality decision must be validated per ISO 13485",
    },
}

# ── QUALITY THRESHOLDS ────────────────────────────────────────────────────────
QUALITY_THRESHOLDS = {
    "min_inputs": 2,
    "min_outputs": 1,
    "min_kpis": 1,
    "min_description_length": 30,
    "min_confidence": 0.7,
    "similarity_threshold": 0.85,  # Flag as duplicate if >85% similar
}


# ── RATE LIMITER ──────────────────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, rpm: int = 3):
        self.rpm = rpm
        self.min_interval = 60.0 / rpm
        self.last_call = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.debug(f"Rate limiter: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        self.last_call = time.time()


rate_limiter = RateLimiter(rpm=ARCHITECT_CONFIG["rate_limit_rpm"])


# ── LLM CALLER ────────────────────────────────────────────────────────────────
def call_llm(prompt: str, expect_json: bool = True) -> str:
    rate_limiter.wait()
    try:
        response = litellm.completion(
            model=ARCHITECT_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=ARCHITECT_CONFIG["max_tokens"],
            temperature=ARCHITECT_CONFIG["temperature"],
            api_key=os.getenv("GROQ_API_KEY"),
        )
        content = response.choices[0].message.content.strip()
        if expect_json and content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        return content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


# ── PROMPTS ───────────────────────────────────────────────────────────────────
def build_validation_prompt(process: dict) -> str:
    return f"""You are a supply chain expert and AI governance specialist validating a process entry for an agentic automation library.

PROCESS TO VALIDATE:
{json.dumps(process, indent=2)}

Evaluate this process entry on these criteria:
1. Accuracy: Is the process correctly described based on its framework?
2. Completeness: Are inputs, outputs and KPIs sufficient?
3. Clarity: Is the description clear enough to build an AI agent?
4. Automation potential: Can this genuinely be automated with AI?
5. Regulatory flags: Are compliance requirements correctly identified?

Return ONLY a JSON object with this exact structure:
{{
  "is_valid": true/false,
  "quality_score": 0.0-1.0,
  "issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "duplicate_of": null,
  "requires_human_review": true/false
}}

Rules:
- is_valid = false only if the process is fundamentally wrong or useless
- quality_score < 0.7 means needs improvement before going to Builder
- requires_human_review = true for ANY regulated sector process (pharma, defense, chemical)
- Keep issues and suggestions concise and actionable"""


def build_variant_prompt(process: dict, sector: str) -> str:
    sector_info = REGULATED_SECTORS.get(sector, {})
    return f"""You are a supply chain expert specializing in {sector} operations.

BASE PROCESS:
{json.dumps(process, indent=2)}

Create a {sector.upper()} sector-specific variant of this process.

Sector context:
- Regulatory frameworks: {", ".join(sector_info.get("frameworks", []))}
- Key requirements: {", ".join(sector_info.get("key_requirements", []))}
- Automation notes: {sector_info.get("automation_notes", "")}

Return ONLY a JSON object with this structure:
{{
  "variant_id": "{process["process_id"]}-{sector.upper()}",
  "base_process_id": "{process["process_id"]}",
  "sector": "{sector}",
  "name": "sector-specific process name",
  "description": "how this process works specifically in {sector}",
  "sector_specific_inputs": ["input1", "input2"],
  "sector_specific_outputs": ["output1", "output2"],
  "sector_specific_kpis": ["kpi1", "kpi2"],
  "regulatory_requirements": ["requirement1", "requirement2"],
  "compliance_frameworks": ["framework1", "framework2"],
  "automation_complexity": "low/medium/high/very_high",
  "notes": "important notes for AI agent implementation",
  "confidence": 0.0-1.0
}}

Be specific and accurate. Focus on what makes {sector} different from generic implementation."""


# ── LOCAL VALIDATION (no LLM needed) ─────────────────────────────────────────
def local_validate(process: dict) -> dict:
    """Fast local validation without consuming tokens"""
    issues = []
    suggestions = []
    score = 1.0

    # Check required fields
    if (
        not process.get("description")
        or len(process.get("description", ""))
        < QUALITY_THRESHOLDS["min_description_length"]
    ):
        issues.append("Description too short or missing")
        suggestions.append("Expand description to at least 30 characters")
        score -= 0.2

    if len(process.get("inputs", [])) < QUALITY_THRESHOLDS["min_inputs"]:
        issues.append(f"Too few inputs (minimum {QUALITY_THRESHOLDS['min_inputs']})")
        suggestions.append("Add more specific inputs")
        score -= 0.15

    if len(process.get("outputs", [])) < QUALITY_THRESHOLDS["min_outputs"]:
        issues.append("No outputs defined")
        suggestions.append("Define at least one output")
        score -= 0.2

    if len(process.get("kpis", [])) < QUALITY_THRESHOLDS["min_kpis"]:
        issues.append("No KPIs defined")
        suggestions.append("Add measurable KPIs for agent performance tracking")
        score -= 0.15

    if process.get("confidence", 0) < QUALITY_THRESHOLDS["min_confidence"]:
        issues.append(f"Low Scout confidence: {process.get('confidence', 0)}")
        suggestions.append("Review process accuracy before building agent")
        score -= 0.1

    # Check if regulated sector needs review
    regulated_keywords = ["pharma", "defense", "chemical", "medtech", "aerospace"]
    needs_review = any(
        kw in " ".join(process.get("sector_applicability", [])).lower()
        or kw in " ".join(process.get("compliance_flags", [])).lower()
        for kw in regulated_keywords
    )

    return {
        "local_valid": score >= 0.6,
        "local_score": max(0.0, score),
        "local_issues": issues,
        "local_suggestions": suggestions,
        "needs_regulated_review": needs_review,
    }


# ── LIBRARY LOADER ────────────────────────────────────────────────────────────
def load_processes_from_library(
    framework: str, domain: Optional[str] = None
) -> list[dict]:
    """Load Scout processes from library"""
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))

    if "scor" in framework.lower():
        processes_path = library_path / "scor" / "processes"
    elif "iso" in framework.lower():
        processes_path = library_path / "iso" / "processes"
    elif "bpmn" in framework.lower():
        processes_path = library_path / "bpmn" / "processes"
    else:
        processes_path = library_path / "sector_specific" / "processes"

    if not processes_path.exists():
        logger.error(f"Library path not found: {processes_path}")
        return []

    processes = []
    for json_file in sorted(processes_path.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            process = json.load(f)
            if domain is None or process.get("domain") == domain:
                processes.append(process)

    logger.info(f"Loaded {len(processes)} processes from library")
    return processes


# ── LIBRARY WRITER ────────────────────────────────────────────────────────────
def save_architect_results(result: ArchitectResult, framework: str):
    """Save Architect results to library"""
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))

    if "scor" in framework.lower():
        folder = library_path / "scor"
    elif "iso" in framework.lower():
        folder = library_path / "iso"
    else:
        folder = library_path / "sector_specific"

    folder.mkdir(parents=True, exist_ok=True)

    # Save full architect result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fw_clean = framework.lower().replace("-", "_")
    filename = folder / f"architect_{fw_clean}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(f"Architect result saved: {filename}")

    # Save variants as individual files
    if result.variants:
        variants_folder = folder / "variants"
        variants_folder.mkdir(exist_ok=True)

        for variant in result.variants:
            variant_file = variants_folder / f"{variant.variant_id}.json"
            with open(variant_file, "w", encoding="utf-8") as f:
                json.dump(variant.model_dump(), f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(result.variants)} variant files")

    # Save validation report
    validations_folder = folder / "validations"
    validations_folder.mkdir(exist_ok=True)

    for validation in result.validations:
        val_file = validations_folder / f"{validation.process_id}_validation.json"
        with open(val_file, "w", encoding="utf-8") as f:
            json.dump(validation.model_dump(), f, indent=2, ensure_ascii=False)

    return filename


# ── MAIN ARCHITECT FUNCTION ───────────────────────────────────────────────────
def architect_framework(
    framework: str,
    domain: Optional[str] = None,
    sectors: Optional[list[str]] = None,
    use_llm_validation: bool = True,
) -> ArchitectResult:
    """
    Main Architect function: validate Scout processes and create sector variants

    Args:
        framework: Framework name (SCOR, ISO_9001, etc.)
        domain: Specific domain to process (None = all)
        sectors: Sectors to create variants for (None = regulated sectors only)
        use_llm_validation: Use LLM for deep validation (False = local only, saves tokens)

    Returns:
        ArchitectResult with validations and variants
    """
    logger.info(
        f"Architect starting: {framework} | domain={domain} | sectors={sectors}"
    )

    # Load processes from library
    processes = load_processes_from_library(framework, domain)
    if not processes:
        logger.error(f"No processes found for {framework}")
        return None

    # Default sectors for variant creation
    if sectors is None:
        sectors = ["pharma", "defense", "chemical", "food"]

    validations = []
    variants = []
    ready_for_builder = []
    needs_human_review = []

    for i, process in enumerate(processes):
        pid = process.get("process_id", f"UNKNOWN-{i}")
        logger.info(f"Reviewing process {i + 1}/{len(processes)}: {pid}")

        # Step 1: Local validation (no tokens)
        local = local_validate(process)

        if use_llm_validation and local["local_valid"]:
            # Step 2: LLM deep validation (uses tokens)
            try:
                prompt = build_validation_prompt(process)
                response = call_llm(prompt, expect_json=True)
                llm_result = json.loads(response)

                validation = ValidationResult(
                    process_id=pid,
                    is_valid=llm_result.get("is_valid", local["local_valid"]),
                    quality_score=llm_result.get("quality_score", local["local_score"]),
                    issues=local["local_issues"] + llm_result.get("issues", []),
                    suggestions=local["local_suggestions"]
                    + llm_result.get("suggestions", []),
                    duplicate_of=llm_result.get("duplicate_of"),
                    requires_human_review=llm_result.get(
                        "requires_human_review", local["needs_regulated_review"]
                    ),
                )
            except Exception as e:
                logger.warning(f"LLM validation failed for {pid}, using local: {e}")
                validation = ValidationResult(
                    process_id=pid,
                    is_valid=local["local_valid"],
                    quality_score=local["local_score"],
                    issues=local["local_issues"],
                    suggestions=local["local_suggestions"],
                    duplicate_of=None,
                    requires_human_review=local["needs_regulated_review"],
                )
        else:
            # Local validation only
            validation = ValidationResult(
                process_id=pid,
                is_valid=local["local_valid"],
                quality_score=local["local_score"],
                issues=local["local_issues"],
                suggestions=local["local_suggestions"],
                duplicate_of=None,
                requires_human_review=local["needs_regulated_review"],
            )

        validations.append(validation)

        if validation.requires_human_review:
            needs_human_review.append(pid)
            logger.warning(f"Process {pid} flagged for human review")
        elif validation.is_valid and validation.quality_score >= 0.7:
            ready_for_builder.append(pid)

        # Step 3: Create sector variants for valid processes
        if validation.is_valid and validation.quality_score >= 0.7:
            for sector in sectors:
                # Only create variant if sector is relevant for this process
                sector_applicability = " ".join(
                    process.get("sector_applicability", [])
                ).lower()
                compliance_flags = " ".join(process.get("compliance_flags", [])).lower()
                is_relevant = (
                    sector in sector_applicability
                    or "all" in sector_applicability
                    or any(
                        kw in compliance_flags
                        for kw in [
                            sector,
                            REGULATED_SECTORS.get(sector, {})
                            .get("frameworks", [""])[0]
                            .lower(),
                        ]
                    )
                )

                if is_relevant:
                    try:
                        prompt = build_variant_prompt(process, sector)
                        response = call_llm(prompt, expect_json=True)
                        variant_data = json.loads(response)

                        variant = SectorVariant(
                            variant_id=variant_data.get(
                                "variant_id", f"{pid}-{sector.upper()}"
                            ),
                            base_process_id=pid,
                            sector=sector,
                            name=variant_data.get("name", process.get("name", "")),
                            description=variant_data.get("description", ""),
                            sector_specific_inputs=variant_data.get(
                                "sector_specific_inputs", []
                            ),
                            sector_specific_outputs=variant_data.get(
                                "sector_specific_outputs", []
                            ),
                            sector_specific_kpis=variant_data.get(
                                "sector_specific_kpis", []
                            ),
                            regulatory_requirements=variant_data.get(
                                "regulatory_requirements", []
                            ),
                            compliance_frameworks=variant_data.get(
                                "compliance_frameworks", []
                            ),
                            automation_complexity=variant_data.get(
                                "automation_complexity", "medium"
                            ),
                            notes=variant_data.get("notes", ""),
                            confidence=variant_data.get("confidence", 0.8),
                        )
                        variants.append(variant)
                        logger.success(f"Variant created: {variant.variant_id}")

                    except Exception as e:
                        logger.warning(
                            f"Variant creation failed for {pid}/{sector}: {e}"
                        )

    # Build result
    result = ArchitectResult(
        architect_timestamp=datetime.now().isoformat(),
        framework=framework,
        processes_reviewed=len(processes),
        processes_valid=len(ready_for_builder),
        processes_flagged=len(needs_human_review),
        variants_created=len(variants),
        validations=validations,
        variants=variants,
        ready_for_builder=ready_for_builder,
        needs_human_review=needs_human_review,
        notes=f"Architect review — Agentic Zero Pioneer Team",
    )

    # Save to library
    save_architect_results(result, framework)

    logger.success(
        f"Architect complete: {framework} | "
        f"{result.processes_valid} valid | "
        f"{result.processes_flagged} flagged | "
        f"{result.variants_created} variants"
    )

    return result


# ── CLI INTERFACE ─────────────────────────────────────────────────────────────
def run_architect(
    framework: str = "SCOR",
    domain: Optional[str] = None,
    sectors: Optional[list] = None,
    local_only: bool = False,
):
    """Run Architect from command line or as API"""
    logger.info("=" * 60)
    logger.info("AGENTIC ZERO — ARCHITECT AGENT")
    logger.info(f"Framework: {framework}")
    logger.info(f"Domain: {domain or 'ALL'}")
    logger.info(f"Sectors: {sectors or 'DEFAULT (pharma, defense, chemical, food)'}")
    logger.info(f"Mode: {'Local only' if local_only else 'LLM validation'}")
    logger.info(f"Model: {ARCHITECT_CONFIG['model']}")
    logger.info("=" * 60)

    result = architect_framework(
        framework=framework,
        domain=domain,
        sectors=sectors,
        use_llm_validation=not local_only,
    )

    if result:
        print(f"\n✅ Architect complete")
        print(f"   Framework: {result.framework}")
        print(f"   Processes reviewed: {result.processes_reviewed}")
        print(f"   Valid → Builder: {result.processes_valid}")
        print(f"   Flagged → Human review: {result.processes_flagged}")
        print(f"   Sector variants created: {result.variants_created}")
        print(f"   Saved to library: library/{framework.lower()}/")

        if result.needs_human_review:
            print(f"\n⚠️  Requires your review:")
            for pid in result.needs_human_review:
                print(f"   → {pid}")

    return result


if __name__ == "__main__":
    import sys

    framework = sys.argv[1] if len(sys.argv) > 1 else "SCOR"
    domain = sys.argv[2] if len(sys.argv) > 2 else None
    local_only = "--local" in sys.argv
    sectors = None

    # Parse optional sectors
    if "--sectors" in sys.argv:
        idx = sys.argv.index("--sectors")
        sectors = sys.argv[idx + 1].split(",")

    # Default: local-only validation first run to save tokens
    if framework == "SCOR" and not domain and not local_only:
        print("\n⚡ Tip: First run with --local to validate without consuming tokens")
        print("   Full LLM validation: python architect.py SCOR")
        print("   Local only:          python architect.py SCOR --local")
        print("   Specific domain:     python architect.py SCOR Plan")
        print(
            "   Custom sectors:      python architect.py SCOR --sectors pharma,defense\n"
        )

    run_architect(framework, domain, sectors, local_only)
