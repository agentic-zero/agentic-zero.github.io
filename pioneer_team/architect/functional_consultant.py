# pioneer_team/architect/functional_consultant.py

"""
AGENTIC ZERO - PIONEER TEAM
Functional Consultant v1.0

Role:
  THE single most important role in the agentic team, per explicit
  product direction (26 Jun 2026): the senior business/functional
  consultant who reads a client's audit - in their own colloquial,
  non-functional language - and produces:

    1. A real functional translation (process flow, business rules,
       exceptions, systems, KPIs) - what functional_translator.py used
       to do alone, with a cheap/fast LLM (Groq Llama).
    2. The tier/route decision (Essential / Standard-Swarm /
       Enterprise-Agentic One) - what intent_classifier.py used to do
       as a SEPARATE step.
    3. Which organisms are needed - matched against the known process
       library (SCOR/BPMN-grounded templates), or genuinely synthesized
       with real content when the client's need isn't covered yet.

  These three were artificially split across two disconnected modules
  using a cheap LLM tier. They are ONE judgment call a real consultant
  makes in a single coherent read of the client's situation - so this
  module makes them together, in one reasoning pass, using the most
  capable model available (Claude, not a cheap/fast tier), because this
  is the highest-leverage decision in the entire commercial pipeline:
  get it wrong, and a client who needed a coordinated Swarm gets sold
  a single linear agent instead, or vice versa.

Why Claude, not Groq/Llama (used elsewhere in this codebase for
cheaper, narrower tasks like scout.py's framework research):
  Detecting "this client described an S&OP need without ever using the
  words S&OP" requires genuine reasoning about business shape, not
  pattern completion. As Claude models improve (Sonnet 4.6 and beyond),
  this module's quality improves with zero code changes - the model
  string is the only thing that needs to move forward.

Design:
  1. PRIMARY: Claude (Anthropic API directly, not litellm/Groq - this
     role is too important for a routing layer in between). Reads the
     full raw client input (AUDIT ZERO + Fast Track + any documentation
     text) and reasons explicitly, like a consultant would, before
     committing to a structured decision.

  2. FALLBACK: deterministic keyword matching (reuses
     enterprise_architect.classify_intent() unchanged) - used only when
     no ANTHROPIC_API_KEY is configured or the API call fails. This is
     a genuinely degraded mode, not an equal alternative - it is kept
     only so the pipeline never hard-stops when a key is misconfigured,
     not because it does the same job.

Output:
  00_enterprise_intent/functional_consultant_result.json
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from typing import Any, Optional

try:
    import anthropic
except Exception:
    anthropic = None

FUNCTIONAL_CONSULTANT_CONFIG = {
    "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
    "max_tokens": 16000,
}


@dataclass
class OrganismSpec:
    template_key: str  # "" if synthesized (not from the existing library)
    name: str
    organism: str
    agent_type: str
    domain: str
    purpose: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    systems: list[str] = field(default_factory=list)
    synthesized: bool = False  # True = LLM proposed this, not from library
    needs_human_review: bool = False  # True for any synthesized organism


@dataclass
class ConsultantResult:
    consultation_id: str
    created_at: str
    method: str  # "claude" or "deterministic_fallback"
    route: str  # PROCESS_AGENT | COMPLEX_PROCESS_AGENT | SWARM | AGENTIC_ONE_ENTERPRISE
    tier: str
    confidence: float
    rationale: str
    level_1_process: str
    organisms: list[OrganismSpec]
    missing_information: list[dict[str, str]] = field(default_factory=list)
    company: str = ""
    sector: str = ""
    erp: str = ""
    process_flow_steps: list[dict[str, Any]] = field(default_factory=list)
    decision_rules: list[str] = field(default_factory=list)
    exception_rules: list[str] = field(default_factory=list)
    approval_rules: list[str] = field(default_factory=list)
    kpis: list[str] = field(default_factory=list)
    autonomous_actions: list[str] = field(default_factory=list)
    approval_required: list[str] = field(default_factory=list)
    always_human: list[str] = field(default_factory=list)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "process").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "process"


def _upper_slug(value: str) -> str:
    return _slug(value).upper()


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def build_known_organism_catalog() -> list[dict[str, Any]]:
    """
    Merges siop_decomposer.py's PROCESS_TEMPLATES and
    enterprise_architect.py's DOMAIN_TEMPLATES into one deduplicated
    catalog (by organism name) - this is given to the LLM as "here is
    what we already know how to build", so it only proposes a NEW
    organism when the client's need genuinely isn't covered.

    Imported lazily and defensively: this module must still work (in
    deterministic-fallback mode) even if one of the two source modules
    has a bug or is mid-edit - a broken catalog build should degrade,
    not crash, classification entirely.
    """
    catalog: dict[str, dict[str, Any]] = {}

    try:
        from siop_decomposer import PROCESS_TEMPLATES

        for key, t in PROCESS_TEMPLATES.items():
            catalog[t["organism"]] = {
                "template_key": key,
                "name": t["name"],
                "organism": t["organism"],
                "agent_type": t["agent_type"],
                "domain": t["domain"],
                "purpose": t["purpose"],
            }
    except Exception:
        pass

    try:
        from enterprise_architect import DOMAIN_TEMPLATES

        for key, t in DOMAIN_TEMPLATES.items():
            catalog.setdefault(
                t["organism"],
                {
                    "template_key": key,
                    "name": t["name"],
                    "organism": t["organism"],
                    "agent_type": t["agent_type"],
                    "domain": t["domain"],
                    "purpose": t["purpose"],
                },
            )
    except Exception:
        pass

    return list(catalog.values())


def build_consultant_prompt(client_text: str, catalog: list[dict[str, Any]]) -> str:
    catalog_json = json.dumps(catalog, indent=2, ensure_ascii=False)

    return f"""You are a senior business and functional consultant at a company that builds AI agents and agent swarms for supply chain and operations. A prospective client has just described their need - in their own words, often informally, in Spanish or English, almost never using formal methodology names (S&OP, IBP, Control Tower...) even when that IS exactly the shape of what they need.

Your job, exactly as a senior consultant would do it in a real discovery call, has THREE parts done together, not separately:
  1. Understand the actual business need behind their words - what are they really trying to achieve, what's the process flow, what could go wrong (exceptions), what would success look like (KPIs).
  2. Decide the right scope: one focused agent for one process (Essential), a coordinated set of agents because their need genuinely spans multiple interconnected domains (Standard - Swarm), or true whole-company autonomy (Enterprise - Agentic One). This is about the SHAPE of their need, never about which buzzwords they used.
  3. If multiple domains are needed, name them - reusing what we already know how to build whenever it genuinely matches, and describing something new and real (not generic) whenever it doesn't.

CLIENT'S DESCRIBED NEED (verbatim, may be colloquial, may be incomplete):
{client_text[:6000]}

ORGANISMS WE ALREADY KNOW HOW TO BUILD (reuse by exact "organism" name whenever it genuinely matches - never invent a duplicate of something already here):
{catalog_json}

Think it through first, like you would before writing up a real discovery call summary: what does this client actually need, why, what's missing from what they told you that you'd want to ask in a follow-up, and why this scope (not a bigger or smaller one) is the right call. Write that reasoning freely.

Then, after a line that says exactly "## FINAL_DECISION", output ONLY this JSON (no markdown fence content outside the JSON itself, no trailing commentary):

{{
  "route": "PROCESS_AGENT|COMPLEX_PROCESS_AGENT|SWARM|AGENTIC_ONE_ENTERPRISE",
  "level_1_process": "short name for the overall need",
  "company": "client company name if mentioned, else empty string",
  "sector": "client's industry/sector if mentioned or clearly implied, else empty string",
  "erp": "client's named system (SAP, Excel, none mentioned, etc.) if mentioned, else empty string",
  "confidence": 0.0,
  "rationale": "one or two sentences, must reference the client's own words/situation, not generic boilerplate",
  "missing_information": [
    {{"field": "specific thing to ask the client", "reason": "why it matters", "severity": "low|medium|high|critical"}}
  ],
  "process_flow_steps": [
    {{
      "step_id": "STEP-01",
      "name": "short step name",
      "system": "system this step touches, only if the client mentioned or clearly implied one - otherwise empty string, never invented",
      "inputs": ["what comes into this step"],
      "outputs": ["what comes out of this step"],
      "rule": "the concrete rule/threshold/check at this step - quote the client's own numbers/criteria if they gave any",
      "confidence": 0.0
    }}
  ],
  "decision_rules": ["concrete rules the agent should apply when deciding routine outcomes"],
  "exception_rules": ["concrete conditions that mean something is wrong and needs special handling"],
  "approval_rules": ["concrete conditions that require a human to approve before proceeding"],
  "kpis": ["what success looks like for this client, in their terms"],
  "autonomous_actions": ["things the agent can safely do without asking anyone, given what the client described"],
  "approval_required": ["things the agent should draft/propose but a human must approve"],
  "always_human": ["things that should never be automated for this client, even partially"],
  "matched_organisms": ["exact organism name from the catalog", "..."],
  "new_organisms": [
    {{
      "name": "",
      "organism": "X Organism",
      "domain": "",
      "purpose": "",
      "inputs": [],
      "outputs": [],
      "systems": []
    }}
  ]
}}"""


def _extract_final_decision_json(raw_response: str) -> dict[str, Any]:
    """
    The prompt deliberately invites free reasoning before the decision
    (a real consultant thinks before concluding) - this extracts only the
    JSON after the "## FINAL_DECISION" marker, instead of assuming the
    whole response is JSON (which would break the moment the model
    reasons out loud, which is exactly what we asked it to do).
    """
    marker = "## FINAL_DECISION"
    if marker in raw_response:
        raw_response = raw_response.split(marker, 1)[1]

    raw_response = raw_response.strip()
    if raw_response.startswith("```"):
        lines = raw_response.split("\n")
        raw_response = "\n".join(lines[1:-1])

    # If there's still leading/trailing prose around the JSON object,
    # take the substring from the first '{' to the last '}'.
    start = raw_response.find("{")
    end = raw_response.rfind("}")
    if start != -1 and end != -1:
        raw_response = raw_response[start : end + 1]

    return json.loads(raw_response)


def call_claude(prompt: str) -> tuple[str, int, int]:
    """
    Calls Claude directly via the Anthropic API - not through litellm/Groq.
    This is the one role in the whole pipeline deliberately wired to the
    best available reasoning model, not the cheap/fast tier used for
    framework research (scout.py) or simple translation
    (functional_translator.py's original scope). As Claude models improve
    (Sonnet 4.6 and beyond), this function's quality improves with zero
    other code changes - only FUNCTIONAL_CONSULTANT_CONFIG["model"] (env
    var ANTHROPIC_MODEL) ever needs to move forward.

    Returns (content, input_tokens, output_tokens) - the token counts come
    straight from the Anthropic API response (response.usage), not an
    estimate, so saas/token_governance.py can record real spend, not a
    guess, for the single highest-value LLM call in this platform.
    """
    if anthropic is None:
        raise RuntimeError("anthropic package not installed.")

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=FUNCTIONAL_CONSULTANT_CONFIG["model"],
        max_tokens=FUNCTIONAL_CONSULTANT_CONFIG["max_tokens"],
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.content[0].text.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    return content, response.usage.input_tokens, response.usage.output_tokens


def _tier_for_route(route: str) -> str:
    return {
        "PROCESS_AGENT": "Essential",
        "COMPLEX_PROCESS_AGENT": "Standard",
        "SWARM": "Standard",
        "AGENTIC_ONE_ENTERPRISE": "Enterprise",
    }.get(route, "Essential")


def _organism_from_catalog_entry(entry: dict[str, Any]) -> OrganismSpec:
    return OrganismSpec(
        template_key=entry.get("template_key", ""),
        name=entry.get("name", ""),
        organism=entry.get("organism", ""),
        agent_type=entry.get("agent_type", ""),
        domain=entry.get("domain", ""),
        purpose=entry.get("purpose", ""),
        synthesized=False,
        needs_human_review=False,
    )


def _client_id_from_package_dir(package_dir: str | Path) -> str:
    """
    package_dir follows the convention clients/<client>/<process>/
    essential_package - the real per-client identifier is the segment
    right after "clients", not the whole path slugified (which would be
    unreadable) and not just the last path component (which would be
    "essential_package" for EVERY client, useless as an identifier).
    Falls back to slugifying the whole path if that convention isn't
    found, so this never crashes on an unexpected path shape.
    """
    parts = Path(package_dir).parts
    if "clients" in parts:
        idx = parts.index("clients")
        if idx + 1 < len(parts):
            return _upper_slug(parts[idx + 1])
    return _upper_slug(str(package_dir)) or "_PROSPECTIVE_LEAD"


def claude_consult(client_text: str, package_dir: str | Path) -> ConsultantResult:
    catalog = build_known_organism_catalog()
    prompt = build_consultant_prompt(client_text, catalog)
    raw, input_tokens, output_tokens = call_claude(prompt)

    try:
        raw_path = Path(package_dir) / "00_enterprise_intent" / "claude_raw_response.txt"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(raw, encoding="utf-8")
    except Exception:
        pass

    parsed = _extract_final_decision_json(raw)

    try:
        from saas.token_governance import TokenGovernance

        TokenGovernance().record_usage(
            client_id=_client_id_from_package_dir(package_dir),
            provider="anthropic",
            model=FUNCTIONAL_CONSULTANT_CONFIG["model"],
            component="functional_consultant",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    except Exception:
        # Recording spend must never block the single most important
        # consultation in the pipeline - same fail-open-for-observability
        # principle used everywhere else in this codebase. A budget
        # mechanic should never be the reason a client's need goes
        # unclassified.
        pass

    by_organism_name = {c["organism"]: c for c in catalog}

    organisms: list[OrganismSpec] = []
    for org_name in parsed.get("matched_organisms", []):
        entry = by_organism_name.get(org_name)
        if entry:
            organisms.append(_organism_from_catalog_entry(entry))

    for new_org in parsed.get("new_organisms", []):
        name = new_org.get("name") or new_org.get("organism", "New Process")
        organisms.append(
            OrganismSpec(
                template_key="",
                name=name,
                organism=new_org.get("organism") or f"{name} Organism",
                agent_type=f"{_slug(name)}_agent",
                domain=new_org.get("domain", "operations"),
                purpose=new_org.get("purpose", ""),
                inputs=new_org.get("inputs", []),
                outputs=new_org.get("outputs", []),
                systems=new_org.get("systems", []),
                synthesized=True,
                needs_human_review=True,
            )
        )

    route = parsed.get("route", "PROCESS_AGENT")
    level_1 = parsed.get("level_1_process", "Customer Process")

    return ConsultantResult(
        consultation_id=f"CONSULT-{_upper_slug(level_1)}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        method="claude",
        route=route,
        tier=_tier_for_route(route),
        confidence=float(parsed.get("confidence", 0.7)),
        rationale=parsed.get("rationale", ""),
        level_1_process=level_1,
        organisms=organisms,
        missing_information=parsed.get("missing_information", []),
        company=parsed.get("company", ""),
        sector=parsed.get("sector", ""),
        erp=parsed.get("erp", ""),
        process_flow_steps=parsed.get("process_flow_steps", []),
        decision_rules=parsed.get("decision_rules", []),
        exception_rules=parsed.get("exception_rules", []),
        approval_rules=parsed.get("approval_rules", []),
        kpis=parsed.get("kpis", []),
        autonomous_actions=parsed.get("autonomous_actions", []),
        approval_required=parsed.get("approval_required", []),
        always_human=parsed.get("always_human", []),
    )


def deterministic_fallback_consult(siop: dict[str, Any], package_dir: str | Path) -> ConsultantResult:
    """
    Fallback when no LLM is available. Reuses enterprise_architect.py's
    classify_intent() + decompose_siop() UNCHANGED - this module does not
    duplicate that keyword-matching logic, it only wraps it in the same
    ConsultantResult shape so callers don't need to care which method
    ran.
    """
    from enterprise_architect import classify_intent, decompose_siop

    classification = classify_intent(siop, package_dir)
    decomposition = decompose_siop(siop, classification)

    # enterprise_architect.py's own classify_intent() tags SWARM as tier
    # "Enterprise" internally - inconsistent with this platform's actual
    # tier structure (Standard = 3+ interconnected agents / full Swarm,
    # Enterprise = Agentic One / whole-company autonomy). _tier_for_route()
    # is the single source of truth for route->tier here so both the LLM
    # path and this fallback always agree, regardless of what
    # enterprise_architect.py's own (inconsistent) tier field says.
    tier = _tier_for_route(classification.route)

    organisms = [
        OrganismSpec(
            template_key=l2.agent_type,
            name=l2.name,
            organism=l2.organism,
            agent_type=l2.agent_type,
            domain=l2.domain,
            purpose=l2.purpose,
            inputs=l2.inputs,
            outputs=l2.outputs,
            systems=l2.systems,
            synthesized=False,
            needs_human_review=False,
        )
        for l2 in decomposition.level_2_siops
    ]

    return ConsultantResult(
        consultation_id=classification.intent_id,
        created_at=_now(),
        method="deterministic_fallback",
        route=classification.route,
        tier=tier,
        confidence=classification.confidence,
        rationale=classification.rationale
        + " (deterministic keyword fallback - no LLM available; cannot propose organisms outside the known template list)",
        level_1_process=classification.level_1_process,
        organisms=organisms,
    )


def consult_on_intent(
    client_text: str,
    siop: dict[str, Any],
    package_dir: str | Path,
    use_llm: bool = True,
) -> ConsultantResult:
    result: Optional[ConsultantResult] = None

    if use_llm and os.getenv("ANTHROPIC_API_KEY") and anthropic is not None:
        try:
            result = claude_consult(client_text, package_dir)
        except Exception:
            result = None  # fall through to deterministic below

    if result is None:
        result = deterministic_fallback_consult(siop, package_dir)

    out_dir = Path(package_dir) / "00_enterprise_intent"
    write_json(out_dir / "functional_consultant_result.json", asdict(result))

    try:
        from consultant_accountability import log_consultation

        log_consultation(result, client_id_hint=str(package_dir))
    except Exception:
        # Same fail-open-for-observability principle as the rest of
        # security/ - a logging gap must never break the consultation
        # the caller already has.
        pass

    return result


def materialize_level2_siops(
    result: ConsultantResult, parent_process: str, detection: dict[str, Any]
) -> list[Any]:
    """
    Converts a ConsultantResult's organisms into real Level2SIOP objects
    ready for the validated swarm pipeline (swarm_topology_validator.py ->
    swarm_splitter.py -> ... -> swarm_generator.py).

    Critical distinction from just reusing OrganismSpec directly: for a
    MATCHED (non-synthesized) organism, this looks up the FULL original
    template (siop_decomposer.PROCESS_TEMPLATES or
    enterprise_architect.DOMAIN_TEMPLATES) by template_key - not the thin
    catalog entry built for the LLM prompt, which only carries
    name/organism/domain/purpose to keep token usage low. Using the thin
    entry directly would silently produce an organism with empty
    inputs/outputs/systems/autonomy_design even though the real template
    has rich content. Only SYNTHESIZED organisms (genuinely new, no
    template_key) use the LLM's own inputs/outputs/systems content.
    """
    from siop_decomposer import (
        PROCESS_TEMPLATES as siop_templates,
        build_level2_siop as siop_build,
    )

    try:
        from enterprise_architect import DOMAIN_TEMPLATES as arch_templates
    except Exception:
        arch_templates = {}

    by_organism_to_key: dict[str, tuple[str, str]] = {}
    for key, t in siop_templates.items():
        by_organism_to_key[t["organism"]] = ("siop_decomposer", key)
    for key, t in arch_templates.items():
        by_organism_to_key.setdefault(t["organism"], ("enterprise_architect", key))

    level2_siops: list[Any] = []

    for org in result.organisms:
        source_key = by_organism_to_key.get(org.organism)

        if not org.synthesized and source_key:
            source, key = source_key
            if source == "siop_decomposer":
                l2 = siop_build(key, parent_process, detection)
                if l2:
                    level2_siops.append(l2)
                    continue
            # enterprise_architect templates are thinner (no
            # scor/bpmn/frameworks/learning_hooks) - build a Level2SIOP
            # with what they do have rather than silently dropping them.
            t = arch_templates.get(key, {})
            level2_siops.append(
                _build_level2_from_dict(
                    siop_id=f"{_upper_slug(parent_process)}-{_upper_slug(t.get('name', org.name))}",
                    parent_process=parent_process,
                    name=t.get("name", org.name),
                    organism=t.get("organism", org.organism),
                    agent_type=t.get("agent_type", org.agent_type),
                    domain=t.get("domain", org.domain),
                    purpose=t.get("purpose", org.purpose),
                    inputs=t.get("inputs", []),
                    outputs=t.get("outputs", []),
                    systems=t.get("systems", []),
                    autonomous_actions=[],
                    approval_required=[],
                    always_human=[],
                )
            )
            continue

        # Synthesized (genuinely new) organism - use the LLM's own
        # content. Conservative autonomy_design: nothing autonomous,
        # everything requires approval, since this organism has no
        # researched/validated business rules behind it yet.
        level2_siops.append(
            _build_level2_from_dict(
                siop_id=f"{_upper_slug(parent_process)}-{_upper_slug(org.name)}",
                parent_process=parent_process,
                name=org.name,
                organism=org.organism,
                agent_type=org.agent_type,
                domain=org.domain,
                purpose=org.purpose,
                inputs=org.inputs,
                outputs=org.outputs,
                systems=org.systems,
                autonomous_actions=[],
                approval_required=[f"any {org.name.lower()} action (synthesized organism, unreviewed)"],
                always_human=[f"all {org.name.lower()} decisions until a human reviews this organism"],
            )
        )

    return level2_siops


def _build_level2_from_dict(**kwargs: Any) -> Any:
    from siop_decomposer import Level2SIOP

    return Level2SIOP(
        siop_id=kwargs["siop_id"],
        parent_process=kwargs["parent_process"],
        name=kwargs["name"],
        organism=kwargs["organism"],
        agent_type=kwargs["agent_type"],
        domain=kwargs["domain"],
        purpose=kwargs["purpose"],
        inputs=kwargs.get("inputs", []),
        outputs=kwargs.get("outputs", []),
        systems=kwargs.get("systems", []),
        autonomy_design={
            "autonomous_actions": kwargs.get("autonomous_actions", []),
            "approval_required": kwargs.get("approval_required", []),
            "always_human": kwargs.get("always_human", []),
        },
        acceptance_criteria=[
            "Inputs are validated before action.",
            "Outputs are traceable.",
            "Low-confidence decisions are escalated.",
            "All decisions emit audit and learning events.",
        ],
        learning_hooks={
            "observation_points": [
                f"{kwargs['agent_type']}_started",
                f"{kwargs['agent_type']}_completed",
                f"{kwargs['agent_type']}_exception",
                f"{kwargs['agent_type']}_confidence_drop",
            ],
            "failure_patterns": ["missing_input", "conflicting_recommendation", "low_confidence", "late_signal"],
            "kpi_deviation_signals": ["service_deviation", "cost_deviation", "time_deviation", "risk_score_increase"],
            "feedback_targets": [kwargs["agent_type"], "swarm_coordinator", "the_machine"],
            "improvement_loop": ["observe", "store_episode", "detect_pattern", "recommend_improvement", "update_shield_rule_if_validated"],
        },
    )


def build_siop_internal(result: ConsultantResult) -> dict[str, Any]:
    """
    Assembles a real siop_internal.json - the exact schema
    architect_siop_bridge.py reads (confirmed field-by-field against its
    siop_to_blueprint() function: executive_summary, business_context,
    process_flow, business_rules as 3 categorized lists - not a flat
    list, autonomy_design with thresholds, acceptance_criteria,
    learning_hooks, missing_information, ready_for_architect).

    Use this for the PROCESS_AGENT / COMPLEX_PROCESS_AGENT route - the
    single-agent path. For SWARM / AGENTIC_ONE_ENTERPRISE, each
    organism gets its own siop-equivalent via materialize_level2_siops()
    instead (different schema, the one swarm_splitter.py expects).

    This is the consultant producing the SIOP directly - not delegating
    to the older Groq-based siop_generator.py. ready_for_architect is
    only True when confidence clears a reasonable bar and there is at
    least one process_flow_step - a consultation that produced nothing
    usable should never silently claim readiness.
    """
    ready = result.confidence >= 0.6 and len(result.process_flow_steps) > 0

    siop = {
        "siop_id": f"SIOP-{_upper_slug(result.level_1_process)}-{result.consultation_id.split('-')[-1]}",
        "source_functional_analysis_id": result.consultation_id,
        "executive_summary": {
            "process_name": result.level_1_process,
            "validated_description": result.rationale,
        },
        "business_context": {
            "company": result.company,
            "sector": result.sector,
            "erp": result.erp,
            "volume": "",
        },
        "process_flow": result.process_flow_steps,
        "data_requirements": {
            "input_objects": list(
                dict.fromkeys(i for s in result.process_flow_steps for i in s.get("inputs", []))
            ),
            "output_objects": list(
                dict.fromkeys(o for s in result.process_flow_steps for o in s.get("outputs", []))
            ),
        },
        "business_rules": {
            "decision_rules": result.decision_rules,
            "exception_rules": result.exception_rules,
            "approval_rules": result.approval_rules,
        },
        "compliance": {},
        "autonomy_design": {
            "thresholds": {
                "approval_threshold": "07:00-22:00 CET",
                "documentation_score": round(result.confidence, 2),
            },
            "autonomous_actions": result.autonomous_actions,
            "approval_required": result.approval_required,
            "always_human": result.always_human,
            "agentic_shield_requirements": [],
        },
        "acceptance_criteria": {
            "kpis": result.kpis,
            "test_scenarios": [],
        },
        "learning_hooks": {
            "enabled": True,
            "observation_points": [],
            "failure_patterns_to_monitor": [],
            "kpi_deviation_signals": [],
            "feedback_targets": [],
            "improvement_loop": "",
        },
        "missing_information": result.missing_information,
        "ready_for_architect": ready,
        "method": result.method,
    }

    try:
        from connector_resolver import enrich_siop_with_connectors

        siop = enrich_siop_with_connectors(siop)
    except Exception:
        # Same fail-open-for-observability principle as everywhere else -
        # missing connector knowledge must never block the SIOP itself.
        # Builder/human can still research integration manually if this
        # didn't run.
        siop["integration_design"] = []

    return siop


def run_cli(text_path: str, siop_path: str, package_dir: str, use_llm: bool = True):
    client_text = Path(text_path).read_text(encoding="utf-8")
    siop = (
        json.loads(Path(siop_path).read_text(encoding="utf-8"))
        if siop_path and Path(siop_path).exists()
        else {}
    )

    result = consult_on_intent(client_text, siop, package_dir, use_llm=use_llm)

    print("\nFunctional Consultant complete")
    print(f"Method:     {result.method}")
    print(f"Route:      {result.route}")
    print(f"Tier:       {result.tier}")
    print(f"Confidence: {int(result.confidence * 100)}%")
    print(f"Rationale:  {result.rationale}")
    if result.process_flow_steps:
        print(f"Steps:      {len(result.process_flow_steps)} pasos de proceso")
    if result.missing_information:
        print(f"Missing:    {[m.get('field', m) if isinstance(m, dict) else m for m in result.missing_information]}")
    print(f"\nOrganisms ({len(result.organisms)}):")
    for o in result.organisms:
        tag = "NEW" if o.synthesized else "KNOWN"
        print(f"  [{tag}] {o.organism}")
    if result.erp:
        print(f"\nERP/System: {result.erp}")
    if result.method == "deterministic_fallback":
        print("\n[AVISO] No se pudo usar Claude - se usó el fallback determinista.")
        print("  Verifica ANTHROPIC_API_KEY en tu .env y que el paquete anthropic esté instalado.")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero - Intent Classifier (smart)")
    parser.add_argument("--text", required=True, help="Path to client's free-text description")
    parser.add_argument("--siop", default="", help="Path to existing SIOP JSON (optional)")
    parser.add_argument("--package-dir", required=True)
    parser.add_argument("--no-llm", action="store_true")
    args = parser.parse_args()

    run_cli(args.text, args.siop, args.package_dir, use_llm=not args.no_llm)
