"""
AGENTIC ZERO — PIONEER TEAM
Agent 1: SCOUT
Role: Research & mapping of process frameworks
Input: Framework name (SCOR, ISO, BPMN, etc.)
Output: Structured process map ready for Architect

Architecture: API-first, queue-ready, zero-cost (Gemini Flash)
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
    "logs/scout_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


# ── MODELS ────────────────────────────────────────────────────────────────────
class ProcessEntry(BaseModel):
    """Single process identified by Scout"""

    process_id: str
    name: str
    framework: str
    domain: str
    level: str  # L1/L2/L3/L4/L5
    description: str
    inputs: list[str]
    outputs: list[str]
    kpis: list[str]
    related_processes: list[str]
    sector_applicability: list[str]
    compliance_flags: list[str]
    source: str
    confidence: float  # 0.0 - 1.0


class ScoutResult(BaseModel):
    """Complete output from Scout for a framework"""

    framework: str
    version: str
    scout_timestamp: str
    total_processes: int
    processes: list[ProcessEntry]
    domains_covered: list[str]
    notes: str
    ready_for_architect: bool


# ── SCOUT CONFIGURATION ───────────────────────────────────────────────────────
SCOUT_CONFIG = {
    "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
    "max_tokens": 8000,
    "temperature": 0.1,  # Low temperature for factual research
    "rate_limit_rpm": 3,  # Groq free tier: 30 RPM
    "rate_limit_rpd": 1400,  # Stay safe under daily limits
}

# ── FRAMEWORK KNOWLEDGE BASE ──────────────────────────────────────────────────
FRAMEWORKS = {
    "SCOR": {
        "full_name": "Supply Chain Operations Reference",
        "version": "12.0",
        "owner": "APICS/ASCM",
        "domains": ["Plan", "Source", "Make", "Deliver", "Return", "Enable"],
        "description": "Standard supply chain management framework covering all SC processes",
        "public_sources": [
            "APICS SCOR documentation",
            "ASCM Supply Chain Council",
            "Academic papers on SCOR implementation",
        ],
    },
    "SCOR-D": {
        "full_name": "Supply Chain Operations Reference — Design",
        "version": "1.0",
        "owner": "APICS/ASCM",
        "domains": ["Design Chain", "Product Development", "Network Design"],
        "description": "Extension of SCOR covering design chain processes",
        "public_sources": ["APICS SCOR-D documentation", "ASCM Design Chain papers"],
    },
    "ISO_9001": {
        "full_name": "ISO 9001 Quality Management Systems",
        "version": "2015",
        "owner": "ISO",
        "domains": [
            "Context",
            "Leadership",
            "Planning",
            "Support",
            "Operation",
            "Performance",
            "Improvement",
        ],
        "description": "International standard for quality management systems",
        "public_sources": ["ISO 9001:2015 standard", "ISO TC176 documentation"],
    },
    "BPMN": {
        "full_name": "Business Process Model and Notation",
        "version": "2.0",
        "owner": "OMG",
        "domains": ["Process Flow", "Events", "Gateways", "Activities", "Connections"],
        "description": "Standard notation for business process modeling",
        "public_sources": [
            "OMG BPMN 2.0 specification",
            "Business process management literature",
        ],
    },
}


# ── SCOUT PROMPTS ─────────────────────────────────────────────────────────────
def build_research_prompt(framework: str, domain: str) -> str:
    """Build research prompt for a specific framework domain"""
    fw = FRAMEWORKS.get(framework, {})
    return f"""You are a supply chain and operations expert researching the {framework} framework.

FRAMEWORK: {fw.get("full_name", framework)}
VERSION: {fw.get("version", "latest")}
DOMAIN TO RESEARCH: {domain}

Your task is to identify and document ALL processes within this domain based on publicly available documentation, academic papers, and industry knowledge.

For each process, provide:
1. process_id: unique identifier (e.g., SCOR-P1.1)
2. name: official process name
3. domain: the domain it belongs to
4. level: complexity level (L1=simple to L5=very complex)
5. description: clear description of what this process does
6. inputs: list of inputs required
7. outputs: list of outputs produced
8. kpis: key performance indicators for this process
9. related_processes: other processes that connect to this one
10. sector_applicability: which industries use this process
11. compliance_flags: any regulatory requirements (GxP, EU AI Act, etc.)
12. confidence: your confidence in accuracy (0.0 to 1.0)

IMPORTANT:
- Only include processes from publicly documented sources
- Be specific and accurate
- Focus on processes that can be automated with AI agents
- Mark processes with regulatory implications

Return ONLY a valid JSON array of process objects. No explanation, no markdown, just JSON.

Example format:
[
  {{
    "process_id": "SCOR-P1.1",
    "name": "Identify, Prioritize and Aggregate Supply Chain Requirements",
    "domain": "Plan",
    "level": "L2",
    "description": "Process of collecting and prioritizing demand signals across the supply chain",
    "inputs": ["demand signals", "inventory data", "capacity data"],
    "outputs": ["supply chain requirements", "demand plan"],
    "kpis": ["forecast accuracy", "planning cycle time"],
    "related_processes": ["SCOR-P2.1", "SCOR-S1.1"],
    "sector_applicability": ["manufacturing", "distribution", "pharma", "food"],
    "compliance_flags": ["GxP if pharma", "GDP if distribution"],
    "confidence": 0.95
  }}
]"""


def build_domain_summary_prompt(framework: str, domain: str, processes: list) -> str:
    """Build prompt to summarize domain coverage"""
    return f"""You are reviewing research on the {framework} framework, {domain} domain.

{len(processes)} processes have been identified.

Provide a brief summary (2-3 sentences) of:
1. What this domain covers
2. Key automation opportunities
3. Main regulatory considerations

Return ONLY a plain text summary, no JSON, no markdown."""


# ── RATE LIMITER ──────────────────────────────────────────────────────────────
class RateLimiter:
    """Simple rate limiter to stay within Gemini free tier"""

    def __init__(self, rpm: int = 14):
        self.rpm = rpm
        self.min_interval = 60.0 / rpm
        self.last_call = 0.0
        self.daily_count = 0
        self.daily_limit = SCOUT_CONFIG["rate_limit_rpd"]

    def wait(self):
        """Wait if necessary to respect rate limits"""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.debug(f"Rate limiter: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        self.last_call = time.time()
        self.daily_count += 1
        if self.daily_count >= self.daily_limit:
            logger.warning(
                f"Daily limit approaching: {self.daily_count}/{self.daily_limit}"
            )


rate_limiter = RateLimiter(rpm=SCOUT_CONFIG["rate_limit_rpm"])


# ── LLM CALLER ────────────────────────────────────────────────────────────────
def call_llm(prompt: str, expect_json: bool = True) -> str:
    """Call Gemini Flash with rate limiting and error handling"""
    rate_limiter.wait()

    try:
        response = litellm.completion(
            model=SCOUT_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=SCOUT_CONFIG["max_tokens"],
            temperature=SCOUT_CONFIG["temperature"],
            api_key=os.getenv("GROQ_API_KEY"),
        )
        content = response.choices[0].message.content.strip()

        if expect_json:
            # Clean potential markdown code blocks
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])

        return content

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


# ── LIBRARY WRITER ────────────────────────────────────────────────────────────
def save_to_library(result: ScoutResult, framework: str):
    """Save Scout results to library"""
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))

    # Determine subfolder
    framework_folder = framework.lower().replace("-", "_").replace(" ", "_")
    if "scor" in framework_folder:
        folder = library_path / "scor"
    elif "iso" in framework_folder:
        folder = library_path / "iso"
    elif "bpmn" in framework_folder:
        folder = library_path / "bpmn"
    else:
        folder = library_path / "sector_specific"

    folder.mkdir(parents=True, exist_ok=True)

    # Save full result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = folder / f"scout_{framework_folder}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(f"Scout result saved: {filename}")

    # Save individual process files for easy library lookup
    processes_folder = folder / "processes"
    processes_folder.mkdir(exist_ok=True)

    for process in result.processes:
        proc_file = processes_folder / f"{process.process_id}.json"
        with open(proc_file, "w", encoding="utf-8") as f:
            json.dump(process.model_dump(), f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(result.processes)} individual process files")
    return filename


# ── MAIN SCOUT FUNCTION ───────────────────────────────────────────────────────
def scout_framework(framework: str, domains: Optional[list[str]] = None) -> ScoutResult:
    """
    Main Scout function: research and map a complete framework

    Args:
        framework: Framework name (SCOR, ISO_9001, BPMN, etc.)
        domains: Specific domains to research (None = all domains)

    Returns:
        ScoutResult with all discovered processes
    """
    logger.info(f"Scout starting research: {framework}")

    fw_config = FRAMEWORKS.get(framework)
    if not fw_config:
        logger.warning(
            f"Framework {framework} not in knowledge base, using generic approach"
        )
        fw_config = {
            "full_name": framework,
            "version": "latest",
            "domains": domains or ["General"],
            "description": framework,
        }

    target_domains = domains or fw_config.get("domains", ["General"])
    all_processes = []
    domains_covered = []

    for domain in target_domains:
        logger.info(f"Researching {framework} — {domain}")

        try:
            # Research processes in this domain
            prompt = build_research_prompt(framework, domain)
            response = call_llm(prompt, expect_json=True)

            # Parse JSON response
            domain_processes_raw = json.loads(response)

            # Validate and create ProcessEntry objects
            domain_processes = []
            for p in domain_processes_raw:
                try:
                    process = ProcessEntry(
                        process_id=p.get(
                            "process_id",
                            f"{framework}-{domain}-{len(domain_processes)}",
                        ),
                        name=p.get("name", "Unknown"),
                        framework=framework,
                        domain=domain,
                        level=p.get("level", "L2"),
                        description=p.get("description", ""),
                        inputs=p.get("inputs", []),
                        outputs=p.get("outputs", []),
                        kpis=p.get("kpis", []),
                        related_processes=p.get("related_processes", []),
                        sector_applicability=p.get("sector_applicability", []),
                        compliance_flags=p.get("compliance_flags", []),
                        source=f"Scout research — {fw_config.get('owner', 'public')}",
                        confidence=p.get("confidence", 0.8),
                    )
                    domain_processes.append(process)
                except Exception as e:
                    logger.warning(f"Failed to parse process: {e}")
                    continue

            all_processes.extend(domain_processes)
            domains_covered.append(domain)
            logger.success(
                f"Domain {domain}: {len(domain_processes)} processes identified"
            )

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {framework}/{domain}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error researching {framework}/{domain}: {e}")
            continue

    # Build final result
    result = ScoutResult(
        framework=framework,
        version=fw_config.get("version", "latest"),
        scout_timestamp=datetime.now().isoformat(),
        total_processes=len(all_processes),
        processes=all_processes,
        domains_covered=domains_covered,
        notes=f"Researched by Scout Agent — Agentic Zero Pioneer Team",
        ready_for_architect=len(all_processes) > 0,
    )

    # Save to library
    save_to_library(result, framework)

    logger.success(
        f"Scout complete: {framework} | "
        f"{len(all_processes)} processes | "
        f"{len(domains_covered)} domains"
    )

    return result


# ── CLI INTERFACE ─────────────────────────────────────────────────────────────
def run_scout(framework: str = "SCOR", domains: Optional[list] = None):
    """Run Scout from command line or as API"""
    logger.info("=" * 60)
    logger.info("AGENTIC ZERO — SCOUT AGENT")
    logger.info(f"Target: {framework}")
    logger.info(f"Model: {SCOUT_CONFIG['model']}")
    logger.info(f"Cost: $0.00 (Gemini Flash free tier)")
    logger.info("=" * 60)

    result = scout_framework(framework, domains)

    print(f"\n✅ Scout complete")
    print(f"   Framework: {result.framework}")
    print(f"   Processes found: {result.total_processes}")
    print(f"   Domains covered: {', '.join(result.domains_covered)}")
    print(f"   Ready for Architect: {result.ready_for_architect}")
    print(f"   Saved to library: library/{framework.lower()}/")

    return result


if __name__ == "__main__":
    import sys

    # Default: start with SCOR Plan domain only (test run)
    framework = sys.argv[1] if len(sys.argv) > 1 else "SCOR"
    domains = sys.argv[2:] if len(sys.argv) > 2 else None

    # For first test run, just do Plan domain to validate
    if framework == "SCOR" and not domains:
        print("\n⚡ First run: testing with SCOR Plan domain only")
        print(
            "   To run full SCOR: python scout.py SCOR Plan Source Make Deliver Return Enable\n"
        )
        domains = ["Plan"]

    run_scout(framework, domains)
