"""
AGENTIC ZERO — COMMERCIAL ENGINE
Agent: VENTURE
Role: Pipeline Manager & Revenue Tracker
Version: 1.0

Venture manages the commercial pipeline from BD opportunity
to signed AUDIT, and tracks passive income from sold agents.

Philosophy:
  Venture is the bridge between BD (who finds) and Herald (who contacts).
  It knows where every opportunity stands, when to push, and what
  the business is generating. Simple today, scalable tomorrow.

Capabilities v1.0:
  1. Pipeline tracking    — opportunity states from lead to closed
  2. Follow-up engine     — generates Herald sequences on stale deals
  3. AUDIT scheduler      — proposes agenda when opportunity is qualified
  4. Passive income       — tracks MRR/ARR from sold/licensed agents

Usage:
  python venture.py --pipeline              # show full pipeline
  python venture.py --add                   # add opportunity manually
  python venture.py --advance <id>          # advance opportunity stage
  python venture.py --followup              # generate follow-up actions
  python venture.py --revenue               # show MRR/ARR dashboard
  python venture.py --import-bd             # import from BD briefings
"""

import os
import sys
import json
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger
import litellm

load_dotenv()

# ── PATHS ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
while ROOT.name != "agentic-zero" and ROOT.parent != ROOT:
    ROOT = ROOT.parent

VENTURE_DIR = ROOT / "commercial" / "venture"
PIPELINE_FILE = VENTURE_DIR / "pipeline.json"
REVENUE_FILE = VENTURE_DIR / "revenue.json"
FOLLOWUP_DIR = VENTURE_DIR / "followups"
LOG_DIR = ROOT / "logs"

for d in [VENTURE_DIR, FOLLOWUP_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logger.add(
    LOG_DIR / "venture_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | VENTURE | {message}",
)

# ── LLM ───────────────────────────────────────────────────────────────
MODEL = "groq/llama-3.3-70b-versatile"
RPM_WAIT = 61

import time

_last_call = 0.0


def call_llm(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < RPM_WAIT:
        time.sleep(RPM_WAIT - elapsed)
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = litellm.completion(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.6,
        )
        _last_call = time.time()
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        _last_call = time.time()
        raise


# ══════════════════════════════════════════════════════════════════════
# PIPELINE STAGES
# ══════════════════════════════════════════════════════════════════════

STAGES = [
    "lead",  # BD detected, not yet contacted
    "contacted",  # Herald sent first message
    "engaged",  # Prospect responded
    "qualified",  # Pain confirmed, budget likely
    "audit_proposed",  # AUDIT agenda sent
    "audit_scheduled",  # AUDIT confirmed in calendar
    "audit_done",  # AUDIT completed
    "proposal_sent",  # Commercial proposal sent
    "negotiation",  # Active negotiation
    "closed_won",  # Deal signed
    "closed_lost",  # Deal lost
    "on_hold",  # Paused for any reason
]

STAGE_ICONS = {
    "lead": "💡",
    "contacted": "📤",
    "engaged": "💬",
    "qualified": "✅",
    "audit_proposed": "📅",
    "audit_scheduled": "🗓️",
    "audit_done": "🔍",
    "proposal_sent": "📋",
    "negotiation": "🤝",
    "closed_won": "🏆",
    "closed_lost": "❌",
    "on_hold": "⏸️",
}

# Days before an opportunity is considered stale at each stage
STALE_DAYS = {
    "lead": 3,
    "contacted": 5,
    "engaged": 7,
    "qualified": 5,
    "audit_proposed": 4,
    "audit_scheduled": 1,
    "audit_done": 3,
    "proposal_sent": 7,
    "negotiation": 5,
}


# ══════════════════════════════════════════════════════════════════════
# PIPELINE DATA
# ══════════════════════════════════════════════════════════════════════


def load_pipeline() -> dict:
    if PIPELINE_FILE.exists():
        with open(PIPELINE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"opportunities": [], "updated_at": None}


def save_pipeline(pipeline: dict):
    pipeline["updated_at"] = datetime.now().isoformat()
    with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(pipeline, f, indent=2, ensure_ascii=False)


def load_revenue() -> dict:
    if REVENUE_FILE.exists():
        with open(REVENUE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"agents_sold": [], "licenses": [], "audits": [], "updated_at": None}


def save_revenue(revenue: dict):
    revenue["updated_at"] = datetime.now().isoformat()
    with open(REVENUE_FILE, "w", encoding="utf-8") as f:
        json.dump(revenue, f, indent=2, ensure_ascii=False)


def generate_id() -> str:
    return f"opp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def is_stale(opp: dict) -> bool:
    stage = opp.get("stage", "lead")
    if stage in ("closed_won", "closed_lost", "on_hold"):
        return False
    max_days = STALE_DAYS.get(stage, 7)
    last_activity = opp.get("last_activity_at", opp.get("created_at", ""))
    if not last_activity:
        return False
    try:
        last = datetime.fromisoformat(last_activity).date()
        return (date.today() - last).days > max_days
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════
# FOLLOW-UP ENGINE
# ══════════════════════════════════════════════════════════════════════


def generate_followup(opp: dict) -> str:
    """Generate a Herald follow-up action for a stale opportunity."""
    system = """You are Venture, the pipeline manager for Agentic Zero.
You identify stale opportunities and generate specific follow-up actions for Herald.
Be direct, specific, and give Herald exactly what to do next.
Herald sends messages on LinkedIn or email — give the exact message or script."""

    prompt = f"""Today is {date.today().isoformat()}.

This opportunity has gone stale and needs follow-up:

{json.dumps(opp, indent=2)}

Generate a specific follow-up action for Herald.
Include:
1. Which channel to use (LinkedIn / email)
2. The exact message to send (ready to copy-paste)
3. The goal of this follow-up
4. What to do if no response in 3 days

Keep the message short, personalized, and value-focused.
Do NOT mention you are an AI agent."""

    return call_llm(prompt, system=system)


# ══════════════════════════════════════════════════════════════════════
# AUDIT SCHEDULER
# ══════════════════════════════════════════════════════════════════════


def generate_audit_proposal(opp: dict) -> str:
    """Generate AUDIT scheduling message when opportunity is qualified."""
    system = """You are Venture, the pipeline manager for Agentic Zero.
When an opportunity is qualified, you generate the AUDIT scheduling proposal.
The AUDIT is free, no-risk, 10 days max for complex processes.
Generate a professional, confident scheduling message."""

    prompt = f"""Today is {date.today().isoformat()}.

This opportunity is qualified and ready for AUDIT scheduling:

{json.dumps(opp, indent=2)}

Generate the AUDIT scheduling proposal:
1. Short intro confirming their interest
2. What the AUDIT involves (brief, no jargon)
3. Proposed timing (offer 2-3 slots this week or next)
4. What they get at the end (ROI calculated on their data)
5. Clear call to action

Keep it under 150 words. Professional but warm."""

    return call_llm(prompt, system=system)


# ══════════════════════════════════════════════════════════════════════
# IMPORT FROM BD
# ══════════════════════════════════════════════════════════════════════


def import_from_bd() -> int:
    """Import HIGH priority opportunities from BD pipeline."""
    # Read from BD pipeline.json (more reliable than briefings)
    bd_pipeline = ROOT / "commercial" / "bd" / "pipeline.json"
    bd_briefings = ROOT / "commercial" / "bd" / "briefings"

    # Try pipeline first, then briefings
    ops = []
    source_name = ""

    if bd_pipeline.exists():
        with open(bd_pipeline, encoding="utf-8") as f:
            bd_data = json.load(f)
        ops = bd_data.get("opportunities", [])
        source_name = "bd/pipeline.json"
    else:
        briefing_files = (
            sorted(bd_briefings.glob("briefing_*.json"), reverse=True)
            if bd_briefings.exists()
            else []
        )
        if not briefing_files:
            print("⚠️  No BD data found.")
            return 0
        with open(briefing_files[0], encoding="utf-8") as f:
            briefing = json.load(f)
        ops = briefing.get("opportunities", [])
        source_name = briefing_files[0].name

    pipeline = load_pipeline()
    existing_titles = {op.get("title", "").lower() for op in pipeline["opportunities"]}

    high_ops = [
        o for o in ops if (o.get("priority") == "HIGH" or o.get("total_score", 0) >= 70)
    ]

    imported = 0
    for op in high_ops:
        title = op.get("title", "")
        if title.lower() in existing_titles:
            continue
        new_opp = {
            "id": generate_id(),
            "title": title,
            "source": "bd_agent",
            "bd_score": op.get("total_score", 0),
            "description": op.get("description", ""),
            "target": op.get("target", ""),
            "agentic_fit": op.get("agentic_fit", ""),
            "revenue_potential": op.get("revenue_potential", ""),
            "next_action": op.get("next_action", ""),
            "stage": "lead",
            "contact_name": "",
            "contact_company": "",
            "contact_linkedin": "",
            "notes": "",
            "created_at": datetime.now().isoformat(),
            "last_activity_at": datetime.now().isoformat(),
            "stage_history": [{"stage": "lead", "at": datetime.now().isoformat()}],
        }
        pipeline["opportunities"].append(new_opp)
        imported += 1

    save_pipeline(pipeline)
    logger.info(f"Imported {imported} HIGH priority opportunities from {source_name}")
    return imported


# ══════════════════════════════════════════════════════════════════════
# REVENUE TRACKER
# ══════════════════════════════════════════════════════════════════════


def calc_revenue() -> dict:
    revenue = load_revenue()

    # One-time sales
    total_sales = sum(a.get("amount", 0) for a in revenue.get("agents_sold", []))

    # Monthly recurring
    active_licenses = [
        l for l in revenue.get("licenses", []) if l.get("status", "active") == "active"
    ]
    mrr = sum(l.get("monthly_amount", 0) for l in active_licenses)
    arr = mrr * 12

    # AUDIT revenue
    audit_revenue = sum(
        a.get("amount", 0) for a in revenue.get("audits", []) if a.get("type") != "free"
    )

    return {
        "total_sales": total_sales,
        "mrr": mrr,
        "arr": arr,
        "audit_revenue": audit_revenue,
        "total_revenue": total_sales + audit_revenue,
        "active_licenses": len(active_licenses),
    }


# ══════════════════════════════════════════════════════════════════════
# PRINT HELPERS
# ══════════════════════════════════════════════════════════════════════


def print_pipeline():
    pipeline = load_pipeline()
    ops = pipeline.get("opportunities", [])

    if not ops:
        print("\n⚠️  Pipeline is empty. Run --import-bd to load from BD briefings.\n")
        return

    # Group by stage
    by_stage = {}
    for op in ops:
        s = op.get("stage", "lead")
        by_stage.setdefault(s, []).append(op)

    print(f"\n{'═' * 60}")
    print(f"  VENTURE PIPELINE — {date.today().isoformat()}")
    print(f"  Total: {len(ops)} opportunities")
    print(f"{'═' * 60}")

    for stage in STAGES:
        stage_ops = by_stage.get(stage, [])
        if not stage_ops:
            continue
        icon = STAGE_ICONS.get(stage, "·")
        print(f"\n  {icon} {stage.upper().replace('_', ' ')} ({len(stage_ops)})")
        print(f"  {'─' * 50}")
        for op in stage_ops:
            stale = "⚠️ " if is_stale(op) else "   "
            score = op.get("bd_score", 0)
            print(
                f"  {stale}[{score:.0f}] {op.get('id', '?')} — {op.get('title', '?')[:45]}"
            )
            if op.get("contact_name"):
                print(
                    f"       Contact: {op['contact_name']} @ {op.get('contact_company', '?')}"
                )
            print(f"       Revenue: {op.get('revenue_potential', '?')}")
    print()


def print_revenue():
    r = calc_revenue()
    pipeline = load_pipeline()
    ops = pipeline.get("opportunities", [])
    won = [o for o in ops if o.get("stage") == "closed_won"]
    active = [o for o in ops if o.get("stage") not in ("closed_won", "closed_lost")]

    print(f"\n{'═' * 55}")
    print(f"  VENTURE REVENUE DASHBOARD — {date.today().isoformat()}")
    print(f"{'═' * 55}")
    print(f"  💰 Total revenue:      ${r['total_revenue']:,.0f}")
    print(f"  💰 One-time sales:     ${r['total_sales']:,.0f}")
    print(f"  💰 AUDIT revenue:      ${r['audit_revenue']:,.0f}")
    print(f"  📈 MRR:                ${r['mrr']:,.0f}/month")
    print(f"  📈 ARR:                ${r['arr']:,.0f}/year")
    print(f"  🔄 Active licenses:    {r['active_licenses']}")
    print(f"\n  PIPELINE")
    print(f"  {'─' * 45}")
    print(f"  Active opportunities:  {len(active)}")
    print(f"  Closed won:            {len(won)}")
    revenue = load_revenue()
    print(f"  Agents sold:           {len(revenue.get('agents_sold', []))}")
    print(f"{'═' * 55}\n")


# ══════════════════════════════════════════════════════════════════════
# CLI COMMANDS
# ══════════════════════════════════════════════════════════════════════


def cmd_pipeline():
    print_pipeline()


def cmd_add():
    """Manually add an opportunity."""
    print("\n➕ ADD OPPORTUNITY")
    pipeline = load_pipeline()
    opp = {
        "id": generate_id(),
        "title": input("  Title: ").strip(),
        "source": "manual",
        "bd_score": 0,
        "description": input("  Description: ").strip(),
        "target": input("  Target company/person: ").strip(),
        "contact_name": input("  Contact name: ").strip(),
        "contact_company": input("  Company: ").strip(),
        "contact_linkedin": input("  LinkedIn URL (optional): ").strip(),
        "agentic_fit": input("  Which agent fits? (e.g. SCOR-P1.1): ").strip(),
        "revenue_potential": input("  Revenue potential: ").strip(),
        "notes": input("  Notes: ").strip(),
        "stage": "lead",
        "created_at": datetime.now().isoformat(),
        "last_activity_at": datetime.now().isoformat(),
        "stage_history": [{"stage": "lead", "at": datetime.now().isoformat()}],
    }
    pipeline["opportunities"].append(opp)
    save_pipeline(pipeline)
    logger.info(f"Opportunity added: {opp['id']} — {opp['title']}")
    print(f"\n  ✅ Added: {opp['id']} — {opp['title']}\n")


def cmd_advance(opp_id: str):
    """Advance an opportunity to the next stage."""
    pipeline = load_pipeline()
    for opp in pipeline["opportunities"]:
        if opp["id"] == opp_id:
            current = opp.get("stage", "lead")
            if current in ("closed_won", "closed_lost"):
                print(f"⚠️  Opportunity already closed: {current}")
                return
            idx = STAGES.index(current) if current in STAGES else 0
            next_stage = STAGES[min(idx + 1, len(STAGES) - 1)]
            print(f"\n  Current stage: {STAGE_ICONS.get(current, '')} {current}")
            print(f"  Next stage:    {STAGE_ICONS.get(next_stage, '')} {next_stage}")
            confirm = input("  Advance? [y/N]: ").strip().lower()
            if confirm == "y":
                opp["stage"] = next_stage
                opp["last_activity_at"] = datetime.now().isoformat()
                opp.setdefault("stage_history", []).append(
                    {"stage": next_stage, "at": datetime.now().isoformat()}
                )
                save_pipeline(pipeline)
                logger.info(f"Opportunity {opp_id} advanced: {current} → {next_stage}")
                print(f"  ✅ Advanced to: {next_stage}")

                # Auto-generate AUDIT proposal if qualified
                if next_stage == "qualified":
                    print("\n  📅 Generating AUDIT proposal for Herald...")
                    try:
                        proposal = generate_audit_proposal(opp)
                        filename = (
                            FOLLOWUP_DIR / f"audit_proposal_{opp_id}_{date.today()}.txt"
                        )
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(f"AUDIT PROPOSAL — {opp['title']}\n")
                            f.write(f"Generated: {datetime.now().isoformat()}\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(proposal)
                        print(f"  ✅ AUDIT proposal saved: {filename.name}")
                    except Exception as e:
                        print(f"  ⚠️  Could not generate proposal: {e}")
            return
    print(f"⚠️  Opportunity not found: {opp_id}")


def cmd_followup():
    """Generate follow-up actions for stale opportunities."""
    pipeline = load_pipeline()
    ops = pipeline.get("opportunities", [])
    stale = [o for o in ops if is_stale(o)]

    if not stale:
        print("\n✅ No stale opportunities — pipeline is healthy.\n")
        return

    print(f"\n⚠️  {len(stale)} stale opportunities need follow-up\n")
    for opp in stale:
        days = (
            date.today()
            - datetime.fromisoformat(
                opp.get("last_activity_at", opp.get("created_at", ""))
            ).date()
        ).days
        print(f"  · [{opp['id']}] {opp['title'][:45]} — {days} days stale")

    print(f"\n📤 Generating follow-up actions for Herald...\n")
    for opp in stale[:3]:  # max 3 at once
        print(f"  Processing: {opp['title'][:45]}...")
        try:
            followup = generate_followup(opp)
            filename = FOLLOWUP_DIR / f"followup_{opp['id']}_{date.today()}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"FOLLOW-UP — {opp['title']}\n")
                f.write(f"Stage: {opp.get('stage', '?')} | Days stale: {days}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(followup)
            print(f"  ✅ Saved: {filename.name}\n")
        except Exception as e:
            print(f"  ⚠️  Failed: {e}\n")


def cmd_revenue():
    print_revenue()


def cmd_import_bd():
    print("\n📥 Importing HIGH priority opportunities from BD briefings...")
    count = import_from_bd()
    if count > 0:
        print(f"  ✅ Imported {count} new opportunities → pipeline updated")
        print_pipeline()
    else:
        print("  ℹ️  No new opportunities to import.")


def cmd_record_sale(agent_id: str, amount: float, sale_type: str = "one_time"):
    """Record a sale or license."""
    revenue = load_revenue()
    entry = {
        "id": f"sale_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": agent_id,
        "amount": amount,
        "type": sale_type,
        "date": date.today().isoformat(),
    }
    if sale_type == "license":
        entry["monthly_amount"] = amount
        entry["status"] = "active"
        revenue["licenses"].append(entry)
    elif sale_type == "audit":
        revenue["audits"].append(entry)
    else:
        revenue["agents_sold"].append(entry)
    save_revenue(revenue)
    logger.info(f"Sale recorded: {agent_id} — ${amount} ({sale_type})")
    print(f"\n  ✅ Sale recorded: {agent_id} — ${amount:,.0f} ({sale_type})\n")


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agentic Zero — Venture Agent v1.0 (Pipeline & Revenue Manager)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pipeline", action="store_true", help="Show full pipeline")
    group.add_argument("--add", action="store_true", help="Add opportunity manually")
    group.add_argument("--advance", metavar="OPP_ID", help="Advance opportunity stage")
    group.add_argument(
        "--followup", action="store_true", help="Generate follow-ups for stale deals"
    )
    group.add_argument("--revenue", action="store_true", help="Show revenue dashboard")
    group.add_argument(
        "--import-bd",
        action="store_true",
        help="Import from BD briefings",
        dest="import_bd",
    )
    group.add_argument(
        "--record-sale",
        nargs=3,
        metavar=("AGENT_ID", "AMOUNT", "TYPE"),
        help="Record a sale: agent_id amount type(one_time|license|audit)",
        dest="record_sale",
    )
    args = parser.parse_args()

    if args.pipeline:
        cmd_pipeline()
    elif args.add:
        cmd_add()
    elif args.advance:
        cmd_advance(args.advance)
    elif args.followup:
        cmd_followup()
    elif args.revenue:
        cmd_revenue()
    elif args.import_bd:
        cmd_import_bd()
    elif args.record_sale:
        agent_id, amount, sale_type = args.record_sale
        cmd_record_sale(agent_id, float(amount), sale_type)
