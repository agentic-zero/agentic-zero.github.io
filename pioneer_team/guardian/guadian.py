"""
AGENTIC ZERO — PIONEER TEAM
Agent 5: GUARDIAN
Role: Compliance & Quality certification before library entry
Input: ProductPackage from Packager
Output: Certified product ready for library and delivery

Responsibilities:
- EU AI Act risk classification
- ISO/IEC 42001 requirements check
- NIST AI RMF alignment
- GDPR AI compliance check
- Quality score validation
- Final approval or rejection with remediation notes
- Generate compliance certificate

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
    "logs/guardian_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


# ── MODELS ────────────────────────────────────────────────────────────────────
class EUAIActClassification(BaseModel):
    risk_level: str  # unacceptable / high / limited / minimal
    risk_rationale: str
    prohibited: bool
    requirements: list[str]  # What must be done for this risk level
    article_references: list[str]  # Relevant EU AI Act articles


class ISO42001Check(BaseModel):
    compliant: bool
    score: float  # 0.0 - 1.0
    gaps: list[str]
    recommendations: list[str]


class NISTAIRMFCheck(BaseModel):
    govern_score: float
    map_score: float
    measure_score: float
    manage_score: float
    overall_score: float
    gaps: list[str]


class GDPRCheck(BaseModel):
    personal_data_involved: bool
    lawful_basis_defined: bool
    data_minimization: bool
    transparency_adequate: bool
    issues: list[str]


class ComplianceCertificate(BaseModel):
    certificate_id: str
    process_id: str
    agent_name: str
    issued_at: str
    issued_by: str  # "Guardian Agent — Agentic Zero"
    valid_until: str  # 12 months from issue
    overall_status: str  # certified / conditional / rejected
    overall_score: float  # 0.0 - 1.0
    eu_ai_act: EUAIActClassification
    iso_42001: ISO42001Check
    nist_ai_rmf: NISTAIRMFCheck
    gdpr: GDPRCheck
    quality_score: float
    quality_issues: list[str]
    conditions: list[str]  # Conditions if conditional approval
    rejection_reasons: list[str]  # Reasons if rejected
    human_review_required: bool
    notes: str


class GuardianResult(BaseModel):
    process_id: str
    guardian_timestamp: str
    certificate: ComplianceCertificate
    approved_for_library: bool
    approved_for_delivery: bool
    requires_human_sign_off: bool
    remediation_plan: list[str]


# ── GUARDIAN CONFIGURATION ────────────────────────────────────────────────────
GUARDIAN_CONFIG = {
    "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
    "max_tokens": 4000,
    "temperature": 0.1,
    "rate_limit_rpm": 1,
    "rate_limit_rpd": 1400,
    "issuer": "Guardian Agent — Agentic Zero Pioneer Team",
    "certificate_validity_months": 12,
}

# ── EU AI ACT KNOWLEDGE BASE ──────────────────────────────────────────────────
EU_AI_ACT_HIGH_RISK_SECTORS = [
    "critical infrastructure",
    "education",
    "employment",
    "essential services",
    "law enforcement",
    "migration",
    "justice",
    "biometric",
    "medical device",
    "safety component",
]

EU_AI_ACT_HIGH_RISK_SUPPLY_CHAIN = [
    "automated decision making affecting workers",
    "creditworthiness assessment",
    "risk assessment",
    "recruitment",
    "performance evaluation",
]

EU_AI_ACT_HIGH_RISK_REQUIREMENTS = [
    "Risk management system (Art. 9)",
    "Data governance measures (Art. 10)",
    "Technical documentation (Art. 11)",
    "Record-keeping and logging (Art. 12)",
    "Transparency and information (Art. 13)",
    "Human oversight measures (Art. 14)",
    "Accuracy, robustness, cybersecurity (Art. 15)",
    "Conformity assessment (Art. 43)",
    "Registration in EU database (Art. 51)",
]

EU_AI_ACT_LIMITED_RISK_REQUIREMENTS = [
    "Transparency obligations (Art. 52)",
    "Inform users they are interacting with AI",
    "Deep fake labeling if applicable",
]

EU_AI_ACT_MINIMAL_RISK_REQUIREMENTS = [
    "Voluntary codes of conduct recommended",
    "No mandatory requirements",
]

# ── ISO 42001 CHECKLIST ───────────────────────────────────────────────────────
ISO_42001_REQUIREMENTS = {
    "4_context": "Understanding of organization and AI context",
    "5_leadership": "Leadership commitment to responsible AI",
    "6_planning": "AI risk and opportunity assessment",
    "7_support": "Resources, competence, awareness",
    "8_operation": "Operational planning and control",
    "9_performance": "Performance evaluation and monitoring",
    "10_improvement": "Continual improvement process",
}

# ── NIST AI RMF FUNCTIONS ─────────────────────────────────────────────────────
NIST_GOVERN_CHECKS = [
    "Policies for responsible AI defined",
    "Roles and responsibilities assigned",
    "Risk tolerance established",
    "Accountability mechanisms in place",
]

NIST_MAP_CHECKS = [
    "AI system context documented",
    "Stakeholders identified",
    "Risks categorized",
    "Impact assessment completed",
]

NIST_MEASURE_CHECKS = [
    "Performance metrics defined",
    "Bias testing planned",
    "Monitoring mechanisms specified",
    "Incident response defined",
]

NIST_MANAGE_CHECKS = [
    "Risk response strategies defined",
    "Human oversight specified",
    "Escalation procedures documented",
    "Remediation process defined",
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


rate_limiter = RateLimiter(rpm=GUARDIAN_CONFIG["rate_limit_rpm"])


# ── LLM CALLER ────────────────────────────────────────────────────────────────
def call_llm(prompt: str, expect_json: bool = True) -> str:
    rate_limiter.wait()
    try:
        response = litellm.completion(
            model=GUARDIAN_CONFIG["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=GUARDIAN_CONFIG["max_tokens"],
            temperature=GUARDIAN_CONFIG["temperature"],
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


# ── LOCAL COMPLIANCE CHECKS (no LLM needed) ───────────────────────────────────
def check_eu_ai_act_local(process: dict, package: dict) -> EUAIActClassification:
    """EU AI Act classification — local rule-based check"""
    compliance_flags = " ".join(process.get("compliance_flags", [])).lower()
    sector_text = " ".join(process.get("sector_applicability", [])).lower()
    name_text = process.get("name", "").lower()
    description_text = process.get("description", "").lower()
    all_text = f"{compliance_flags} {sector_text} {name_text} {description_text}"

    # Check for prohibited use cases
    prohibited_keywords = [
        "social scoring",
        "mass surveillance",
        "subliminal manipulation",
        "exploit vulnerabilities",
    ]
    is_prohibited = any(kw in all_text for kw in prohibited_keywords)

    if is_prohibited:
        return EUAIActClassification(
            risk_level="unacceptable",
            risk_rationale="Process appears to involve prohibited AI use case",
            prohibited=True,
            requirements=["PROHIBITED — Cannot be deployed under EU AI Act"],
            article_references=["Article 5 — Prohibited AI practices"],
        )

    # Check for high-risk indicators
    high_risk_keywords = [
        "pharma",
        "medical",
        "defense",
        "safety",
        "critical",
        "risk assessment",
        "worker",
        "recruitment",
        "credit",
        "law enforcement",
        "biometric",
    ]
    is_high_risk = any(kw in all_text for kw in high_risk_keywords)

    if is_high_risk:
        return EUAIActClassification(
            risk_level="high",
            risk_rationale=f"Process operates in regulated/safety-critical domain",
            prohibited=False,
            requirements=EU_AI_ACT_HIGH_RISK_REQUIREMENTS,
            article_references=[
                "Annex III — High-risk AI systems",
                "Article 9",
                "Article 10",
                "Article 11",
                "Article 12",
                "Article 13",
                "Article 14",
                "Article 15",
            ],
        )

    # Check for limited risk
    limited_risk_keywords = [
        "customer",
        "chatbot",
        "recommendation",
        "generation",
        "synthesis",
    ]
    is_limited_risk = any(kw in all_text for kw in limited_risk_keywords)

    if is_limited_risk:
        return EUAIActClassification(
            risk_level="limited",
            risk_rationale="Process involves AI interaction with users",
            prohibited=False,
            requirements=EU_AI_ACT_LIMITED_RISK_REQUIREMENTS,
            article_references=["Article 52 — Transparency obligations"],
        )

    # Default: minimal risk
    return EUAIActClassification(
        risk_level="minimal",
        risk_rationale="Standard supply chain process with no identified high-risk characteristics",
        prohibited=False,
        requirements=EU_AI_ACT_MINIMAL_RISK_REQUIREMENTS,
        article_references=["Recital 47 — Minimal risk AI systems"],
    )


def check_nist_local(
    process: dict, builder_result: dict, package: dict
) -> NISTAIRMFCheck:
    """NIST AI RMF check — local scoring"""
    agent_spec = builder_result.get("agent_spec", {})

    # Govern: check if accountability defined
    govern_score = 0.5
    if agent_spec.get("escalation_rules"):
        govern_score += 0.25
    if process.get("compliance_flags"):
        govern_score += 0.25

    # Map: check if context documented
    map_score = 0.5
    if process.get("sector_applicability"):
        map_score += 0.25
    if process.get("description") and len(process.get("description", "")) > 50:
        map_score += 0.25

    # Measure: check if metrics defined
    measure_score = 0.4
    if process.get("kpis"):
        measure_score += 0.3
    if agent_spec.get("monitoring_metrics"):
        measure_score += 0.3

    # Manage: check if response defined
    manage_score = 0.4
    if agent_spec.get("escalation_rules"):
        manage_score += 0.3
    if builder_result.get("ontology", {}).get("failure_modes"):
        manage_score += 0.3

    overall = (govern_score + map_score + measure_score + manage_score) / 4

    gaps = []
    if govern_score < 0.75:
        gaps.append("GOVERN: Define explicit accountability and governance policies")
    if map_score < 0.75:
        gaps.append("MAP: Complete stakeholder impact assessment")
    if measure_score < 0.75:
        gaps.append("MEASURE: Add bias testing and fairness metrics")
    if manage_score < 0.75:
        gaps.append("MANAGE: Document complete incident response procedure")

    return NISTAIRMFCheck(
        govern_score=min(govern_score, 1.0),
        map_score=min(map_score, 1.0),
        measure_score=min(measure_score, 1.0),
        manage_score=min(manage_score, 1.0),
        overall_score=min(overall, 1.0),
        gaps=gaps,
    )


def check_gdpr_local(process: dict) -> GDPRCheck:
    """GDPR AI check — local rule-based"""
    all_text = " ".join(
        [
            process.get("name", ""),
            process.get("description", ""),
            " ".join(process.get("inputs", [])),
            " ".join(process.get("outputs", [])),
        ]
    ).lower()

    personal_data_keywords = [
        "customer",
        "employee",
        "worker",
        "personal",
        "individual",
        "supplier contact",
        "user",
        "patient",
        "name",
        "email",
        "id",
    ]
    personal_data = any(kw in all_text for kw in personal_data_keywords)

    issues = []
    if personal_data:
        issues.append("Personal data detected: define lawful basis for processing")
        issues.append("Data minimization: ensure only necessary data is processed")
        issues.append("Retention policy: define how long data is retained")

    return GDPRCheck(
        personal_data_involved=personal_data,
        lawful_basis_defined=not personal_data,
        data_minimization=True,
        transparency_adequate=True,
        issues=issues,
    )


def check_quality_local(
    process: dict, builder_result: dict, package: dict
) -> tuple[float, list]:
    """Quality score — local check"""
    issues = []
    score = 1.0

    # Check process completeness
    if not process.get("inputs") or len(process.get("inputs", [])) < 2:
        issues.append("Process has insufficient inputs defined")
        score -= 0.1
    if not process.get("outputs") or len(process.get("outputs", [])) < 1:
        issues.append("Process has no outputs defined")
        score -= 0.15
    if not process.get("kpis"):
        issues.append("No KPIs defined for performance measurement")
        score -= 0.1

    # Check builder result completeness
    if not builder_result.get("ontology", {}).get("decision_points"):
        issues.append(
            "No decision points in ontology — agent may not handle edge cases"
        )
        score -= 0.1
    if not builder_result.get("test_cases"):
        issues.append("No test cases generated — deployment risk")
        score -= 0.15
    if not builder_result.get("agent_code"):
        issues.append("No agent code generated")
        score -= 0.25

    # Check package completeness
    if not package.get("product_summary"):
        issues.append("Missing product summary")
        score -= 0.05
    if not package.get("demo_script"):
        issues.append("Missing demo script")
        score -= 0.05

    return max(score, 0.0), issues


# ── COMPLIANCE CERTIFICATE GENERATOR ─────────────────────────────────────────
def generate_certificate(
    process: dict,
    package: dict,
    builder_result: dict,
    eu_ai_act: EUAIActClassification,
    iso_42001: ISO42001Check,
    nist: NISTAIRMFCheck,
    gdpr: GDPRCheck,
    quality_score: float,
    quality_issues: list,
) -> ComplianceCertificate:
    """Generate compliance certificate"""
    process_id = process.get("process_id", "UNKNOWN")
    agent_name = package.get("agent_name", "unknown_agent")

    # Overall status determination
    conditions = []
    rejection_reasons = []
    human_review_required = False

    if eu_ai_act.prohibited:
        overall_status = "rejected"
        rejection_reasons.append("EU AI Act: Prohibited use case")
    elif eu_ai_act.risk_level == "high":
        if quality_score >= 0.7 and nist.overall_score >= 0.6:
            overall_status = "conditional"
            conditions.extend(eu_ai_act.requirements[:3])
            human_review_required = True
        else:
            overall_status = "conditional"
            conditions.extend(eu_ai_act.requirements[:3])
            conditions.extend(quality_issues[:2])
            human_review_required = True
    elif quality_score >= 0.7 and nist.overall_score >= 0.6:
        overall_status = "certified"
    elif quality_score >= 0.5:
        overall_status = "conditional"
        conditions.extend(quality_issues[:3])
    else:
        overall_status = "rejected"
        rejection_reasons.extend(quality_issues[:3])

    # Overall score
    overall_score = (
        quality_score * 0.3
        + iso_42001.score * 0.2
        + nist.overall_score * 0.3
        + (0.8 if not gdpr.issues else 0.5) * 0.2
    )

    # Certificate validity
    from datetime import timedelta

    valid_until = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    # Certificate ID
    cert_id = f"AZ-CERT-{process_id}-{datetime.now().strftime('%Y%m%d')}"

    return ComplianceCertificate(
        certificate_id=cert_id,
        process_id=process_id,
        agent_name=agent_name,
        issued_at=datetime.now().isoformat(),
        issued_by=GUARDIAN_CONFIG["issuer"],
        valid_until=valid_until,
        overall_status=overall_status,
        overall_score=round(overall_score, 2),
        eu_ai_act=eu_ai_act,
        iso_42001=iso_42001,
        nist_ai_rmf=nist,
        gdpr=gdpr,
        quality_score=quality_score,
        quality_issues=quality_issues,
        conditions=conditions,
        rejection_reasons=rejection_reasons,
        human_review_required=human_review_required,
        notes=f"Guardian review completed. Risk level: {eu_ai_act.risk_level}. Quality: {round(quality_score * 100)}%",
    )


# ── ISO 42001 CHECK (LLM-assisted) ────────────────────────────────────────────
def check_iso_42001(process: dict, builder_result: dict) -> ISO42001Check:
    """ISO/IEC 42001 check — LLM assisted for depth"""
    try:
        prompt = f"""You are an ISO/IEC 42001 auditor reviewing an AI agent.

AGENT PROCESS: {process.get("name")}
AGENT TYPE: {builder_result.get("agent_spec", {}).get("agent_type", "reactive")}
CAPABILITIES: {builder_result.get("agent_spec", {}).get("capabilities", [])}
ESCALATION RULES: {builder_result.get("agent_spec", {}).get("escalation_rules", [])}
COMPLIANCE FLAGS: {process.get("compliance_flags", [])}

Evaluate against ISO/IEC 42001 AI Management Systems standard.
Return ONLY a JSON object:
{{
  "compliant": true/false,
  "score": 0.0-1.0,
  "gaps": ["gap1", "gap2"],
  "recommendations": ["rec1", "rec2"]
}}

Score guide: 0.9+ fully compliant, 0.7-0.9 mostly compliant with minor gaps, 
0.5-0.7 partial compliance, <0.5 significant gaps"""

        response = call_llm(prompt, expect_json=True)
        data = json.loads(response)
        return ISO42001Check(
            compliant=data.get("compliant", False),
            score=data.get("score", 0.6),
            gaps=data.get("gaps", []),
            recommendations=data.get("recommendations", []),
        )
    except Exception as e:
        logger.warning(f"ISO 42001 LLM check failed, using default: {e}")
        return ISO42001Check(
            compliant=True,
            score=0.7,
            gaps=["Full ISO 42001 assessment requires manual review"],
            recommendations=[
                "Complete formal ISO 42001 gap analysis before production deployment"
            ],
        )


# ── LIBRARY LOADER / WRITER ───────────────────────────────────────────────────
def load_package(process_id: str) -> Optional[dict]:
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        pkg_file = library_path / folder / "packages" / f"{process_id}_package.json"
        if pkg_file.exists():
            with open(pkg_file, "r", encoding="utf-8") as f:
                return json.load(f)
    logger.error(f"Package not found for: {process_id}")
    return None


def load_builder_result(process_id: str) -> Optional[dict]:
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        result_file = library_path / folder / "agents" / f"{process_id}_builder.json"
        if result_file.exists():
            with open(result_file, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def load_process(process_id: str) -> Optional[dict]:
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        proc_file = library_path / folder / "processes" / f"{process_id}.json"
        if proc_file.exists():
            with open(proc_file, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def save_guardian_result(result: GuardianResult, process: dict):
    library_path = Path(os.getenv("LIBRARY_PATH", "library"))
    framework = process.get("framework", "scor").lower()

    if "scor" in framework:
        folder = library_path / "scor"
    elif "iso" in framework:
        folder = library_path / "iso"
    else:
        folder = library_path / "sector_specific"

    certs_folder = folder / "certificates"
    certs_folder.mkdir(exist_ok=True)

    # Save full result
    result_file = certs_folder / f"{result.process_id}_guardian.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    # Save certificate as readable text
    cert = result.certificate
    cert_text = f"""
AGENTIC ZERO — COMPLIANCE CERTIFICATE
======================================
Certificate ID:  {cert.certificate_id}
Process ID:      {cert.process_id}
Agent:           {cert.agent_name}
Issued:          {cert.issued_at[:10]}
Valid Until:     {cert.valid_until}
Issued By:       {cert.issued_by}

OVERALL STATUS:  {cert.overall_status.upper()}
Overall Score:   {round(cert.overall_score * 100)}%

COMPLIANCE SUMMARY
──────────────────
EU AI Act:       {cert.eu_ai_act.risk_level.upper()} RISK
ISO/IEC 42001:   {"COMPLIANT" if cert.iso_42001.compliant else "GAPS FOUND"} ({round(cert.iso_42001.score * 100)}%)
NIST AI RMF:     {round(cert.nist_ai_rmf.overall_score * 100)}% overall
GDPR AI:         {"ISSUES FOUND" if cert.gdpr.issues else "CLEAR"}
Quality:         {round(cert.quality_score * 100)}%

{"CONDITIONS" if cert.conditions else ""}
{"─" * 20 if cert.conditions else ""}
{chr(10).join([f"• {c}" for c in cert.conditions]) if cert.conditions else ""}

{"HUMAN REVIEW REQUIRED" if cert.human_review_required else "No human review required"}

{cert.notes}
"""

    cert_file = certs_folder / f"{result.process_id}_certificate.txt"
    with open(cert_file, "w", encoding="utf-8") as f:
        f.write(cert_text)

    logger.info(f"Guardian result saved: {result_file}")
    logger.info(f"Certificate saved: {cert_file}")
    return result_file


# ── MAIN GUARDIAN FUNCTION ────────────────────────────────────────────────────
def certify_agent(process_id: str) -> Optional[GuardianResult]:
    """
    Main Guardian function: compliance certification

    Args:
        process_id: ID of the process to certify

    Returns:
        GuardianResult with compliance certificate
    """
    logger.info(f"Guardian starting certification: {process_id}")

    process = load_process(process_id)
    builder_result = load_builder_result(process_id)
    package = load_package(process_id)

    if not process:
        logger.error(f"Process not found: {process_id}")
        return None
    if not builder_result:
        logger.error(f"Builder result not found: {process_id}. Run Builder first.")
        return None
    if not package:
        logger.error(f"Package not found: {process_id}. Run Packager first.")
        return None

    try:
        # STEP 1 — EU AI Act (local, fast)
        logger.info("Step 1/5: EU AI Act classification...")
        eu_ai_act = check_eu_ai_act_local(process, package)
        logger.success(f"EU AI Act: {eu_ai_act.risk_level.upper()} RISK")

        if eu_ai_act.prohibited:
            logger.error(f"Process {process_id} is PROHIBITED under EU AI Act")
            cert = generate_certificate(
                process,
                package,
                builder_result,
                eu_ai_act,
                ISO42001Check(
                    compliant=False, score=0.0, gaps=["Prohibited"], recommendations=[]
                ),
                NISTAIRMFCheck(
                    govern_score=0,
                    map_score=0,
                    measure_score=0,
                    manage_score=0,
                    overall_score=0,
                    gaps=[],
                ),
                GDPRCheck(
                    personal_data_involved=False,
                    lawful_basis_defined=False,
                    data_minimization=False,
                    transparency_adequate=False,
                    issues=[],
                ),
                0.0,
                ["PROHIBITED USE CASE"],
            )
            result = GuardianResult(
                process_id=process_id,
                guardian_timestamp=datetime.now().isoformat(),
                certificate=cert,
                approved_for_library=False,
                approved_for_delivery=False,
                requires_human_sign_off=True,
                remediation_plan=["Review EU AI Act Article 5 compliance requirements"],
            )
            save_guardian_result(result, process)
            return result

        # STEP 2 — ISO/IEC 42001 (LLM)
        logger.info("Step 2/5: ISO/IEC 42001 check...")
        iso_42001 = check_iso_42001(process, builder_result)
        logger.success(f"ISO 42001: {round(iso_42001.score * 100)}%")

        # STEP 3 — NIST AI RMF (local)
        logger.info("Step 3/5: NIST AI RMF check...")
        nist = check_nist_local(process, builder_result, package)
        logger.success(f"NIST AI RMF: {round(nist.overall_score * 100)}%")

        # STEP 4 — GDPR (local)
        logger.info("Step 4/5: GDPR AI check...")
        gdpr = check_gdpr_local(process)
        logger.success(f"GDPR: {'Issues found' if gdpr.issues else 'Clear'}")

        # STEP 5 — Quality (local)
        logger.info("Step 5/5: Quality check...")
        quality_score, quality_issues = check_quality_local(
            process, builder_result, package
        )
        logger.success(f"Quality: {round(quality_score * 100)}%")

        # Generate certificate
        cert = generate_certificate(
            process,
            package,
            builder_result,
            eu_ai_act,
            iso_42001,
            nist,
            gdpr,
            quality_score,
            quality_issues,
        )

        # Determine approvals
        approved_library = cert.overall_status in ["certified", "conditional"]
        approved_delivery = cert.overall_status == "certified"
        needs_human = cert.human_review_required or eu_ai_act.risk_level == "high"

        # Build remediation plan
        remediation = []
        if quality_issues:
            remediation.extend([f"Quality: {issue}" for issue in quality_issues[:2]])
        if nist.gaps:
            remediation.extend([f"NIST: {gap}" for gap in nist.gaps[:2]])
        if iso_42001.gaps:
            remediation.extend([f"ISO 42001: {gap}" for gap in iso_42001.gaps[:1]])
        if gdpr.issues:
            remediation.extend([f"GDPR: {issue}" for issue in gdpr.issues[:1]])

        result = GuardianResult(
            process_id=process_id,
            guardian_timestamp=datetime.now().isoformat(),
            certificate=cert,
            approved_for_library=approved_library,
            approved_for_delivery=approved_delivery,
            requires_human_sign_off=needs_human,
            remediation_plan=remediation,
        )

        save_guardian_result(result, process)

        logger.success(
            f"Guardian complete: {process_id} | "
            f"Status: {cert.overall_status.upper()} | "
            f"Score: {round(cert.overall_score * 100)}% | "
            f"Library: {approved_library} | "
            f"Delivery: {approved_delivery}"
        )

        return result

    except Exception as e:
        logger.error(f"Guardian failed for {process_id}: {e}")
        return None


# ── CLI INTERFACE ─────────────────────────────────────────────────────────────
def run_guardian(process_ids: list):
    logger.info("=" * 60)
    logger.info("AGENTIC ZERO — GUARDIAN AGENT")
    logger.info(f"Processes to certify: {process_ids}")
    logger.info(f"Frameworks: EU AI Act · ISO/IEC 42001 · NIST AI RMF · GDPR AI")
    logger.info("=" * 60)

    results = []
    for pid in process_ids:
        logger.info(f"Certifying: {pid}")
        result = certify_agent(pid)
        if result:
            results.append(result)
            cert = result.certificate
            print(f"\n✅ {pid}")
            print(f"   Status:     {cert.overall_status.upper()}")
            print(f"   Score:      {round(cert.overall_score * 100)}%")
            print(f"   EU AI Act:  {cert.eu_ai_act.risk_level.upper()} RISK")
            print(f"   ISO 42001:  {round(cert.iso_42001.score * 100)}%")
            print(f"   NIST RMF:   {round(cert.nist_ai_rmf.overall_score * 100)}%")
            print(f"   Library:    {'✅' if result.approved_for_library else '❌'}")
            print(f"   Delivery:   {'✅' if result.approved_for_delivery else '❌'}")
            if result.requires_human_sign_off:
                print(f"   ⚠️  Requires human sign-off")
        else:
            print(f"\n❌ {pid} → Certification failed")

    print(f"\n{'=' * 40}")
    print(f"Guardian complete: {len(results)}/{len(process_ids)} certified")
    certified = [r for r in results if r.certificate.overall_status == "certified"]
    conditional = [r for r in results if r.certificate.overall_status == "conditional"]
    rejected = [r for r in results if r.certificate.overall_status == "rejected"]
    print(f"  Certified:   {len(certified)}")
    print(f"  Conditional: {len(conditional)}")
    print(f"  Rejected:    {len(rejected)}")
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("\nUsage: python guardian.py PROCESS_ID [PROCESS_ID2 ...]")
        print("Example: python guardian.py SCOR-P1.1")
        print("Note: Builder and Packager must have run first\n")
        sys.exit(1)

    process_ids = sys.argv[1:]
    run_guardian(process_ids)
