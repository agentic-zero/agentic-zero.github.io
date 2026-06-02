"""
AGENTIC ZERO — COMMERCIAL ENGINE
Agent: HERALD
Role: Chief Marketing & Growth Agent
Version: 1.0

Herald generates high-quality outreach and content for Alberto.
Herald proposes. Alberto decides and sends.

Capabilities v1.0:
  1. Personalized LinkedIn outreach messages
  2. LinkedIn authority posts
  3. ROI argumentario by sector and process
  4. EU AI Act urgency framing

Input: contact profile + process/agent + communication type
Output: ready-to-send content for review and approval

Architecture: Same as Pioneer Team — Groq free tier, RPM=1
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from loguru import logger
import litellm

load_dotenv()

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

logger.add(
    ROOT / "logs" / "herald_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | HERALD | {message}",
)


# ── MODELS ────────────────────────────────────────────────────────────────────
class ContactProfile(BaseModel):
    name: str
    company: str
    role: str
    sector: str  # pharma / defense / chemical / food / manufacturing
    country: str = "España"
    history: str = ""  # Historial de consultoría con este contacto
    pain_points: list[str] = []  # Dolores conocidos
    linkedin_url: str = ""
    last_contact: str = ""  # Cuándo fue el último contacto


class HeraldRequest(BaseModel):
    contact: ContactProfile
    process_id: str  # e.g. SCOR-P1.1
    communication_type: str  # first_contact / follow_up / audit_proposal / post
    language: str = "es"  # es / en
    tone: str = "professional"  # professional / warm / direct
    notes: str = ""  # Notas adicionales para Herald


class HeraldOutput(BaseModel):
    request_id: str
    generated_at: str
    communication_type: str
    contact_name: str
    process_id: str

    # Main outputs
    primary_message: str  # El mensaje principal listo para enviar
    subject_line: str  # Para email o contexto del mensaje
    key_arguments: list[str]  # Los 3-5 argumentos clave usados
    roi_hook: str  # El hook ROI específico para este sector
    eu_ai_act_angle: str  # El ángulo EU AI Act
    call_to_action: str  # El CTA específico

    # LinkedIn post (if requested)
    linkedin_post: Optional[str] = None
    linkedin_hashtags: Optional[list[str]] = None

    # Metadata
    word_count: int
    estimated_read_time_seconds: int
    confidence_score: float
    notes: str = ""


# ── HERALD CONFIGURATION ──────────────────────────────────────────────────────
HERALD_CONFIG = {
    "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
    "max_tokens": 4000,
    "temperature": 0.7,  # Más creatividad que los agentes técnicos
    "rate_limit_rpm": 1,
    "rate_limit_rpd": 1400,
}

# ── FOUNDER PROFILE ───────────────────────────────────────────────────────────
ALBERTO_PROFILE = """
Alberto Muñoz Waissen — Founder & CEO, Agentic Zero
25+ years experience · 30+ countries · 400+ industrial plants · $420M value demonstrated

Credentials:
- MIT Operations Research & Analytics
- Oxford AI Governance
- Vanderbilt Agentic AI Developer
- IBM AI Engineering Professional
- APICS SCOR-D
- EU AI Act · NIST AI RMF · ISO/IEC 42001

Key references:
- IFF Global: €30M project, 150 people, 20 countries
- Indra Defense: complex supply chain transformation
- Tiresur: €16M anti-dumping strategy

Background: 20+ years digital consulting, deep expertise in regulated environments.
Now building Agentic Zero — the first autonomous operations system for regulated supply chains.
"""

# ── ROI BENCHMARKS ────────────────────────────────────────────────────────────
ROI_BENCHMARKS = {
    "pharma": {"roi12": 876, "payback": 1.2, "annual_saving": 78060, "hourly": 85},
    "defense": {"roi12": 903, "payback": 1.2, "annual_saving": 80268, "hourly": 90},
    "chemical": {"roi12": 485, "payback": 2.1, "annual_saving": 46812, "hourly": 75},
    "food": {"roi12": 309, "payback": 2.9, "annual_saving": 32700, "hourly": 65},
    "automotive": {"roi12": 312, "payback": 2.9, "annual_saving": 32972, "hourly": 72},
    "manufacturing": {
        "roi12": 192,
        "payback": 4.1,
        "annual_saving": 23369,
        "hourly": 60,
    },
    "distribution": {
        "roi12": 136,
        "payback": 5.1,
        "annual_saving": 18894,
        "hourly": 55,
    },
}

# ── EU AI ACT CONTEXT ──────────────────────────────────────────────────────────
EU_AI_ACT_CONTEXT = """
EU AI Act enforcement begins August 2026 — in weeks.
High-risk AI systems in regulated supply chains require:
- Risk management system (Art. 9)
- Data governance (Art. 10)
- Technical documentation (Art. 11)
- Audit trail and logging (Art. 12)
- Human oversight measures (Art. 14)
- Conformity assessment before deployment

Agentic Zero agents come with compliance built-in:
- EU AI Act classification by Guardian Agent
- ISO/IEC 42001 certification
- NIST AI RMF alignment
- GDPR AI compliance
- Full audit trail from day 1

Companies deploying AI without this framework face significant regulatory risk.
"""

# ── PROCESS DESCRIPTIONS ──────────────────────────────────────────────────────
PROCESS_DESCRIPTIONS = {
    "SCOR-P1.1": "Identify, Prioritize and Aggregate Supply Chain Requirements — automated demand planning with GxP compliance",
    "SCOR-P1.2": "Analyze Supply Chain Capabilities and Capacity — AI-powered capacity assessment across your network",
    "SCOR-P1.3": "Balance SC Resources with Requirements — autonomous planning that optimizes supply vs demand",
    "SCOR-P1.4": "Establish SC Transportation Policy — intelligent transport optimization with regulatory compliance",
    "SCOR-P1.5": "Manage Supply Chain Risk — proactive risk detection and autonomous response in regulated environments",
    "SCOR-S1.1": "Schedule Product Deliveries — automated scheduling with compliance audit trail",
    "SCOR-S1.2": "Receive Product — intelligent receiving with quality and compliance verification",
    "SCOR-D1.1": "Deliver Stocked Product — end-to-end delivery automation for regulated distribution",
}

# ── RATE LIMITER ──────────────────────────────────────────────────────────────
import time


class RateLimiter:
    def __init__(self, rpm: int = 1):
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


rate_limiter = RateLimiter(rpm=HERALD_CONFIG["rate_limit_rpm"])


# ── LLM CALLER ────────────────────────────────────────────────────────────────
def call_llm(prompt: str) -> str:
    rate_limiter.wait()
    try:
        response = litellm.completion(
            model=HERALD_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=HERALD_CONFIG["max_tokens"],
            temperature=HERALD_CONFIG["temperature"],
            api_key=os.getenv("GROQ_API_KEY"),
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


# ── LIBRARY LOADER ────────────────────────────────────────────────────────────
def load_process(process_id: str) -> Optional[dict]:
    library_path = Path(os.getenv("LIBRARY_PATH", str(ROOT / "library")))
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        proc_file = library_path / folder / "processes" / f"{process_id}.json"
        if proc_file.exists():
            with open(proc_file, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


# ── PROMPTS ───────────────────────────────────────────────────────────────────
def build_outreach_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    lang = "Spanish" if request.language == "es" else "English"
    contact = request.contact

    return f"""You are Herald, the marketing agent for Agentic Zero.
You write on behalf of Alberto Muñoz Waissen, Founder & CEO.

FOUNDER PROFILE:
{ALBERTO_PROFILE}

CONTACT:
Name: {contact.name}
Company: {contact.company}
Role: {contact.role}
Sector: {contact.sector}
Country: {contact.country}
History with Alberto: {contact.history or "Previous consulting engagement"}
Known pain points: {", ".join(contact.pain_points) if contact.pain_points else "Supply chain complexity in regulated environment"}
Last contact: {contact.last_contact or "Some time ago"}

PROCESS/AGENT TO PRESENT:
{process.get("name", PROCESS_DESCRIPTIONS.get(request.process_id, request.process_id))}
{process.get("description", "")}

ROI DATA FOR {contact.sector.upper()}:
- ROI at 12 months: {roi.get("roi12", 0)}%
- Payback period: {roi.get("payback", 0)} months
- Annual saving: €{roi.get("annual_saving", 0):,}

EU AI ACT CONTEXT:
{EU_AI_ACT_CONTEXT}

COMMUNICATION TYPE: {request.communication_type}
TONE: {request.tone}
LANGUAGE: {lang}
ADDITIONAL NOTES: {request.notes or "None"}

Write a personalized LinkedIn message from Alberto to {contact.name}.

Requirements:
- Reference the shared history naturally (not forced)
- Lead with their pain, not our solution
- Include ONE specific ROI number for their sector
- Mention EU AI Act deadline only if it adds value
- End with a specific, low-friction CTA (15-min call, not "let's connect")
- Max 150 words for first_contact, 200 for follow_up
- Sound human, not like a sales pitch
- Language: {lang}

Write ONLY the message. No explanation, no subject line, no labels."""


def build_post_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    lang = "Spanish" if request.language == "es" else "English"
    sector = request.contact.sector

    return f"""You are Herald, writing a LinkedIn post for Alberto Muñoz Waissen, Founder & CEO of Agentic Zero.

ALBERTO'S VOICE: Direct, data-driven, provocative but credible. He has 25 years of field experience. He uses specific numbers. He challenges conventional thinking. He doesn't do buzzwords.

TOPIC: {process.get("name", request.process_id)} — autonomous operations in {sector}

ROI HOOK: {roi.get("roi12", 0)}% ROI in 12 months for {sector} companies

EU AI ACT: August 2026 deadline is real and most companies are not ready

POST REQUIREMENTS:
- Hook in first line (stop the scroll)
- 1 specific data point in first 3 lines
- Personal story or observation from 400+ plants visited
- Specific argument about why {sector} needs this NOW
- NOT promotional — educational and provocative
- End with a question that invites comments
- 150-250 words
- Language: {lang}
- 5-7 relevant hashtags at the end

Write ONLY the post content including hashtags. No labels or explanation."""


def build_roi_argumentario_prompt(
    request: HeraldRequest, process: dict, roi: dict
) -> str:
    lang = "Spanish" if request.language == "es" else "English"
    contact = request.contact

    return f"""You are Herald, creating a ROI argumentario for Alberto to use with {contact.name} at {contact.company}.

PROCESS: {process.get("name", request.process_id)}
SECTOR: {contact.sector}
ROI DATA: {roi.get("roi12", 0)}% ROI · €{roi.get("annual_saving", 0):,}/year · {roi.get("payback", 0)}m payback

Create a concise ROI argumentario with:
1. The problem (1 sentence, specific to {contact.sector})
2. The cost of inaction (quantified)
3. The Agentic Zero solution (1 sentence)
4. 3 specific ROI proof points for {contact.sector}
5. EU AI Act urgency (1 sentence)
6. The ask (specific next step)

Language: {lang}
Format: Bullet points, max 200 words total.
Write ONLY the argumentario."""


# ── HERALD MAIN FUNCTION ──────────────────────────────────────────────────────
def run_herald(request: HeraldRequest) -> HeraldOutput:
    logger.info(
        f"Herald starting: {request.communication_type} for {request.contact.name} ({request.contact.company})"
    )

    # Load process from library
    process = load_process(request.process_id)
    if not process:
        process = {
            "name": PROCESS_DESCRIPTIONS.get(request.process_id, request.process_id),
            "description": "Autonomous operations agent for regulated supply chains",
        }
        logger.warning(
            f"Process {request.process_id} not in library, using default description"
        )

    # Get ROI data
    roi = ROI_BENCHMARKS.get(request.contact.sector, ROI_BENCHMARKS["manufacturing"])

    request_id = f"HERALD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Generate primary message
    logger.info("Generating primary message...")
    if request.communication_type == "post":
        primary_message = call_llm(build_post_prompt(request, process, roi))
    else:
        primary_message = call_llm(build_outreach_prompt(request, process, roi))

    # Generate ROI argumentario
    logger.info("Generating ROI argumentario...")
    roi_hook = call_llm(build_roi_argumentario_prompt(request, process, roi))

    # Generate LinkedIn post if not already the main output
    linkedin_post = None
    linkedin_hashtags = None
    if request.communication_type != "post":
        logger.info("Generating LinkedIn post...")
        post_content = call_llm(build_post_prompt(request, process, roi))
        lines = post_content.split("\n")
        hashtag_lines = [l for l in lines if "#" in l]
        content_lines = [l for l in lines if "#" not in l]
        linkedin_post = "\n".join(content_lines).strip()
        hashtags = []
        for line in hashtag_lines:
            hashtags.extend([w for w in line.split() if w.startswith("#")])
        linkedin_hashtags = hashtags

    # Build output
    word_count = len(primary_message.split())
    read_time = max(10, word_count * 3)

    # Extract key arguments (simplified)
    key_arguments = [
        f"{roi.get('roi12', 0)}% ROI in 12 months for {request.contact.sector}",
        f"Payback in {roi.get('payback', 0)} months",
        f"€{roi.get('annual_saving', 0):,} annual saving",
        "EU AI Act compliance built-in from day 1",
        "5 compliance frameworks: EU AI Act · ISO 42001 · NIST RMF · GxP · GDPR",
    ]

    eu_ai_act_angle = f"EU AI Act enforcement begins August 2026. High-risk AI in {request.contact.sector} supply chains requires conformity assessment. Agentic Zero agents arrive pre-certified."

    # CTA based on type
    cta_map = {
        "first_contact": "15-minute call this week to show you the ROI numbers for your specific situation",
        "follow_up": "Quick call to walk you through what we built for a similar operation in your sector",
        "audit_proposal": "Free 10-day AUDIT — you see ROI before committing to anything",
        "post": "Share your experience with AI in regulated operations in the comments",
    }
    cta = cta_map.get(request.communication_type, cta_map["first_contact"])

    subject_map = {
        "first_contact": f"{roi.get('roi12', 0)}% ROI in 12 months — {process.get('name', request.process_id)[:40]}",
        "follow_up": f"Following up — autonomous operations for {request.contact.company}",
        "audit_proposal": f"Free AUDIT proposal — {request.contact.company}",
        "post": f"LinkedIn post — {process.get('name', request.process_id)[:50]}",
    }
    subject = subject_map.get(request.communication_type, "Agentic Zero")

    output = HeraldOutput(
        request_id=request_id,
        generated_at=datetime.now().isoformat(),
        communication_type=request.communication_type,
        contact_name=request.contact.name,
        process_id=request.process_id,
        primary_message=primary_message,
        subject_line=subject,
        key_arguments=key_arguments,
        roi_hook=roi_hook,
        eu_ai_act_angle=eu_ai_act_angle,
        call_to_action=cta,
        linkedin_post=linkedin_post,
        linkedin_hashtags=linkedin_hashtags,
        word_count=word_count,
        estimated_read_time_seconds=read_time,
        confidence_score=0.88,
        notes=f"Generated for {request.contact.name} at {request.contact.company}",
    )

    # Save output
    output_dir = ROOT / "core" / "herald" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{request_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output.model_dump(), f, indent=2, ensure_ascii=False)

    logger.success(f"Herald complete: {request_id} — {word_count} words generated")
    return output


# ── CLI INTERFACE ─────────────────────────────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Agentic Zero — Herald Marketing Agent"
    )
    parser.add_argument("--name", required=True, help="Contact name")
    parser.add_argument("--company", required=True, help="Contact company")
    parser.add_argument("--role", default="Supply Chain Director", help="Contact role")
    parser.add_argument(
        "--sector",
        default="manufacturing",
        choices=[
            "pharma",
            "defense",
            "chemical",
            "food",
            "automotive",
            "manufacturing",
            "distribution",
        ],
        help="Industry sector",
    )
    parser.add_argument("--process", default="SCOR-P1.1", help="Process ID to present")
    parser.add_argument(
        "--type",
        default="first_contact",
        choices=["first_contact", "follow_up", "audit_proposal", "post"],
        help="Communication type",
    )
    parser.add_argument("--history", default="", help="History with this contact")
    parser.add_argument("--language", default="es", choices=["es", "en"])
    parser.add_argument(
        "--tone", default="professional", choices=["professional", "warm", "direct"]
    )
    parser.add_argument("--notes", default="", help="Additional notes for Herald")
    args = parser.parse_args()

    request = HeraldRequest(
        contact=ContactProfile(
            name=args.name,
            company=args.company,
            role=args.role,
            sector=args.sector,
            history=args.history,
        ),
        process_id=args.process,
        communication_type=args.type,
        language=args.language,
        tone=args.tone,
        notes=args.notes,
    )

    logger.info("=" * 60)
    logger.info("AGENTIC ZERO — HERALD AGENT v1.0")
    logger.info(f"Contact: {args.name} @ {args.company} ({args.sector})")
    logger.info(f"Process: {args.process} | Type: {args.type}")
    logger.info("=" * 60)

    output = run_herald(request)

    print(f"\n{'=' * 60}")
    print(f"HERALD OUTPUT — {output.request_id}")
    print(f"{'=' * 60}")
    print(f"\n📧 SUBJECT: {output.subject_line}")
    print(f"\n{'─' * 60}")
    print(f"PRIMARY MESSAGE:")
    print(f"{'─' * 60}")
    print(output.primary_message)
    print(f"\n{'─' * 60}")
    print(f"ROI ARGUMENTARIO:")
    print(f"{'─' * 60}")
    print(output.roi_hook)
    print(f"\n{'─' * 60}")
    print(f"EU AI ACT ANGLE:")
    print(f"{'─' * 60}")
    print(output.eu_ai_act_angle)
    print(f"\n{'─' * 60}")
    print(f"CTA: {output.call_to_action}")
    if output.linkedin_post:
        print(f"\n{'─' * 60}")
        print(f"LINKEDIN POST:")
        print(f"{'─' * 60}")
        print(output.linkedin_post)
        if output.linkedin_hashtags:
            print("\n" + " ".join(output.linkedin_hashtags))
    print(f"\n{'─' * 60}")
    print(f"KEY ARGUMENTS:")
    for arg in output.key_arguments:
        print(f"  • {arg}")
    print(f"\n📁 Saved: core/herald/outputs/{output.request_id}.json")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
