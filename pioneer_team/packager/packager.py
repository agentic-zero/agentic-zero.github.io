"""
AGENTIC ZERO — PIONEER TEAM
Agent 4: PACKAGER
Role: Package Builder output into deliverable product
Input: BuilderResult (agent code + ontology + SOP + tests)
Output: Complete product package ready for Guardian and delivery

Responsibilities:
- Generate product documentation
- Create integration guides for common ERP systems
- Generate demo scripts for executive sessions
- Build pricing score based on complexity
- Create library catalog entry
- Prepare delivery package

Architecture: API-first, queue-ready, zero-cost (Groq free tier)
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
    "logs/packager_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


# ── MODELS ────────────────────────────────────────────────────────────────────
class PricingScore(BaseModel):
    """Complexity-based pricing score"""

    process_id: str
    complexity_score: int  # 1-100
    level: str  # L1/L2/L3/L4/L5
    base_price_eur: float  # Suggested base price
    regulated_surcharge: float  # Extra for regulated sectors
    total_price_eur: float  # Final suggested price
    price_rationale: str  # Why this price
    roi_multiplier: float  # Expected ROI for client


class ProductPackage(BaseModel):
    """Complete deliverable product package"""

    process_id: str
    agent_name: str
    package_version: str  # e.g. "1.0.0"
    packager_timestamp: str

    # Documentation
    product_summary: str  # 1-paragraph executive summary
    value_proposition: str  # Why this agent matters
    technical_summary: str  # Technical overview

    # Integration
    integration_guide: str  # How to deploy and connect
    supported_systems: list[str]  # ERPs and systems it connects to
    api_endpoints: list[str]  # API endpoints it exposes

    # Demo materials
    demo_script: str  # Script for executive demo session
    demo_inputs: dict  # Example inputs for demo
    expected_demo_outputs: dict  # Expected outputs for demo

    # Catalog entry
    catalog_entry: dict  # Library catalog entry
    tags: list[str]  # Searchable tags
    use_cases: list[str]  # Specific use cases

    # Pricing
    pricing: PricingScore

    # Metadata
    ready_for_guardian: bool
    package_path: str


# ── PACKAGER CONFIGURATION ────────────────────────────────────────────────────
PACKAGER_CONFIG = {
    "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
    "max_tokens": 4000,
    "temperature": 0.2,
    "rate_limit_rpm": 1,
    "rate_limit_rpd": 1400,
    "package_version": "1.0.0",
}

# ── PRICING MODEL ─────────────────────────────────────────────────────────────
PRICING_CONFIG = {
    "L1": {"base": 149, "roi_multiplier": 10.0},
    "L2": {"base": 499, "roi_multiplier": 8.0},
    "L3": {"base": 1500, "roi_multiplier": 6.0},
    "L4": {"base": 5000, "roi_multiplier": 5.0},
    "L5": {"base": 15000, "roi_multiplier": 4.0},
}

REGULATED_SURCHARGE = {
    "pharma": 0.40,  # +40% for GxP/GMP
    "defense": 0.50,  # +50% for classified/ITAR
    "medtech": 0.45,  # +45% for ISO 13485/MDR
    "chemical": 0.25,  # +25% for REACH/HARPC
    "food": 0.20,  # +20% for HACCP/FSMA
    "automotive": 0.15,  # +15% for IATF/APQP
}

SUPPORTED_SYSTEMS = [
    "SAP ECC",
    "SAP S/4HANA",
    "SAP EWM",
    "Oracle ERP Cloud",
    "Oracle JDE",
    "Microsoft Dynamics 365",
    "Custom REST APIs",
    "CSV/Excel file input",
    "Database direct connection",
]


# ── RATE LIMITER ──────────────────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, rpm: int = 1):
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


rate_limiter = RateLimiter(rpm=PACKAGER_CONFIG["rate_limit_rpm"])


# ── LLM CALLER ────────────────────────────────────────────────────────────────
def call_llm(prompt: str, expect_json: bool = False) -> str:
    rate_limiter.wait()
    try:
        response = litellm.completion(
            model=PACKAGER_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=PACKAGER_CONFIG["max_tokens"],
            temperature=PACKAGER_CONFIG["temperature"],
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


# ── PRICING CALCULATOR ────────────────────────────────────────────────────────
def calculate_pricing(process: dict, builder_result: dict) -> PricingScore:
    """Calculate pricing score based on process complexity"""
    level = process.get("level", "L2")
    pricing = PRICING_CONFIG.get(level, PRICING_CONFIG["L2"])
    base_price = pricing["base"]
    roi_multiplier = pricing["roi_multiplier"]

    # Calculate complexity score (1-100)
    complexity_factors = {
        "inputs_count": min(len(process.get("inputs", [])) * 5, 20),
        "outputs_count": min(len(process.get("outputs", [])) * 5, 15),
        "compliance_count": min(len(process.get("compliance_flags", [])) * 10, 30),
        "kpis_count": min(len(process.get("kpis", [])) * 3, 15),
        "level_base": {"L1": 10, "L2": 25, "L3": 50, "L4": 75, "L5": 90}.get(level, 25),
    }
    complexity_score = min(sum(complexity_factors.values()), 100)

    # Calculate regulated surcharge
    sector_list = " ".join(process.get("sector_applicability", [])).lower()
    compliance_text = " ".join(process.get("compliance_flags", [])).lower()
    max_surcharge = 0.0
    for sector, surcharge in REGULATED_SURCHARGE.items():
        if sector in sector_list or sector in compliance_text:
            max_surcharge = max(max_surcharge, surcharge)

    regulated_surcharge = base_price * max_surcharge
    total_price = base_price + regulated_surcharge

    rationale = f"Level {level} process with complexity score {complexity_score}/100"
    if max_surcharge > 0:
        rationale += f". Regulated sector surcharge {int(max_surcharge * 100)}% applied"

    return PricingScore(
        process_id=process.get("process_id", "UNKNOWN"),
        complexity_score=complexity_score,
        level=level,
        base_price_eur=base_price,
        regulated_surcharge=regulated_surcharge,
        total_price_eur=total_price,
        price_rationale=rationale,
        roi_multiplier=roi_multiplier,
    )


# ── PROMPTS ───────────────────────────────────────────────────────────────────
def build_summary_prompt(process: dict, agent_spec: dict) -> str:
    return f"""You are a product manager at Agentic Zero writing product documentation.

PROCESS: {process.get("name")}
DESCRIPTION: {process.get("description")}
AGENT TYPE: {agent_spec.get("agent_type")}
CAPABILITIES: {agent_spec.get("capabilities", [])}
COMPLIANCE: {process.get("compliance_flags", [])}

Write 3 sections. Return plain text, no JSON, no markdown headers:

PRODUCT_SUMMARY: One paragraph (3-4 sentences) for executives explaining what this agent does and its business value.

VALUE_PROPOSITION: One sentence that captures the core value. Start with "Automates" or "Eliminates" or "Transforms".

TECHNICAL_SUMMARY: One paragraph (2-3 sentences) for technical teams explaining architecture and integration.

Format exactly as:
PRODUCT_SUMMARY: [text]
VALUE_PROPOSITION: [text]
TECHNICAL_SUMMARY: [text]"""


def build_demo_script_prompt(
    process: dict, agent_spec: dict, pricing: PricingScore
) -> str:
    return f"""You are preparing a demo script for an executive session at Agentic Zero.

AGENT: {agent_spec.get("agent_name")}
PROCESS: {process.get("name")}
VALUE PROPOSITION: Automates {process.get("name")} with AI
PRICE: €{pricing.total_price_eur:.0f}
ROI MULTIPLIER: {pricing.roi_multiplier}x

Write a concise demo script (5-7 steps) for a 10-minute executive demo.
Focus on showing ROI and compliance value.
Return plain text, numbered steps."""


def build_use_cases_prompt(process: dict) -> str:
    return f"""You are a business analyst at Agentic Zero.

PROCESS: {process.get("name")}
SECTORS: {process.get("sector_applicability", [])}
COMPLIANCE: {process.get("compliance_flags", [])}

List 5 specific use cases where this agent delivers clear ROI.
Return ONLY a JSON array of strings:
["Use case 1: specific scenario with measurable outcome",
 "Use case 2: ...",
 ...]"""


# ── LOCAL PACKAGER (no LLM needed for most tasks) ─────────────────────────────
def build_catalog_entry(process: dict, agent_spec: dict, pricing: PricingScore) -> dict:
    """Build library catalog entry — no LLM needed"""
    return {
        "process_id": process.get("process_id"),
        "agent_name": agent_spec.get("agent_name"),
        "framework": process.get("framework"),
        "domain": process.get("domain"),
        "level": process.get("level"),
        "sector_applicability": process.get("sector_applicability", []),
        "compliance_frameworks": process.get("compliance_flags", []),
        "agent_type": agent_spec.get("agent_type"),
        "capabilities_count": len(agent_spec.get("capabilities", [])),
        "price_eur": pricing.total_price_eur,
        "complexity_score": pricing.complexity_score,
        "roi_multiplier": pricing.roi_multiplier,
        "status": "ready_for_guardian",
        "version": PACKAGER_CONFIG["package_version"],
        "created_at": datetime.now().isoformat(),
    }


def build_integration_guide(process: dict, agent_spec: dict) -> str:
    """Build integration guide — no LLM needed"""
    lines = [
        f"# Integration Guide — {agent_spec.get('agent_name')}",
        f"**Process:** {process.get('name')}",
        f"**Version:** {PACKAGER_CONFIG['package_version']}",
        "",
        "## Prerequisites",
        "- Python 3.10+",
        "- Agentic Zero runtime installed",
        "- API credentials configured in .env",
        "",
        "## Installation",
        "```bash",
        f"# Copy agent to your project",
        f"cp {agent_spec.get('agent_name')}.py ./agents/",
        "```",
        "",
        "## Basic Usage",
        "```python",
        f"from agents.{agent_spec.get('agent_name')} import {agent_spec.get('agent_name', '').title().replace('_', '')}Agent",
        "",
        f"agent = {agent_spec.get('agent_name', '').title().replace('_', '')}Agent()",
        "result = agent.execute({",
    ]
    for inp in process.get("inputs", [])[:3]:
        key = inp.replace(" ", "_").lower()
        lines.append(f'    "{key}": your_{key}_data,')
    lines += [
        "})",
        "print(result['outputs'])",
        "```",
        "",
        "## Supported Systems",
    ]
    for system in SUPPORTED_SYSTEMS[:5]:
        lines.append(f"- {system}")
    lines += [
        "",
        "## Tools Required",
    ]
    for tool in agent_spec.get("tools_required", ["None required"]):
        lines.append(f"- {tool}")
    lines += [
        "",
        "## Escalation",
        "The agent automatically escalates to human when:",
    ]
    for rule in agent_spec.get("escalation_rules", ["- Execution error detected"]):
        lines.append(f"- {rule}")
    return "\n".join(lines)


def build_api_endpoints(process: dict, agent_spec: dict) -> list[str]:
    """Generate API endpoint definitions"""
    agent_name = agent_spec.get("agent_name", "agent")
    base = f"/api/v1/agents/{agent_name}"
    return [
        f"POST {base}/execute — Execute the agent with inputs",
        f"GET  {base}/status — Get agent status and metrics",
        f"GET  {base}/health — Health check",
        f"GET  {base}/spec   — Get agent specification",
        f"POST {base}/test   — Run test cases",
    ]


# ── LIBRARY LOADER / WRITER ───────────────────────────────────────────────────
def load_builder_result(process_id: str) -> Optional[dict]:
    """Load Builder result from library"""
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        result_file = library_path / folder / "agents" / f"{process_id}_builder.json"
        if result_file.exists():
            with open(result_file, "r", encoding="utf-8") as f:
                return json.load(f)
    logger.error(f"Builder result not found for: {process_id}")
    return None


def load_process(process_id: str) -> Optional[dict]:
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        proc_file = library_path / folder / "processes" / f"{process_id}.json"
        if proc_file.exists():
            with open(proc_file, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def save_package(package: ProductPackage, process: dict):
    """Save product package to library"""
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    framework = process.get("framework", "scor").lower()

    if "scor" in framework:
        folder = library_path / "scor"
    elif "iso" in framework:
        folder = library_path / "iso"
    else:
        folder = library_path / "sector_specific"

    packages_folder = folder / "packages"
    packages_folder.mkdir(exist_ok=True)

    # Save full package JSON
    package_file = packages_folder / f"{package.process_id}_package.json"
    with open(package_file, "w", encoding="utf-8") as f:
        json.dump(package.model_dump(), f, indent=2, ensure_ascii=False)

    # Save demo script as text
    demo_file = packages_folder / f"{package.process_id}_demo_script.txt"
    with open(demo_file, "w", encoding="utf-8") as f:
        f.write(package.demo_script)

    # Save integration guide as markdown
    guide_file = packages_folder / f"{package.process_id}_integration_guide.md"
    with open(guide_file, "w", encoding="utf-8") as f:
        f.write(package.integration_guide)

    # Update catalog
    catalog_file = folder / "catalog.json"
    catalog = []
    if catalog_file.exists():
        with open(catalog_file, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    existing_ids = [e.get("process_id") for e in catalog]
    if package.process_id not in existing_ids:
        catalog.append(package.catalog_entry)
    else:
        catalog = [
            package.catalog_entry if e.get("process_id") == package.process_id else e
            for e in catalog
        ]
    with open(catalog_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    logger.info(f"Package saved: {package_file}")
    logger.info(f"Catalog updated: {catalog_file}")
    return str(package_file)


# ── MAIN PACKAGER FUNCTION ────────────────────────────────────────────────────
def package_agent(process_id: str) -> Optional[ProductPackage]:
    """
    Main Packager function: build deliverable product package

    Args:
        process_id: ID of the process to package

    Returns:
        ProductPackage ready for Guardian
    """
    logger.info(f"Packager starting: {process_id}")

    # Load process and builder result
    process = load_process(process_id)
    if not process:
        logger.error(f"Process not found: {process_id}")
        return None

    builder_result = load_builder_result(process_id)
    if not builder_result:
        logger.error(f"Builder result not found for {process_id}. Run Builder first.")
        return None

    agent_spec = builder_result.get("agent_spec", {})
    agent_name = agent_spec.get("agent_name", f"agent_{process_id.lower()}")

    try:
        # STEP 1 — Calculate pricing (local, no tokens)
        logger.info("Step 1/5: Calculating pricing score...")
        pricing = calculate_pricing(process, builder_result)
        logger.success(
            f"Pricing: €{pricing.total_price_eur:.0f} (complexity: {pricing.complexity_score}/100)"
        )

        # STEP 2 — Generate summaries (LLM)
        logger.info("Step 2/5: Generating product summaries...")
        prompt = build_summary_prompt(process, agent_spec)
        response = call_llm(prompt, expect_json=False)

        product_summary = ""
        value_proposition = ""
        technical_summary = ""

        for line in response.split("\n"):
            if line.startswith("PRODUCT_SUMMARY:"):
                product_summary = line.replace("PRODUCT_SUMMARY:", "").strip()
            elif line.startswith("VALUE_PROPOSITION:"):
                value_proposition = line.replace("VALUE_PROPOSITION:", "").strip()
            elif line.startswith("TECHNICAL_SUMMARY:"):
                technical_summary = line.replace("TECHNICAL_SUMMARY:", "").strip()

        if not product_summary:
            product_summary = f"The {agent_name} automates {process.get('name')} within {process.get('framework')} framework. It processes {', '.join(process.get('inputs', [])[:2])} to generate {', '.join(process.get('outputs', [])[:2])}. Compliance with {', '.join(process.get('compliance_flags', ['standard requirements']))} is built-in."
        if not value_proposition:
            value_proposition = (
                f"Automates {process.get('name')} reducing manual effort by up to 90%."
            )

        logger.success("Summaries generated")

        # STEP 3 — Generate demo script (LLM)
        logger.info("Step 3/5: Generating demo script...")
        prompt = build_demo_script_prompt(process, agent_spec, pricing)
        demo_script = call_llm(prompt, expect_json=False)
        logger.success("Demo script generated")

        # STEP 4 — Generate use cases (LLM)
        logger.info("Step 4/5: Generating use cases...")
        prompt = build_use_cases_prompt(process)
        response = call_llm(prompt, expect_json=True)
        try:
            use_cases = json.loads(response)
        except Exception:
            use_cases = [
                f"Automate {process.get('name')} in {s} sector"
                for s in process.get("sector_applicability", ["manufacturing"])[:5]
            ]
        logger.success(f"{len(use_cases)} use cases generated")

        # STEP 5 — Build package (local)
        logger.info("Step 5/5: Building package...")
        integration_guide = build_integration_guide(process, agent_spec)
        api_endpoints = build_api_endpoints(process, agent_spec)
        catalog_entry = build_catalog_entry(process, agent_spec, pricing)

        # Demo inputs/outputs examples
        demo_inputs = {}
        for inp in process.get("inputs", [])[:3]:
            key = inp.replace(" ", "_").lower()
            demo_inputs[key] = f"[example_{key}]"
        demo_outputs = {}
        for out in process.get("outputs", [])[:2]:
            key = out.replace(" ", "_").lower()
            demo_outputs[key] = f"[generated_{key}]"

        # Tags for search
        tags = list(
            set(
                [process.get("framework", "").lower()]
                + [process.get("domain", "").lower()]
                + [process.get("level", "").lower()]
                + process.get("sector_applicability", [])
                + [agent_spec.get("agent_type", "")]
            )
        )

        package_path = f"library/scor/packages/{process_id}_package.json"

        package = ProductPackage(
            process_id=process_id,
            agent_name=agent_name,
            package_version=PACKAGER_CONFIG["package_version"],
            packager_timestamp=datetime.now().isoformat(),
            product_summary=product_summary,
            value_proposition=value_proposition,
            technical_summary=technical_summary
            or f"Reactive agent implementing {process.get('framework')} {process.get('domain')} process. Integrates via REST API with major ERP systems.",
            integration_guide=integration_guide,
            supported_systems=SUPPORTED_SYSTEMS,
            api_endpoints=api_endpoints,
            demo_script=demo_script,
            demo_inputs=demo_inputs,
            expected_demo_outputs=demo_outputs,
            catalog_entry=catalog_entry,
            tags=tags,
            use_cases=use_cases if isinstance(use_cases, list) else [],
            pricing=pricing,
            ready_for_guardian=True,
            package_path=package_path,
        )

        # Save package
        save_package(package, process)

        logger.success(
            f"Packager complete: {process_id} | "
            f"Agent: {agent_name} | "
            f"Price: €{pricing.total_price_eur:.0f} | "
            f"Ready for Guardian: {package.ready_for_guardian}"
        )

        return package

    except Exception as e:
        logger.error(f"Packager failed for {process_id}: {e}")
        return None


# ── CLI INTERFACE ─────────────────────────────────────────────────────────────
def run_packager(process_ids: list):
    logger.info("=" * 60)
    logger.info("AGENTIC ZERO — PACKAGER AGENT")
    logger.info(f"Processes to package: {process_ids}")
    logger.info(f"Model: {PACKAGER_CONFIG['model']}")
    logger.info("=" * 60)

    results = []
    for pid in process_ids:
        logger.info(f"Packaging: {pid}")
        package = package_agent(pid)
        if package:
            results.append(package)
            print(f"\n✅ {pid} → {package.agent_name}")
            print(f"   Price: €{package.pricing.total_price_eur:.0f}")
            print(f"   Complexity: {package.pricing.complexity_score}/100")
            print(f"   Use cases: {len(package.use_cases)}")
            print(f"   Ready for Guardian: {package.ready_for_guardian}")
        else:
            print(f"\n❌ {pid} → Packaging failed")

    print(f"\n{'=' * 40}")
    print(f"Packager complete: {len(results)}/{len(process_ids)} packages built")
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("\nUsage: python packager.py PROCESS_ID [PROCESS_ID2 ...]")
        print("Example: python packager.py SCOR-P1.1")
        print("Note: Builder must have run first for each process\n")
        sys.exit(1)

    process_ids = sys.argv[1:]
    run_packager(process_ids)
