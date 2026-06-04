"""
AGENTIC ZERO — COMMERCIAL ENGINE
Agent: BD (Business Development Agent)
Role: Junior BD Engineer — explores, scouts, learns
Version: 1.0

Philosophy:
  BD is a junior BD engineer. Curious, proactive, honest.
  Every day he scans the market, scores opportunities,
  and delivers a prioritized briefing of 5-10 opportunities.
  He learns from feedback and improves over time.

Capabilities v1.0:
  1. Market scan — LinkedIn signals, Medium articles, communities
  2. Opportunity scoring — pain · ROI · timing · fit
  3. Channel intelligence — marketplaces, pricing gaps
  4. Partner detection — white-label, integrators, VARs
  5. Daily briefing — 5-10 prioritized opportunities for Herald

Architecture:
  Open and extensible — new sources, new scoring criteria,
  new output formats can be added without refactoring.
  Logs everything for continuous improvement.

Usage:
  python bd_agent.py --scan          # full daily scan
  python bd_agent.py --briefing      # generate today's briefing
  python bd_agent.py --feedback      # review past opportunities
  python bd_agent.py --status        # show BD pipeline status
"""

import os
import sys
import json
import argparse
from datetime import datetime, date
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

BD_DIR = ROOT / "commercial" / "bd"
BRIEFINGS_DIR = BD_DIR / "briefings"
PIPELINE_FILE = BD_DIR / "pipeline.json"
FEEDBACK_FILE = BD_DIR / "feedback.json"
LOG_DIR = ROOT / "logs"

for d in [BD_DIR, BRIEFINGS_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logger.add(
    LOG_DIR / "bd_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | BD | {message}",
)

# ── LLM ───────────────────────────────────────────────────────────────
MODEL = "groq/llama-3.3-70b-versatile"
RPM_WAIT = 61  # seconds between LLM calls

import time

_last_call = 0.0


def call_llm(prompt: str, system: str = "", max_tokens: int = 2000) -> str:
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < RPM_WAIT:
        wait = RPM_WAIT - elapsed
        logger.debug(f"Rate limiter: waiting {wait:.1f}s")
        time.sleep(wait)
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = litellm.completion(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        _last_call = time.time()
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        _last_call = time.time()
        raise


# ══════════════════════════════════════════════════════════════════════
# MULTI-SOURCE SEARCH ENGINE
# 4 sources: Tavily · Serper · Brave · Reddit (PRAW)
# Falls back gracefully if any key is missing
# ══════════════════════════════════════════════════════════════════════

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")
SERPER_KEY = os.getenv("SERPER_API_KEY", "")
BRAVE_KEY = os.getenv("BRAVE_API_KEY", "")
REDDIT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_SEC = os.getenv("REDDIT_CLIENT_SECRET", "")


def search_tavily(query: str, num_results: int = 5) -> list:
    """Tavily AI search — designed for AI agents, returns rich content."""
    if not TAVILY_KEY:
        return []
    try:
        import urllib.request, json as _json

        payload = _json.dumps(
            {
                "api_key": TAVILY_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": num_results,
                "include_answer": True,
            }
        ).encode()
        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = _json.loads(r.read())
        results = []
        for item in data.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("content", "")[:200],
                    "source": "tavily",
                }
            )
        logger.debug(f"Tavily '{query[:40]}': {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"Tavily failed: {e}")
        return []


def search_serper(query: str, num_results: int = 5) -> list:
    """Serper.dev — Google results via API."""
    if not SERPER_KEY:
        return []
    try:
        import urllib.request, json as _json

        payload = _json.dumps({"q": query, "num": num_results}).encode()
        req = urllib.request.Request(
            "https://google.serper.dev/search",
            data=payload,
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = _json.loads(r.read())
        results = []
        for item in data.get("organic", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", "")[:200],
                    "source": "serper",
                }
            )
        logger.debug(f"Serper '{query[:40]}': {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"Serper failed: {e}")
        return []


def search_brave(query: str, num_results: int = 5) -> list:
    """Brave Search API — independent index."""
    if not BRAVE_KEY:
        return []
    try:
        import urllib.request, urllib.parse, json as _json

        encoded = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"https://api.search.brave.com/res/v1/web/search?q={encoded}&count={num_results}",
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": BRAVE_KEY,
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = _json.loads(r.read())
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("description", "")[:200],
                    "source": "brave",
                }
            )
        logger.debug(f"Brave '{query[:40]}': {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"Brave failed: {e}")
        return []


def search_reddit(query: str, subreddits: list = None, num_results: int = 10) -> list:
    """Reddit via PRAW — real community signals."""
    if not REDDIT_ID or not REDDIT_SEC:
        return []
    try:
        import praw

        reddit = praw.Reddit(
            client_id=REDDIT_ID,
            client_secret=REDDIT_SEC,
            user_agent="agentic-zero-bd/1.0",
        )
        results = []
        subs = subreddits or [
            "passive_income",
            "entrepreneur",
            "automation",
            "n8n",
            "artificial",
            "AIAgents",
            "SideProject",
            "startups",
        ]
        for sub in subs[:4]:
            try:
                for post in reddit.subreddit(sub).search(
                    query, limit=3, sort="relevance"
                ):
                    results.append(
                        {
                            "title": post.title,
                            "snippet": (
                                post.selftext[:200] if post.selftext else post.title
                            ),
                            "source": f"reddit/r/{sub}",
                            "score": post.score,
                            "comments": post.num_comments,
                        }
                    )
            except Exception:
                continue
        logger.debug(f"Reddit '{query[:40]}': {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"Reddit failed: {e}")
        return []


def multi_search(query: str, num_results: int = 4) -> list:
    """Combine all available search sources. Falls back gracefully."""
    all_results = []

    # Tavily first — best for AI analysis
    r = search_tavily(query, num_results)
    all_results.extend(r)

    # Serper — Google coverage
    if len(all_results) < num_results:
        r = search_serper(query, num_results)
        all_results.extend(r)

    # Brave — independent coverage
    if len(all_results) < num_results:
        r = search_brave(query, num_results)
        all_results.extend(r)

    # DuckDuckGo fallback if no keys available
    if not all_results:
        try:
            import urllib.request, urllib.parse, re

            encoded = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            titles = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html)
            for i in range(min(num_results, len(titles))):
                title = re.sub(r"<[^>]+>", "", titles[i]).strip()
                snip = (
                    re.sub(r"<[^>]+>", "", snippets[i]).strip()
                    if i < len(snippets)
                    else ""
                )
                if title:
                    all_results.append(
                        {"title": title, "snippet": snip, "source": "duckduckgo"}
                    )
        except Exception:
            pass

    return all_results[: num_results * 2]


def search_source(source: dict) -> str:
    """Gather real content from all available sources for a given scan source."""
    queries = source.get("search_queries", [])
    source_id = source.get("id", "")
    if not queries:
        return f"Source: {source['name']}. No search queries defined."

    all_results = []

    for query in queries[:3]:
        # Reddit gets special treatment for reddit-specific sources
        if source_id in ["reddit_passive_income", "trending_pain_points"]:
            reddit_results = search_reddit(query)
            for r in reddit_results:
                score = f" [↑{r.get('score', 0)} 💬{r.get('comments', 0)}]"
                all_results.append(
                    f"  [{r['source']}]{score} {r['title']}: {r['snippet'][:150]}"
                )

        # All sources get web search
        results = multi_search(query, num_results=4)
        if results:
            all_results.append(f"Query: '{query}'")
            for r in results:
                all_results.append(
                    f"  [{r['source']}] {r['title']}: {r['snippet'][:150]}"
                )

    # Show which sources are active
    active = []
    if TAVILY_KEY:
        active.append("Tavily")
    if SERPER_KEY:
        active.append("Serper")
    if BRAVE_KEY:
        active.append("Brave")
    if REDDIT_ID:
        active.append("Reddit")
    if not active:
        active.append("DuckDuckGo (fallback)")
    logger.info(f"Search sources active: {', '.join(active)}")

    if not all_results:
        return f"Source: {source['name']}. No results found across all search engines."

    return "\n".join(all_results)


# ══════════════════════════════════════════════════════════════════════
# SCORING ENGINE
# ══════════════════════════════════════════════════════════════════════

SCORING_CRITERIA = {
    "universal_pain": {"weight": 20, "desc": "Problem affects 1000+ businesses"},
    "measurable_roi": {"weight": 20, "desc": "Clear, quantifiable value"},
    "agentic_fit": {"weight": 20, "desc": "Solvable with Agentic Zero stack"},
    "timing": {"weight": 15, "desc": "Urgency or trigger event detected"},
    "market_size": {"weight": 15, "desc": "TAM and accessible segment"},
    "competitive_gap": {"weight": 10, "desc": "No obvious dominant solution"},
}


def score_opportunity(opportunity: dict) -> dict:
    """Score an opportunity using the BD scoring framework."""
    scores = {}
    total = 0
    for criterion, meta in SCORING_CRITERIA.items():
        score = opportunity.get("scores", {}).get(criterion, 5)
        weighted = (score / 10) * meta["weight"]
        scores[criterion] = {"raw": score, "weighted": round(weighted, 1)}
        total += weighted
    opportunity["total_score"] = round(total, 1)
    opportunity["scores_detail"] = scores
    opportunity["priority"] = (
        "HIGH" if total >= 70 else "MEDIUM" if total >= 50 else "LOW"
    )
    return opportunity


# ══════════════════════════════════════════════════════════════════════
# MARKET SCAN ENGINE
# ══════════════════════════════════════════════════════════════════════

SCAN_SOURCES = [
    {
        "id": "medium_passive_income",
        "name": "Medium — Passive income with agents",
        "desc": "Articles about passive income using AI agents, monetizing automation, building and selling agents, agentic economy opportunities. Any industry, any sector.",
        "search_queries": [
            "passive income AI agents 2026",
            "sell AI agents make money",
            "agentic economy opportunities",
            "build once sell many times automation",
            "AI agent marketplace monetization",
        ],
    },
    {
        "id": "linkedin_operations",
        "name": "LinkedIn — Operations & Supply Chain + AI",
        "desc": "Any professional posting about supply chain, operations, or logistics combined with AI, automation, or digital transformation. No sector filter — any industry with operational pain is a target.",
        "search_queries": [
            "supply chain AI automation LinkedIn",
            "operations director AI implementation",
            "logistics automation AI agents",
            "operations bottleneck AI solution",
            "supply chain digital transformation pain",
        ],
    },
    {
        "id": "reddit_passive_income",
        "name": "Reddit — Passive income & automatable problems",
        "desc": "People posting problems that could be packaged and sold as AI agents. r/passive_income, r/entrepreneur, r/automation, r/n8n, r/artificial. Looking for: recurring pain points, manual tasks people hate, problems someone would pay to solve.",
        "search_queries": [
            "site:reddit.com passive income AI agents 2026",
            "site:reddit.com automate sell agent workflow",
            "site:reddit.com problem automate n8n make",
            "site:reddit.com spend hours manual process automate",
        ],
    },
    {
        "id": "marketplace_gaps",
        "name": "Agent Marketplaces — What's selling & what's missing",
        "desc": "AgentHub, AIMarketplace, Upwork, Fiverr — analyze what AI agents are selling, at what price, and most importantly what problems have NO good agent solution yet. Find the gaps.",
        "search_queries": [
            "AgentHub best selling agents 2026",
            "Upwork AI agent automation jobs 2026",
            "AI agent marketplace gaps opportunities",
            "n8n workflow sell marketplace",
        ],
    },
    {
        "id": "whitespace_any_industry",
        "name": "Whitespace detection — Any industry, any process",
        "desc": "Scan for industries or process categories where AI agents could replace manual work but no good solution exists yet. No sector bias — regulated is just one sector among many.",
        "search_queries": [
            "manual process still done humans 2026 automate",
            "industry no AI automation solution yet",
            "repetitive business process no software solution",
            "SME operations manual no automation",
        ],
    },
    {
        "id": "partner_channels",
        "name": "Partner & channel detection",
        "desc": "Consultancies, system integrators, agencies, and VARs looking for AI automation products to resell to their clients. White-label opportunities. Distribution without selling effort.",
        "search_queries": [
            "AI automation reseller partner program 2026",
            "white label AI agents consultancy",
            "system integrator AI automation product",
            "agency resell AI workflow automation",
        ],
    },
    {
        "id": "trending_pain_points",
        "name": "Trending pain points — What people are complaining about",
        "desc": "Real-time scan of what business owners, founders, and operators are frustrated about right now. Twitter/X, HackerNews, ProductHunt, LinkedIn. Fresh pain = fresh opportunity.",
        "search_queries": [
            "founder operations problem frustrated 2026",
            "business owner manual process nightmare",
            "startup operations bottleneck AI",
            "hackernews ask automation agent business",
        ],
    },
]


def scan_source(source: dict, context: dict) -> list:
    """Scan a single source for opportunities using real web search + LLM analysis."""

    # First: get real web content
    web_content = search_source(source)

    system = """You are BD, a junior Business Development agent for Agentic Zero.
Agentic Zero builds certified AI agents for complex, regulated operations.
Our stack: SCOR-certified agents, EU AI Act compliant, NIST AI RMF, ISO/IEC 42001.
Our sweet spot: any company with repetitive, complex or regulated processes.
We sell: individual agents ($699–$7,000), support plans ($600–$1,800/month), Swarm (enterprise).

Your job: identify real business opportunities for Agentic Zero.
Be specific, honest, and prioritize quality over quantity.
If you don't find strong signals, say so — don't invent opportunities."""

    prompt = f"""Today is {date.today().isoformat()}.

Scan this source for Agentic Zero business opportunities.
I have already searched the web for you — use these REAL results as your primary source:

═══ REAL WEB RESULTS ═══
{web_content}
═══════════════════════

SOURCE: {source["name"]}
DESCRIPTION: {source["desc"]}

AGENTIC ZERO CONTEXT:
- Certified agent library: Plan (P1.1-P1.5), Source (S1.1-S1.5), Make (M1.1, M2.1), Deliver (in progress)
- Key differentiators: EU AI Act compliance, NIST AI RMF, 25 years field expertise
- Target: any company with repetitive, complex or regulated processes
- Passive income model: build once, sell multiple times (like the $47K customer support agent example)

Generate 1-3 specific, actionable opportunities from this source.
For each opportunity respond in JSON format:

{{
  "opportunities": [
    {{
      "id": "unique_id",
      "title": "Short opportunity title",
      "source": "{source["id"]}",
      "description": "What the opportunity is and why it matters",
      "target": "Specific type of company or person to approach",
      "trigger": "What signal or event makes this timely",
      "agentic_fit": "Which Agentic Zero agent or capability addresses this",
      "revenue_potential": "Estimated deal size or recurring value",
      "next_action": "Specific first step for Herald to take",
      "scores": {{
        "universal_pain": 1-10,
        "measurable_roi": 1-10,
        "agentic_fit": 1-10,
        "timing": 1-10,
        "market_size": 1-10,
        "competitive_gap": 1-10
      }}
    }}
  ]
}}

Return ONLY valid JSON. No markdown, no preamble."""

    try:
        result = call_llm(prompt, system=system, max_tokens=1500)
        # Clean JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        data = json.loads(result)
        opportunities = data.get("opportunities", [])
        # Score each
        return [score_opportunity(op) for op in opportunities]
    except Exception as e:
        logger.error(f"Scan failed for {source['name']}: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════
# BRIEFING ENGINE
# ══════════════════════════════════════════════════════════════════════


def generate_briefing(opportunities: list) -> dict:
    """Generate the daily BD briefing from scanned opportunities."""

    # Sort by score, take top 10
    sorted_ops = sorted(
        opportunities, key=lambda x: x.get("total_score", 0), reverse=True
    )
    top_ops = sorted_ops[:10]

    system = """You are BD, the Business Development agent for Agentic Zero.
You have scanned the market and found opportunities.
Now generate a concise, actionable daily briefing for Alberto.
Be direct, specific, and prioritize the most promising opportunities.
Format: executive-level, 5 minutes to read, immediately actionable."""

    ops_summary = json.dumps(
        [
            {
                "title": op.get("title"),
                "description": op.get("description"),
                "target": op.get("target"),
                "trigger": op.get("trigger"),
                "agentic_fit": op.get("agentic_fit"),
                "revenue_potential": op.get("revenue_potential"),
                "next_action": op.get("next_action"),
                "score": op.get("total_score"),
                "priority": op.get("priority"),
            }
            for op in top_ops
        ],
        indent=2,
    )

    prompt = f"""Today is {date.today().isoformat()}.

Here are today's top opportunities found by BD:

{ops_summary}

Generate a daily briefing with:
1. Executive summary (2-3 sentences)
2. Top 3 priority actions for today
3. Quick summary of each opportunity (one line each)
4. One market insight or trend worth noting

Keep it sharp. Alberto reads this in 5 minutes.
Respond in JSON:
{{
  "date": "{date.today().isoformat()}",
  "executive_summary": "...",
  "top_3_actions": ["action1", "action2", "action3"],
  "opportunity_summaries": ["op1 summary", "op2 summary", ...],
  "market_insight": "..."
}}

Return ONLY valid JSON."""

    try:
        result = call_llm(prompt, system=system, max_tokens=1000)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        briefing = json.loads(result)
        briefing["opportunities"] = top_ops
        briefing["total_scanned"] = len(opportunities)
        briefing["generated_at"] = datetime.now().isoformat()
        return briefing
    except Exception as e:
        logger.error(f"Briefing generation failed: {e}")
        return {
            "date": date.today().isoformat(),
            "executive_summary": "BD scan completed. Manual review recommended.",
            "opportunities": top_ops,
            "total_scanned": len(opportunities),
            "generated_at": datetime.now().isoformat(),
            "error": str(e),
        }


# ══════════════════════════════════════════════════════════════════════
# PIPELINE MANAGEMENT
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


def add_to_pipeline(opportunities: list):
    pipeline = load_pipeline()
    existing_ids = {op.get("id") for op in pipeline["opportunities"]}
    new_ops = [op for op in opportunities if op.get("id") not in existing_ids]
    pipeline["opportunities"].extend(new_ops)
    save_pipeline(pipeline)
    return len(new_ops)


def save_briefing(briefing: dict):
    filename = BRIEFINGS_DIR / f"briefing_{date.today().isoformat()}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False)
    logger.info(f"Briefing saved: {filename.name}")
    return filename


# ══════════════════════════════════════════════════════════════════════
# FEEDBACK LOOP
# ══════════════════════════════════════════════════════════════════════


def record_feedback(opportunity_id: str, outcome: str, notes: str = ""):
    """Record what happened with an opportunity to improve future scoring."""
    feedback = []
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, encoding="utf-8") as f:
            feedback = json.load(f)
    feedback.append(
        {
            "opportunity_id": opportunity_id,
            "outcome": outcome,  # converted / qualified / not_relevant / in_progress
            "notes": notes,
            "recorded_at": datetime.now().isoformat(),
        }
    )
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)
    logger.info(f"Feedback recorded: {opportunity_id} → {outcome}")


# ══════════════════════════════════════════════════════════════════════
# PRINT HELPERS
# ══════════════════════════════════════════════════════════════════════

PRIORITY_ICONS = {"HIGH": "🔥", "MEDIUM": "⚡", "LOW": "💡"}


def print_briefing(briefing: dict):
    print(f"\n{'═' * 60}")
    print(f"  BD DAILY BRIEFING — {briefing.get('date', 'N/A')}")
    print(f"  Scanned: {briefing.get('total_scanned', 0)} opportunities")
    print(f"{'═' * 60}")

    print(f"\n  📋 EXECUTIVE SUMMARY")
    print(f"  {'─' * 50}")
    print(f"  {briefing.get('executive_summary', 'N/A')}")

    actions = briefing.get("top_3_actions", [])
    if actions:
        print(f"\n  🎯 TOP 3 ACTIONS TODAY")
        print(f"  {'─' * 50}")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")

    insight = briefing.get("market_insight")
    if insight:
        print(f"\n  📈 MARKET INSIGHT")
        print(f"  {'─' * 50}")
        print(f"  {insight}")

    ops = briefing.get("opportunities", [])
    if ops:
        print(f"\n  🔍 OPPORTUNITIES ({len(ops)})")
        print(f"  {'─' * 50}")
        for op in ops:
            icon = PRIORITY_ICONS.get(op.get("priority", "LOW"), "·")
            score = op.get("total_score", 0)
            print(f"\n  {icon} [{score:.0f}] {op.get('title', 'N/A')}")
            print(f"     Target:   {op.get('target', 'N/A')}")
            print(f"     Fit:      {op.get('agentic_fit', 'N/A')}")
            print(f"     Revenue:  {op.get('revenue_potential', 'N/A')}")
            print(f"     Action:   {op.get('next_action', 'N/A')}")

    print(f"\n{'═' * 60}\n")


def print_status():
    pipeline = load_pipeline()
    ops = pipeline.get("opportunities", [])
    high = [o for o in ops if o.get("priority") == "HIGH"]
    medium = [o for o in ops if o.get("priority") == "MEDIUM"]
    low = [o for o in ops if o.get("priority") == "LOW"]

    print(f"\n{'═' * 55}")
    print(f"  BD PIPELINE STATUS")
    print(f"{'═' * 55}")
    print(f"  Total opportunities:  {len(ops)}")
    print(f"  🔥 HIGH priority:     {len(high)}")
    print(f"  ⚡ MEDIUM priority:   {len(medium)}")
    print(f"  💡 LOW priority:      {len(low)}")
    print(f"  Last updated:         {pipeline.get('updated_at', 'Never')}")

    briefings = sorted(BRIEFINGS_DIR.glob("briefing_*.json"), reverse=True)
    print(f"  Briefings generated:  {len(briefings)}")
    if briefings:
        print(f"  Latest briefing:      {briefings[0].stem}")
    print(f"{'═' * 55}\n")


# ══════════════════════════════════════════════════════════════════════
# MAIN COMMANDS
# ══════════════════════════════════════════════════════════════════════


def cmd_scan():
    """Full daily market scan across all sources."""
    logger.info("BD daily scan starting...")
    print(f"\n🔍 BD scanning market — {date.today().isoformat()}")
    print(f"   Sources: {len(SCAN_SOURCES)}")
    print(f"   This takes ~{len(SCAN_SOURCES)} minutes (rate limiter)\n")

    all_opportunities = []
    for i, source in enumerate(SCAN_SOURCES, 1):
        print(f"   [{i}/{len(SCAN_SOURCES)}] Scanning: {source['name']}...")
        try:
            ops = scan_source(source, {})
            all_opportunities.extend(ops)
            high = [o for o in ops if o.get("priority") == "HIGH"]
            print(
                f"         → {len(ops)} opportunities found ({len(high)} HIGH priority)"
            )
            logger.info(f"Source scanned: {source['name']} → {len(ops)} opportunities")
        except Exception as e:
            print(f"         → ⚠️  Failed: {e}")
            logger.error(f"Source scan failed: {source['name']}: {e}")

    # Add to pipeline
    new_count = add_to_pipeline(all_opportunities)
    print(
        f"\n   ✅ Scan complete: {len(all_opportunities)} opportunities found, {new_count} new"
    )

    # Generate briefing
    print(f"\n📋 Generating daily briefing...")
    briefing = generate_briefing(all_opportunities)
    briefing_file = save_briefing(briefing)
    print_briefing(briefing)
    print(f"   Briefing saved: {briefing_file}")
    logger.info(
        f"Daily scan complete: {len(all_opportunities)} opportunities, briefing saved"
    )


def cmd_briefing():
    """Generate briefing from existing pipeline (no new scan)."""
    pipeline = load_pipeline()
    ops = pipeline.get("opportunities", [])
    if not ops:
        print("⚠️  No opportunities in pipeline. Run --scan first.")
        return
    print(f"\n📋 Generating briefing from {len(ops)} pipeline opportunities...")
    briefing = generate_briefing(ops)
    save_briefing(briefing)
    print_briefing(briefing)


def cmd_feedback():
    """Interactive feedback on past opportunities."""
    pipeline = load_pipeline()
    ops = pipeline.get("opportunities", [])
    if not ops:
        print("⚠️  No opportunities in pipeline.")
        return
    print(f"\n📊 BD FEEDBACK — {len(ops)} opportunities in pipeline")
    print("Outcomes: [c]onverted / [q]ualified / [n]ot_relevant / [p]ending\n")
    for op in ops[:5]:  # Show top 5
        print(f"  [{op.get('total_score', 0):.0f}] {op.get('title', 'N/A')}")
        outcome = input(f"  Outcome (c/q/n/p) [Enter to skip]: ").strip().lower()
        if outcome in ["c", "q", "n", "p"]:
            outcome_map = {
                "c": "converted",
                "q": "qualified",
                "n": "not_relevant",
                "p": "pending",
            }
            notes = input("  Notes (optional): ").strip()
            record_feedback(op.get("id", ""), outcome_map[outcome], notes)
            print(f"  ✅ Recorded: {outcome_map[outcome]}\n")


def cmd_status():
    print_status()


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agentic Zero — BD Agent v1.0 (Junior Business Development Engineer)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--scan", action="store_true", help="Full daily market scan + briefing"
    )
    group.add_argument(
        "--briefing", action="store_true", help="Generate briefing from pipeline"
    )
    group.add_argument(
        "--feedback", action="store_true", help="Record outcomes on opportunities"
    )
    group.add_argument("--status", action="store_true", help="Show pipeline status")
    args = parser.parse_args()

    if args.scan:
        cmd_scan()
    elif args.briefing:
        cmd_briefing()
    elif args.feedback:
        cmd_feedback()
    elif args.status:
        cmd_status()
