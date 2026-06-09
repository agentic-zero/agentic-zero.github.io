"""
AGENTIC ZERO — COMMERCIAL ENGINE
Agent: HERALD
Role: Chief Marketing & Growth Agent
Version: 2.0

Herald generates high-quality outreach and content for Alberto.
Herald proposes. Alberto decides and sends.

Capabilities v2.0:
  1. Personalized LinkedIn outreach messages
  2. Personalized email outreach (subject + body)
  3. Full follow-up sequences (3-touch)
  4. LinkedIn authority posts
  5. ROI argumentario by sector and process
  6. EU AI Act urgency framing
  7. AUDIT proposal messages
  8. Venture integration — import opportunities directly

Input: contact profile + process/agent + communication type
Output: ready-to-send content for review and approval
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
    sector: str
    country: str = "España"
    history: str = ""
    pain_points: list[str] = []
    linkedin_url: str = ""
    email: str = ""
    last_contact: str = ""


class HeraldRequest(BaseModel):
    contact: ContactProfile
    process_id: str
    communication_type: (
        str  # first_contact / follow_up / sequence / audit_proposal / post / email
    )
    language: str = "en"
    tone: str = "professional"
    notes: str = ""
    venture_opp_id: str = ""  # Optional: link to Venture pipeline opportunity


class HeraldOutput(BaseModel):
    request_id: str
    generated_at: str
    communication_type: str
    contact_name: str
    process_id: str

    # Main outputs
    primary_message: str
    subject_line: str
    email_body: Optional[str] = None
    key_arguments: list[str]
    roi_hook: str
    eu_ai_act_angle: str
    call_to_action: str

    # Sequence (3-touch)
    sequence: Optional[list[dict]] = None

    # LinkedIn post
    linkedin_post: Optional[str] = None
    linkedin_hashtags: Optional[list[str]] = None

    # Metadata
    word_count: int
    estimated_read_time_seconds: int
    confidence_score: float
    notes: str = ""


# ── HERALD CONFIGURATION ──────────────────────────────────────────────────────
HERALD_CONFIG = {
    "model": os.getenv("XAI_MODEL", "xai/grok-3-mini"),
    "max_tokens": 4000,
    "temperature": 0.7,
    "rate_limit_rpm": 30,
}

# ── FOUNDER PROFILE ───────────────────────────────────────────────────────────
ALBERTO_PROFILE = """
Alberto Muñoz Waissen — Founder & CEO, Agentic Zero
Powered by Dis-Solutions — 25 years of digital transformation consultancy

Credentials:
- MIT Operations Research & Analytics
- Oxford AI Governance
- Vanderbilt Agentic AI Developer
- IBM AI Engineering Professional
- APICS SCOR-D
- EU AI Act · NIST AI RMF · ISO/IEC 42001

Track record:
- 25 years · 30+ countries · 400+ industrial plants
- $420M value demonstrated in operations transformation
- Deep expertise in regulated environments (pharma, defense, chemical, food)

Now building Agentic Zero — certified AI agents for complex operations.
Any company, any industry, any size.
"""

# ── ROI BENCHMARKS (updated · defendible · 3 processes · 3 FTE basis) ────────
ROI_BENCHMARKS = {
    "pharma": {
        "roi12": 322,
        "payback": 2.8,
        "annual_saving": 156000,
        "automation_pct": 65,
    },
    "defense": {
        "roi12": 349,
        "payback": 2.7,
        "annual_saving": 166000,
        "automation_pct": 65,
    },
    "chemical": {
        "roi12": 285,
        "payback": 3.2,
        "annual_saving": 137000,
        "automation_pct": 60,
    },
    "food": {
        "roi12": 242,
        "payback": 3.7,
        "annual_saving": 117000,
        "automation_pct": 55,
    },
    "automotive": {
        "roi12": 264,
        "payback": 3.4,
        "annual_saving": 127000,
        "automation_pct": 58,
    },
    "manufacturing": {
        "roi12": 218,
        "payback": 4.1,
        "annual_saving": 107000,
        "automation_pct": 52,
    },
    "distribution": {
        "roi12": 196,
        "payback": 4.6,
        "annual_saving": 98000,
        "automation_pct": 50,
    },
}

# Reference benchmarks from published sources
MARKET_BENCHMARKS = """
Real-world agentic benchmarks (published sources):
- ClawWork (Claude Opus 4 · Mar 2026): One agent, $10 capital → $19,915 in 8 hours, 220 tasks
- The AI Agent Economy (Medium 2026): Same agent sold 7× → $47,000 from 20 hours of work, still running
"""

# ── EU AI ACT CONTEXT ──────────────────────────────────────────────────────────
EU_AI_ACT_CONTEXT = """
EU AI Act enforcement begins August 2026 — mandatory for high-risk AI systems.
High-risk AI in regulated supply chains (pharma, defense, chemical, food) requires:
- Risk management system (Art. 9)
- Data governance (Art. 10)
- Technical documentation (Art. 11)
- Audit trail and logging (Art. 12)
- Human oversight measures (Art. 14)
- Conformity assessment before deployment

Agentic Zero agents come pre-certified:
- EU AI Act classification by Guardian Agent
- ISO/IEC 42001 certification
- NIST AI RMF alignment
- GDPR AI compliance
- Full audit trail from day 1

Companies deploying AI without this framework face regulatory risk from August 2026.
"""

# ── PROCESS DESCRIPTIONS ──────────────────────────────────────────────────────
PROCESS_DESCRIPTIONS = {
    "SCOR-P1.1": "Supply Chain Plan Reliability — automated demand planning",
    "SCOR-P1.2": "Supply Chain Capacity Assessment — AI-powered capacity analysis",
    "SCOR-P1.3": "Supply/Demand Balance — autonomous planning optimization",
    "SCOR-P1.4": "Transportation Policy — intelligent transport optimization",
    "SCOR-P1.5": "Supply Chain Risk Management — proactive risk detection",
    "SCOR-S1.1": "Purchase Order Scheduling — automated PO management",
    "SCOR-S1.2": "Payment Authorization — intelligent payment processing",
    "SCOR-S1.3": "Supplier Information Management — supplier data automation",
    "SCOR-S1.4": "Supplier Contract Management — contract lifecycle automation",
    "SCOR-S1.5": "Supplier Audit & Assessment — automated compliance auditing",
    "SCOR-M1.1": "Production Scheduling — autonomous manufacturing planning",
    "SCOR-M2.1": "Production Release — automated production order management",
    "SCOR-M3.1": "Production Confirmation — quality and compliance verification",
    "SCOR-M4.1": "Product Testing & Inspection — automated QC with audit trail",
    "SCOR-M5.1": "Pack & Prepare for Distribution — packaging automation",
    "SCOR-D1.1": "Design Chain Strategy — supply chain design automation",
    "SCOR-D1.2": "Design Chain Roadmap — roadmap planning agent",
}

# ── RATE LIMITER ──────────────────────────────────────────────────────────────
import time


class RateLimiter:
    def __init__(self, rpm: int = 1):
        self.min_interval = 60.0 / rpm
        self.last_call = 0.0

    def wait(self):
        elapsed = time.time() - self.last_call
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
            api_key=os.getenv("XAI_API_KEY"),
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


# ── PROCESS LOADER ────────────────────────────────────────────────────────────
def load_process(process_id: str) -> Optional[dict]:
    library_path = ROOT / "library" / "scor" / "processes" / f"{process_id}.json"
    if library_path.exists():
        with open(library_path, encoding="utf-8") as f:
            return json.load(f)
    return None


# ── PROMPT BUILDERS ───────────────────────────────────────────────────────────


def build_linkedin_outreach_prompt(
    request: HeraldRequest, process: dict, roi: dict
) -> str:
    lang = "English" if request.language == "en" else "Spanish"
    pain = (
        "\n".join(f"- {p}" for p in request.contact.pain_points)
        if request.contact.pain_points
        else "Not specified"
    )
    history = request.contact.history or "No prior contact"

    return f"""You are Herald, the marketing agent for Agentic Zero.
Write a personalized LinkedIn outreach message for Alberto Muñoz Waissen to send.

AGENTIC ZERO:
Certified AI agents for complex operations. Any company, any industry.
Powered by Dis-Solutions — 25 years of digital transformation consultancy.

SENDER PROFILE:
{ALBERTO_PROFILE}

CONTACT:
Name: {request.contact.name}
Company: {request.contact.company}
Role: {request.contact.role}
Sector: {request.contact.sector}
Country: {request.contact.country}
History: {history}
Known pain points: {pain}

PROCESS/AGENT:
{process.get("name", process_id_to_name(request.process_id))}
{process.get("description", PROCESS_DESCRIPTIONS.get(request.process_id, ""))}

ROI DATA (defendible · 3 processes · 3 FTE basis):
- {roi["roi12"]}% ROI in 12 months
- Payback in {roi["payback"]} months
- ${roi["annual_saving"]:,} annual saving estimated
- {roi["automation_pct"]}% automation rate (conservative)

MARKET BENCHMARKS:
{MARKET_BENCHMARKS}

EU AI ACT:
{EU_AI_ACT_CONTEXT}

COMMUNICATION TYPE: {request.communication_type}
TONE: {request.tone}
NOTES: {request.notes or "None"}

RULES:
- Write in {lang}
- LinkedIn message: max 300 characters for connection request OR max 1000 chars for message
- Start with something specific about them or their company — NOT "I hope this finds you well"
- Lead with value, not features
- ONE clear CTA at the end
- Do NOT mention you are an AI
- Do NOT use hollow phrases like "synergies", "leverage", "circle back"
- Sound like a human expert, not a bot
- Reference the free AUDIT as the entry point (no risk, ROI calculated on their data)

Write ONLY the message. No preamble, no explanation."""


def build_email_outreach_prompt(
    request: HeraldRequest, process: dict, roi: dict
) -> str:
    lang = "English" if request.language == "en" else "Spanish"
    pain = (
        "\n".join(f"- {p}" for p in request.contact.pain_points)
        if request.contact.pain_points
        else "Not specified"
    )

    return f"""You are Herald, the marketing agent for Agentic Zero.
Write a personalized cold email for Alberto Muñoz Waissen to send.

SENDER PROFILE:
{ALBERTO_PROFILE}

CONTACT:
Name: {request.contact.name}
Company: {request.contact.company}
Role: {request.contact.role}
Sector: {request.contact.sector}
Known pain points: {pain}

PROCESS/AGENT:
{process.get("name", process_id_to_name(request.process_id))}

ROI DATA:
- {roi["roi12"]}% ROI in 12 months
- Payback in {roi["payback"]} months
- ${roi["annual_saving"]:,} annual saving estimated

MARKET BENCHMARKS:
{MARKET_BENCHMARKS}

EU AI ACT:
{EU_AI_ACT_CONTEXT}

NOTES: {request.notes or "None"}

OUTPUT FORMAT (return exactly this):
SUBJECT: [subject line here]
---
[email body here]

RULES:
- Write in {lang}
- Subject: specific, value-focused, max 60 chars, no spam words
- Body: max 150 words, 3 short paragraphs
- Paragraph 1: specific hook about their situation
- Paragraph 2: what Agentic Zero does + one concrete number
- Paragraph 3: CTA — free AUDIT, no risk
- Signature: Alberto Muñoz Waissen | Agentic Zero | Powered by Dis-Solutions
- Sound like a human expert
- Do NOT mention you are an AI

Write ONLY subject + body."""


def build_touch1_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    """Touch 1 — LinkedIn — Recognize the problem. No pitch."""
    lang = "English" if request.language == "en" else "Spanish"
    pain = (
        ", ".join(request.contact.pain_points)
        if request.contact.pain_points
        else "operational inefficiencies"
    )

    return f"""You are Herald, writing on behalf of Alberto Muñoz Waissen (Agentic Zero · Dis-Solutions).
Write a LinkedIn message. Alberto has 25 years experience, 400+ industrial plants, 30 countries.

CONTACT: {request.contact.name} · {request.contact.role} · {request.contact.company} · {request.contact.sector}
THEIR PAIN: {pain}

GOAL: Recognize their SPECIFIC pain with precision. Show you understand it better than they can articulate.
Do NOT pitch. Do NOT mention ROI or products. Do NOT say what you do.
Ask ONE sharp question that shows deep expertise.

FORMAT: Max 500 characters. Sound like a human expert, not a bot.
Language: {lang}
Sign: Alberto Muñoz Waissen | Agentic Zero

Return ONLY the message text."""


def build_touch2_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    """Touch 2 — Email — Expert perspective. No product pitch yet."""
    lang = "English" if request.language == "en" else "Spanish"
    pain = (
        ", ".join(request.contact.pain_points)
        if request.contact.pain_points
        else "operational inefficiencies"
    )

    return f"""You are Herald, writing on behalf of Alberto Muñoz Waissen (Agentic Zero · Dis-Solutions).
Write a cold email. Alberto has 25 years experience, 400+ industrial plants, 30 countries.

CONTACT: {request.contact.name} · {request.contact.role} · {request.contact.company} · {request.contact.sector}
THEIR PAIN: {pain}

GOAL: Share expert insight from field experience. Describe 2-3 specific consequences of their pain
that they may not have quantified. Reference a similar situation resolved (no client names, sector only).
Do NOT pitch the product yet. Just show expertise and offer a 15-minute conversation.

FORMAT:
Line 1: SUBJECT: [subject line]
Line 2: ---
Lines 3+: Email body max 150 words.
3 short paragraphs:
  P1: Specific insight about their situation (from field experience)
  P2: 2-3 consequences they may not have measured
  P3: CTA — 15 minutes to share the approach, no commitment

Language: {lang}
Sign: Alberto Muñoz Waissen | Agentic Zero | Powered by Dis-Solutions
Return ONLY subject + body."""


def build_touch3_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    """Touch 3 — LinkedIn — Present the solution briefly."""
    lang = "English" if request.language == "en" else "Spanish"
    pain = (
        ", ".join(request.contact.pain_points)
        if request.contact.pain_points
        else "operational inefficiencies"
    )
    proc_name = process.get("name", process_id_to_name(request.process_id))

    return f"""You are Herald, writing on behalf of Alberto Muñoz Waissen (Agentic Zero · Dis-Solutions).
Write a LinkedIn follow-up message.

CONTACT: {request.contact.name} · {request.contact.company} · {request.contact.sector}
THEIR PAIN: {pain}
SOLUTION: {proc_name} — certified AI agent, deploys on existing stack, no ERP migration.

GOAL: Briefly present what was built and how it connects to their pain.
Mention: no migration, works on current infrastructure, certified compliance.
CTA: Free AUDIT — see it working on their real data.

FORMAT: Max 400 characters. Brief and specific.
Language: {lang}
Return ONLY the message text."""


def build_touch4_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    """Touch 4 — Email — ROI + price. Make the decision easy."""
    lang = "English" if request.language == "en" else "Spanish"
    pain = (
        ", ".join(request.contact.pain_points)
        if request.contact.pain_points
        else "operational inefficiencies"
    )

    return f"""You are Herald, writing on behalf of Alberto Muñoz Waissen (Agentic Zero · Dis-Solutions).
Write a final follow-up email with ROI estimate and pricing.

CONTACT: {request.contact.name} · {request.contact.role} · {request.contact.company} · {request.contact.sector}
THEIR PAIN: {pain}

ROI DATA (conservative · defendible):
- {roi["roi12"]}% ROI in 12 months
- Payback in {roi["payback"]} months
- ${roi["annual_saving"]:,} estimated annual saving
- Based on: 3 processes · 3 FTE · {roi["automation_pct"]}% automation rate
- Exact figures calculated during free AUDIT on their real data

PRICING: From $600/month (Standard plan) after AUDIT confirms ROI

GOAL: Give the numbers clearly. Explain the AUDIT removes all risk.
Make the decision obvious: see your ROI for free before committing to anything.

FORMAT:
Line 1: SUBJECT: [subject line]
Line 2: ---
Lines 3+: Email body max 120 words.
3 short paragraphs:
  P1: ROI estimate for their situation (label as estimate, based on 3 processes)
  P2: How the AUDIT works (free, their data, exact numbers, no commitment)
  P3: Price range + CTA: book at agentic-zero.com

Language: {lang}
Sign: Alberto Muñoz Waissen | Agentic Zero | Powered by Dis-Solutions
Return ONLY subject + body."""


def build_sequence_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    lang = "English" if request.language == "en" else "Spanish"
    pain = (
        ", ".join(request.contact.pain_points)
        if request.contact.pain_points
        else "operational inefficiencies"
    )
    history = request.contact.history or "No prior contact"

    return f"""You are Herald, the marketing agent for Agentic Zero.
Write a 4-touch consultative sales sequence for Alberto Muñoz Waissen to send.

This is NOT mass LinkedIn outreach. Alberto is a 25-year expert consultant who writes
like a practitioner who has seen this exact problem in 400 plants across 30 countries.
Every message must feel handwritten, specific, and expert — not templated.

SENDER PROFILE:
{ALBERTO_PROFILE}

CONTACT:
Name: {request.contact.name}
Company: {request.contact.company}
Role: {request.contact.role}
Sector: {request.contact.sector}
History: {history}
SPECIFIC PAIN POINTS (use these — do not ignore them):
{pain}

PROCESS/SOLUTION:
{process.get("name", process_id_to_name(request.process_id))}
{process.get("description", PROCESS_DESCRIPTIONS.get(request.process_id, ""))}

ROI DATA (conservative · defendible):
- {roi["roi12"]}% ROI in 12 months
- Payback in {roi["payback"]} months
- ${roi["annual_saving"]:,} estimated annual saving
- Based on: 3 processes · 3 FTE · {roi["automation_pct"]}% automation rate

MARKET BENCHMARKS:
{MARKET_BENCHMARKS}

EU AI ACT DEADLINE: August 2026

4-TOUCH CONSULTATIVE STRUCTURE:

TOUCH 1 — LinkedIn (Day 1) — RECOGNIZE THE PROBLEM
  Goal: Show you understand THEIR specific pain better than they can articulate it.
  Do NOT pitch. Do NOT mention ROI. Do NOT sell.
  Reference their specific pain points. Ask one sharp question.
  Max 200 chars for connection request OR 500 chars for message.
  End with a question, not a CTA.

TOUCH 2 — Email (Day 4 · if no response) — OFFER PERSPECTIVE
  Goal: Share expert insight from field experience (25 years · 400 plants).
  Describe 2-3 specific consequences of their pain that they may not have quantified.
  Reference a similar situation you have solved (no client names · sector only).
  CTA: 15-minute call to share the approach.
  Max 150 words.

TOUCH 3 — LinkedIn (Day 9 · if no response) — THE SOLUTION
  Goal: Explain what you built and how it works — concisely.
  Mention the agent, what it automates, how it connects to their stack.
  No migration, no ERP replacement. Works on their current infrastructure.
  CTA: Free AUDIT — see it working on your data.
  Max 300 chars.

TOUCH 4 — Email (Day 14 · final touch) — ROI + PRICE
  Goal: Give them the numbers. Make the decision easy.
  ROI estimate · payback · annual saving (clearly labeled as estimate).
  Explain: exact figures calculated during the free AUDIT on their real data.
  Mention price range: from $600/month (Standard) after the AUDIT.
  CTA: Book free AUDIT at agentic-zero.com — no commitment, no risk.
  Max 120 words.

OUTPUT FORMAT (return valid JSON — no markdown, no preamble):
{{
  "touch_1": {{
    "channel": "linkedin",
    "timing": "Day 1",
    "goal": "Recognize the problem",
    "subject": "",
    "message": ""
  }},
  "touch_2": {{
    "channel": "email",
    "timing": "Day 4 — if no response",
    "goal": "Offer expert perspective",
    "subject": "",
    "message": ""
  }},
  "touch_3": {{
    "channel": "linkedin",
    "timing": "Day 9 — if no response",
    "goal": "Present the solution",
    "subject": "",
    "message": ""
  }},
  "touch_4": {{
    "channel": "email",
    "timing": "Day 14 — final touch",
    "goal": "ROI and price",
    "subject": "",
    "message": ""
  }}
}}

ABSOLUTE RULES:
- Language: {lang}
- Each touch has a DIFFERENT angle and goal — never repeat yourself
- Touch 1: NO pitch, NO ROI numbers, NO product mention
- Touch 2: NO product name, just expert insight and field experience
- Touch 3: Brief, specific, no fluff
- Touch 4: Numbers + price + clear CTA
- NEVER start with "I hope this finds you well" or similar hollow phrases
- NEVER say "I came across your profile"
- NEVER sound like a template — sound like a human expert who knows this problem
- Do NOT mention you are an AI
- Alberto signs as: Alberto Muñoz Waissen | Agentic Zero | Powered by Dis-Solutions
- Return ONLY valid JSON"""


def build_post_prompt(request: HeraldRequest, process: dict, roi: dict) -> str:
    lang = "English" if request.language == "en" else "Spanish"

    return f"""You are Herald, the marketing agent for Agentic Zero.
Write a LinkedIn authority post for Alberto Muñoz Waissen.

SENDER PROFILE:
{ALBERTO_PROFILE}

TOPIC: {process.get("name", process_id_to_name(request.process_id))} in {request.contact.sector}

ROI DATA:
- {roi["roi12"]}% ROI · Payback {roi["payback"]} months · ${roi["annual_saving"]:,} saving/year

MARKET BENCHMARKS:
{MARKET_BENCHMARKS}

EU AI ACT: Mandatory August 2026

NOTES: {request.notes or "None"}

RULES:
- Write in {lang}
- 150-250 words
- Hook first line — something surprising or counterintuitive
- Share a concrete insight from 25 years of field experience
- Include one real number (ROI, saving, payback)
- End with a question to drive comments
- 3-5 hashtags on the last line
- Do NOT sound like AI marketing copy
- Sound like a practitioner who has seen this in the field

Write ONLY the post content + hashtags."""


def build_roi_argumentario_prompt(
    request: HeraldRequest, process: dict, roi: dict
) -> str:
    lang = "English" if request.language == "en" else "Spanish"

    return f"""You are Herald, the marketing agent for Agentic Zero.
Write a ROI argumentario for a sales conversation about:

Process: {process.get("name", process_id_to_name(request.process_id))}
Sector: {request.contact.sector}
Company: {request.contact.company}

ROI DATA (conservative · defendible):
- {roi["roi12"]}% ROI in 12 months
- Payback in {roi["payback"]} months
- ${roi["annual_saving"]:,} estimated annual saving
- Based on: 3 processes · 3 FTE · {roi["automation_pct"]}% automation rate

METHODOLOGY (if challenged):
- FTE cost reference: published sector salary benchmarks
- Automation rate: conservative estimate ({roi["automation_pct"]}% vs industry avg 70-80%)
- Agent cost: $12K/year (license + Standard support)
- Exact figures calculated during the free AUDIT on client's real data

MARKET BENCHMARKS:
{MARKET_BENCHMARKS}

Language: {lang}
Format: 5 bullet points max, ready to use in a conversation.
Write ONLY the argumentario."""


def build_audit_proposal_prompt(
    request: HeraldRequest, process: dict, roi: dict
) -> str:
    lang = "English" if request.language == "en" else "Spanish"

    return f"""You are Herald, the marketing agent for Agentic Zero.
Write an AUDIT proposal message for {request.contact.name} at {request.contact.company}.

Context: They have shown interest. Now propose the free AUDIT.

WHAT THE AUDIT IS:
- Free — no cost, no commitment
- 10 days for complex/regulated processes, 24h for standard library processes
- We analyze their operation with their real data
- Output: exact ROI calculation before any buying decision
- If the numbers don't convince, there's no conversation to have

SENDER PROFILE:
{ALBERTO_PROFILE}

CONTACT:
Name: {request.contact.name}
Company: {request.contact.company}
Role: {request.contact.role}
Sector: {request.contact.sector}

NOTES: {request.notes or "None"}

RULES:
- Write in {lang}
- Max 120 words
- Confirm their interest briefly
- Explain AUDIT in one sentence (not a sales pitch)
- Propose 2-3 timing slots (this week / next week)
- Emphasize: ROI calculated on YOUR data, before any commitment
- End with clear YES/NO question
- Do NOT mention you are an AI

Write ONLY the message."""


def process_id_to_name(process_id: str) -> str:
    return PROCESS_DESCRIPTIONS.get(process_id, process_id)


# ── VENTURE INTEGRATION ───────────────────────────────────────────────────────
def load_venture_opportunity(opp_id: str) -> Optional[dict]:
    """Load an opportunity from Venture pipeline."""
    pipeline_file = ROOT / "commercial" / "venture" / "pipeline.json"
    if not pipeline_file.exists():
        return None
    with open(pipeline_file, encoding="utf-8") as f:
        pipeline = json.load(f)
    for opp in pipeline.get("opportunities", []):
        if opp.get("id") == opp_id:
            return opp
    return None


def herald_from_venture(
    opp_id: str, comm_type: str = "first_contact", language: str = "en"
) -> Optional["HeraldOutput"]:
    """Generate Herald output directly from a Venture opportunity."""
    opp = load_venture_opportunity(opp_id)
    if not opp:
        logger.error(f"Venture opportunity not found: {opp_id}")
        return None

    # Build contact from opportunity
    contact = ContactProfile(
        name=opp.get("contact_name", "Decision Maker"),
        company=opp.get("contact_company", opp.get("target", "Target Company")),
        role="Operations Director",
        sector="manufacturing",
        pain_points=[opp.get("description", "")],
        linkedin_url=opp.get("contact_linkedin", ""),
    )

    request = HeraldRequest(
        contact=contact,
        process_id=opp.get("agentic_fit", "SCOR-P1.1").split()[0],
        communication_type=comm_type,
        language=language,
        notes=f"BD Score: {opp.get('bd_score', 0)} | Revenue potential: {opp.get('revenue_potential', '')}",
        venture_opp_id=opp_id,
    )

    return run_herald(request)


# ── HERALD MAIN FUNCTION ──────────────────────────────────────────────────────
def run_herald(request: HeraldRequest) -> HeraldOutput:
    logger.info(
        f"Herald starting: {request.communication_type} for {request.contact.name} ({request.contact.company})"
    )

    process = load_process(request.process_id)
    if not process:
        process = {
            "name": process_id_to_name(request.process_id),
            "description": "Autonomous operations agent",
        }

    roi = ROI_BENCHMARKS.get(request.contact.sector, ROI_BENCHMARKS["manufacturing"])
    request_id = f"HERALD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    primary_message = ""
    email_body = None
    sequence = None
    linkedin_post = None
    linkedin_hashtags = None

    # Generate based on type
    if request.communication_type == "post":
        primary_message = call_llm(build_post_prompt(request, process, roi))

    elif request.communication_type == "email":
        raw = call_llm(build_email_outreach_prompt(request, process, roi))
        # Parse subject + body
        if "---" in raw:
            parts = raw.split("---", 1)
            subject_raw = parts[0].strip()
            email_body = parts[1].strip()
            primary_message = subject_raw.replace("SUBJECT:", "").strip()
        else:
            primary_message = raw
            email_body = raw

    elif request.communication_type == "sequence":
        # Generate each touch separately for quality and reliability
        logger.info("Generating Touch 1 (LinkedIn — Recognize problem)...")
        t1_msg = call_llm(build_touch1_prompt(request, process, roi))

        logger.info("Generating Touch 2 (Email — Expert perspective)...")
        t2_raw = call_llm(build_touch2_prompt(request, process, roi))
        t2_subject, t2_body = ("", t2_raw)
        if "---" in t2_raw:
            parts = t2_raw.split("---", 1)
            t2_subject = parts[0].replace("SUBJECT:", "").strip()
            t2_body = parts[1].strip()

        logger.info("Generating Touch 3 (LinkedIn — The solution)...")
        t3_msg = call_llm(build_touch3_prompt(request, process, roi))

        logger.info("Generating Touch 4 (Email — ROI + price)...")
        t4_raw = call_llm(build_touch4_prompt(request, process, roi))
        t4_subject, t4_body = ("", t4_raw)
        if "---" in t4_raw:
            parts = t4_raw.split("---", 1)
            t4_subject = parts[0].replace("SUBJECT:", "").strip()
            t4_body = parts[1].strip()

        sequence = [
            {
                "touch": "1",
                "channel": "linkedin",
                "timing": "Day 1",
                "goal": "Recognize the problem — no pitch",
                "subject": "LinkedIn message",
                "message": t1_msg,
            },
            {
                "touch": "2",
                "channel": "email",
                "timing": "Day 4 — if no response",
                "goal": "Offer expert perspective",
                "subject": t2_subject,
                "message": t2_body,
            },
            {
                "touch": "3",
                "channel": "linkedin",
                "timing": "Day 9 — if no response",
                "goal": "Present the solution",
                "subject": "LinkedIn follow-up",
                "message": t3_msg,
            },
            {
                "touch": "4",
                "channel": "email",
                "timing": "Day 14 — final touch",
                "goal": "ROI estimate + price",
                "subject": t4_subject,
                "message": t4_body,
            },
        ]
        primary_message = t1_msg

    elif request.communication_type == "audit_proposal":
        primary_message = call_llm(build_audit_proposal_prompt(request, process, roi))

    else:  # first_contact, follow_up — LinkedIn default
        primary_message = call_llm(
            build_linkedin_outreach_prompt(request, process, roi)
        )

    # Always generate ROI argumentario
    logger.info("Generating ROI argumentario...")
    roi_hook = call_llm(build_roi_argumentario_prompt(request, process, roi))

    # Generate LinkedIn post if not already the main output
    if request.communication_type not in ("post", "sequence"):
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

    # Key arguments with updated ROI data
    key_arguments = [
        f"{roi['roi12']}% ROI in 12 months ({request.contact.sector} · conservative estimate)",
        f"Payback in {roi['payback']} months",
        f"${roi['annual_saving']:,} estimated annual saving · 3 processes · 3 FTE basis",
        "Exact ROI calculated on your data during the free AUDIT",
        "EU AI Act compliant by design — mandatory August 2026",
        "Powered by Dis-Solutions · 25 years · $420M value demonstrated",
    ]

    eu_ai_act_angle = (
        f"EU AI Act enforcement begins August 2026. "
        f"High-risk AI in {request.contact.sector} supply chains requires conformity assessment. "
        f"Agentic Zero agents arrive pre-certified — Guardian-verified compliance from day 1."
    )

    cta_map = {
        "first_contact": "15-minute call to show you the ROI numbers for your specific operation",
        "follow_up": "Quick call to walk you through what we built for a similar operation",
        "email": "Book a free AUDIT at agentic-zero.com — ROI calculated before any commitment",
        "sequence": "Free AUDIT — you see the numbers before deciding anything",
        "audit_proposal": "Free AUDIT — ROI calculated on your data, no commitment required",
        "post": "Share your experience with AI in operations in the comments",
    }
    cta = cta_map.get(request.communication_type, cta_map["first_contact"])

    subject_map = {
        "first_contact": f"{roi['roi12']}% ROI · {process_id_to_name(request.process_id)[:40]}",
        "follow_up": f"Following up — autonomous operations for {request.contact.company}",
        "email": primary_message
        if request.communication_type == "email"
        else f"Agentic Zero · {request.contact.company}",
        "sequence": f"3-touch sequence for {request.contact.name} @ {request.contact.company}",
        "audit_proposal": f"Free AUDIT proposal — {request.contact.company}",
        "post": f"LinkedIn post — {process_id_to_name(request.process_id)[:50]}",
    }
    subject = subject_map.get(request.communication_type, "Agentic Zero")

    word_count = len(primary_message.split())
    read_time = max(10, word_count * 3)

    output = HeraldOutput(
        request_id=request_id,
        generated_at=datetime.now().isoformat(),
        communication_type=request.communication_type,
        contact_name=request.contact.name,
        process_id=request.process_id,
        primary_message=primary_message,
        subject_line=subject,
        email_body=email_body,
        sequence=sequence,
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
    output_dir = ROOT / "commercial" / "herald" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{request_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output.model_dump(), f, indent=2, ensure_ascii=False)

    logger.success(f"Herald complete: {request_id} — {word_count} words generated")
    return output


# ── CLI INTERFACE ─────────────────────────────────────────────────────────────
def print_output(output: HeraldOutput):
    print(f"\n{'=' * 60}")
    print(f"HERALD OUTPUT — {output.request_id}")
    print(f"{'=' * 60}")
    print(f"\n📧 SUBJECT / CONTEXT: {output.subject_line}")
    print(f"\n{'─' * 60}")
    print(f"PRIMARY MESSAGE ({output.communication_type.upper()}):")
    print(f"{'─' * 60}")
    print(output.primary_message)

    if output.email_body and output.communication_type == "email":
        print(f"\n{'─' * 60}")
        print(f"EMAIL BODY:")
        print(f"{'─' * 60}")
        print(output.email_body)

    if output.sequence:
        print(f"\n{'─' * 60}")
        print(f"3-TOUCH SEQUENCE:")
        print(f"{'─' * 60}")
        for touch in output.sequence:
            print(f"\n  TOUCH {touch.get('touch')} — {touch.get('timing', '')}")
            print(f"  Channel: {touch.get('channel', '')}")
            if touch.get("subject"):
                print(f"  Subject: {touch.get('subject', '')}")
            print(f"  Goal:    {touch.get('goal', '')}")
        print(f"  Message:\n{touch.get('message', '')}")

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
    print(f"\n📁 Saved: commercial/herald/outputs/{output.request_id}.json")
    print(f"{'=' * 60}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero — Herald Agent v2.0")
    parser.add_argument("--name", required=False, default="", help="Contact name")
    parser.add_argument("--company", required=False, default="", help="Contact company")
    parser.add_argument("--role", default="Operations Director")
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
    )
    parser.add_argument("--process", default="SCOR-P1.1")
    parser.add_argument(
        "--type",
        default="first_contact",
        choices=[
            "first_contact",
            "follow_up",
            "email",
            "sequence",
            "audit_proposal",
            "post",
        ],
        dest="comm_type",
    )
    parser.add_argument("--language", default="en", choices=["es", "en"])
    parser.add_argument(
        "--tone", default="professional", choices=["professional", "warm", "direct"]
    )
    parser.add_argument("--history", default="")
    parser.add_argument(
        "--pain", default="", help="Known pain points (comma-separated)"
    )
    parser.add_argument("--email", default="", help="Contact email address")
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--venture", default="", help="Import from Venture opportunity ID"
    )
    args = parser.parse_args()

    # Venture integration
    if args.venture:
        logger.info(f"Loading from Venture: {args.venture}")
        output = herald_from_venture(args.venture, args.comm_type, args.language)
        if output:
            print_output(output)
        else:
            print(f"❌ Venture opportunity not found: {args.venture}")
        return

    if not args.name or not args.company:
        print("❌ --name and --company required (or use --venture OPP_ID)")
        return

    pain_points = [p.strip() for p in args.pain.split(",")] if args.pain else []

    request = HeraldRequest(
        contact=ContactProfile(
            name=args.name,
            company=args.company,
            role=args.role,
            sector=args.sector,
            history=args.history,
            pain_points=pain_points,
            email=args.email,
        ),
        process_id=args.process,
        communication_type=args.comm_type,
        language=args.language,
        tone=args.tone,
        notes=args.notes,
    )

    logger.info("=" * 60)
    logger.info("AGENTIC ZERO — HERALD AGENT v2.0")
    logger.info(f"Contact: {args.name} @ {args.company} ({args.sector})")
    logger.info(f"Process: {args.process} | Type: {args.comm_type}")
    logger.info("=" * 60)

    output = run_herald(request)
    print_output(output)


if __name__ == "__main__":
    main()
