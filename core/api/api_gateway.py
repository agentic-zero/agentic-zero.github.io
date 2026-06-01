"""
AGENTIC ZERO — CORE
Module: API Gateway (M7)
Role: Expose Pioneer Team agents as REST microservices

Architecture: FastAPI · API-first · Queue-ready
Every agent is an independent endpoint.
Compatible with Paperclip, n8n, any orchestrator.

Endpoints:
  POST /api/v1/pioneer/scout
  POST /api/v1/pioneer/architect
  POST /api/v1/pioneer/builder
  POST /api/v1/pioneer/packager
  POST /api/v1/pioneer/guardian
  POST /api/v1/pioneer/pipeline     ← full chain
  GET  /api/v1/library/search
  GET  /api/v1/library/process/{id}
  GET  /api/v1/health
  GET  /api/v1/status
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# ── Add project root to path so agents are importable ─────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── LOGGING ───────────────────────────────────────────────────────────────────
logger.add(
    ROOT / "logs" / "api_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | API | {message}",
)

# ── FASTAPI APP ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Agentic Zero API",
    description="Pioneer Team microservices — Autonomous Operations for Regulated Supply Chains",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REQUEST / RESPONSE MODELS ─────────────────────────────────────────────────
class ScoutRequest(BaseModel):
    framework: str  # SCOR, ISO_9001, BPMN, SCOR-D
    domains: Optional[list[str]] = None
    description: str = "API request"


class ArchitectRequest(BaseModel):
    framework: str
    domain: Optional[str] = None
    sectors: Optional[list[str]] = None
    use_llm: bool = False  # False = local only (saves tokens)


class BuilderRequest(BaseModel):
    process_id: str  # e.g. SCOR-P1.1


class PackagerRequest(BaseModel):
    process_id: str


class GuardianRequest(BaseModel):
    process_id: str


class PipelineRequest(BaseModel):
    process_id: str
    run_scout: bool = False  # Usually Scout already ran
    run_architect: bool = False  # Usually Architect already ran
    run_builder: bool = True
    run_packager: bool = True
    run_guardian: bool = True


class LibrarySearchRequest(BaseModel):
    query: str
    framework: Optional[str] = None
    domain: Optional[str] = None
    sector: Optional[str] = None
    level: Optional[str] = None
    limit: int = 10


class AgentResponse(BaseModel):
    agent: str
    status: str  # success / error / partial
    timestamp: str
    input: dict
    output: dict
    metadata: dict
    next_agent: Optional[str] = None
    errors: list[str] = []


# ── LIBRARY SERVICE ───────────────────────────────────────────────────────────
LIBRARY_PATH = Path(os.getenv("LIBRARY_PATH", str(ROOT / "library")))


def search_library(
    query: str = "",
    framework: str = None,
    domain: str = None,
    sector: str = None,
    level: str = None,
    limit: int = 10,
) -> list[dict]:
    """Search processes in library"""
    results = []
    query_lower = query.lower()

    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        processes_path = LIBRARY_PATH / folder / "processes"
        if not processes_path.exists():
            continue
        for json_file in processes_path.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    process = json.load(f)

                # Apply filters
                if (
                    framework
                    and process.get("framework", "").lower() != framework.lower()
                ):
                    continue
                if domain and process.get("domain", "").lower() != domain.lower():
                    continue
                if level and process.get("level", "").lower() != level.lower():
                    continue
                if sector:
                    sectors = " ".join(process.get("sector_applicability", [])).lower()
                    if sector.lower() not in sectors:
                        continue

                # Apply text search
                if query_lower:
                    searchable = " ".join(
                        [
                            process.get("name", ""),
                            process.get("description", ""),
                            process.get("process_id", ""),
                            " ".join(process.get("sector_applicability", [])),
                        ]
                    ).lower()
                    if query_lower not in searchable:
                        continue

                results.append(process)

                if len(results) >= limit:
                    break

            except Exception as e:
                logger.warning(f"Error reading {json_file}: {e}")

        if len(results) >= limit:
            break

    return results


def get_process_by_id(process_id: str) -> Optional[dict]:
    """Get specific process from library"""
    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        proc_file = LIBRARY_PATH / folder / "processes" / f"{process_id}.json"
        if proc_file.exists():
            with open(proc_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # Also check variants
        var_file = LIBRARY_PATH / folder / "variants" / f"{process_id}.json"
        if var_file.exists():
            with open(var_file, "r", encoding="utf-8") as f:
                return json.load(f)

    return None


def get_library_stats() -> dict:
    """Get library statistics"""
    stats = {
        "total_processes": 0,
        "total_variants": 0,
        "total_agents": 0,
        "total_packages": 0,
        "total_certificates": 0,
        "frameworks": [],
        "domains": set(),
        "sectors": set(),
    }

    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        base = LIBRARY_PATH / folder

        processes = (
            list((base / "processes").glob("*.json"))
            if (base / "processes").exists()
            else []
        )
        variants = (
            list((base / "variants").glob("*.json"))
            if (base / "variants").exists()
            else []
        )
        agents = (
            list((base / "agents").glob("*.json")) if (base / "agents").exists() else []
        )
        packages = (
            list((base / "packages").glob("*.json"))
            if (base / "packages").exists()
            else []
        )
        certs = (
            list((base / "certificates").glob("*_guardian.json"))
            if (base / "certificates").exists()
            else []
        )

        if processes:
            stats["frameworks"].append(folder.upper())
            stats["total_processes"] += len(processes)

            for p in processes[:5]:  # Sample for domains/sectors
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("domain"):
                            stats["domains"].add(data["domain"])
                        for s in data.get("sector_applicability", []):
                            stats["sectors"].add(s)
                except Exception:
                    pass

        stats["total_variants"] += len(variants)
        stats["total_agents"] += len(agents)
        stats["total_packages"] += len(packages)
        stats["total_certificates"] += len(certs)

    stats["domains"] = list(stats["domains"])
    stats["sectors"] = list(stats["sectors"])
    return stats


# ── HEALTH & STATUS ENDPOINTS ─────────────────────────────────────────────────
@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": "Agentic Zero API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "library_path": str(LIBRARY_PATH),
        "library_exists": LIBRARY_PATH.exists(),
    }


@app.get("/api/v1/status")
async def status():
    stats = get_library_stats()
    return {
        "status": "operational",
        "service": "Agentic Zero Pioneer Team",
        "timestamp": datetime.now().isoformat(),
        "pioneer_team": {
            "scout": "available",
            "architect": "available",
            "builder": "available",
            "packager": "available",
            "guardian": "available",
        },
        "library": stats,
    }


# ── LIBRARY ENDPOINTS ─────────────────────────────────────────────────────────
@app.get("/api/v1/library/search")
async def library_search(
    q: str = "",
    framework: Optional[str] = None,
    domain: Optional[str] = None,
    sector: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 10,
):
    results = search_library(q, framework, domain, sector, level, limit)
    return {
        "query": q,
        "filters": {
            "framework": framework,
            "domain": domain,
            "sector": sector,
            "level": level,
        },
        "total": len(results),
        "results": results,
    }


@app.get("/api/v1/library/process/{process_id}")
async def get_process(process_id: str):
    process = get_process_by_id(process_id)
    if not process:
        raise HTTPException(
            status_code=404, detail=f"Process {process_id} not found in library"
        )
    return process


@app.get("/api/v1/library/stats")
async def library_stats():
    return get_library_stats()


# ── PIONEER TEAM ENDPOINTS ────────────────────────────────────────────────────
@app.post("/api/v1/pioneer/scout", response_model=AgentResponse)
async def run_scout(request: ScoutRequest):
    logger.info(f"API Scout: {request.framework} {request.domains}")
    try:
        from pioneer_team.scout.scout import scout_framework

        result = scout_framework(request.framework, request.domains)
        return AgentResponse(
            agent="scout",
            status="success" if result and result.ready_for_architect else "partial",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={
                "framework": result.framework if result else request.framework,
                "total_processes": result.total_processes if result else 0,
                "domains_covered": result.domains_covered if result else [],
                "ready_for_architect": result.ready_for_architect if result else False,
            },
            metadata={
                "model": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
                "cost": "$0.00",
            },
            next_agent="architect",
        )
    except Exception as e:
        logger.error(f"Scout API error: {e}")
        return AgentResponse(
            agent="scout",
            status="error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={},
            metadata={},
            errors=[str(e)],
        )


@app.post("/api/v1/pioneer/architect", response_model=AgentResponse)
async def run_architect(request: ArchitectRequest):
    logger.info(f"API Architect: {request.framework} {request.domain}")
    try:
        from pioneer_team.architect.architect import architect_framework

        result = architect_framework(
            framework=request.framework,
            domain=request.domain,
            sectors=request.sectors,
            use_llm_validation=request.use_llm,
        )
        return AgentResponse(
            agent="architect",
            status="success" if result else "error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={
                "processes_reviewed": result.processes_reviewed if result else 0,
                "processes_valid": result.processes_valid if result else 0,
                "processes_flagged": result.processes_flagged if result else 0,
                "variants_created": result.variants_created if result else 0,
                "ready_for_builder": result.ready_for_builder if result else [],
                "needs_human_review": result.needs_human_review if result else [],
            },
            metadata={"model": os.getenv("GROQ_MODEL", "")},
            next_agent="builder",
            errors=[] if result else ["Architect returned no result"],
        )
    except Exception as e:
        logger.error(f"Architect API error: {e}")
        return AgentResponse(
            agent="architect",
            status="error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={},
            metadata={},
            errors=[str(e)],
        )


@app.post("/api/v1/pioneer/builder", response_model=AgentResponse)
async def run_builder(request: BuilderRequest):
    logger.info(f"API Builder: {request.process_id}")
    try:
        from pioneer_team.builder.builder import build_agent

        result = build_agent(request.process_id)
        return AgentResponse(
            agent="builder",
            status="success" if result and result.ready_for_packager else "error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={
                "process_id": result.process_id if result else request.process_id,
                "agent_name": result.agent_spec.agent_name if result else None,
                "agent_type": result.agent_spec.agent_type if result else None,
                "ready_for_packager": result.ready_for_packager if result else False,
                "test_cases_count": len(result.test_cases) if result else 0,
            },
            metadata={"model": os.getenv("GROQ_MODEL", ""), "pattern": "IBM Bob"},
            next_agent="packager",
            errors=[] if result else ["Builder returned no result"],
        )
    except Exception as e:
        logger.error(f"Builder API error: {e}")
        return AgentResponse(
            agent="builder",
            status="error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={},
            metadata={},
            errors=[str(e)],
        )


@app.post("/api/v1/pioneer/packager", response_model=AgentResponse)
async def run_packager(request: PackagerRequest):
    logger.info(f"API Packager: {request.process_id}")
    try:
        from pioneer_team.packager.packager import package_agent

        result = package_agent(request.process_id)
        return AgentResponse(
            agent="packager",
            status="success" if result and result.ready_for_guardian else "error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={
                "process_id": result.process_id if result else request.process_id,
                "agent_name": result.agent_name if result else None,
                "price_eur": result.pricing.total_price_eur if result else None,
                "complexity_score": result.pricing.complexity_score if result else None,
                "use_cases_count": len(result.use_cases) if result else 0,
                "ready_for_guardian": result.ready_for_guardian if result else False,
            },
            metadata={"model": os.getenv("GROQ_MODEL", "")},
            next_agent="guardian",
            errors=[] if result else ["Packager returned no result"],
        )
    except Exception as e:
        logger.error(f"Packager API error: {e}")
        return AgentResponse(
            agent="packager",
            status="error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={},
            metadata={},
            errors=[str(e)],
        )


@app.post("/api/v1/pioneer/guardian", response_model=AgentResponse)
async def run_guardian(request: GuardianRequest):
    logger.info(f"API Guardian: {request.process_id}")
    try:
        from pioneer_team.guardian.guardian import certify_agent

        result = certify_agent(request.process_id)
        return AgentResponse(
            agent="guardian",
            status="success"
            if result and result.approved_for_library
            else "conditional",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={
                "process_id": result.process_id if result else request.process_id,
                "certificate_id": result.certificate.certificate_id if result else None,
                "overall_status": result.certificate.overall_status
                if result
                else "error",
                "overall_score": result.certificate.overall_score if result else 0,
                "eu_ai_act_risk": result.certificate.eu_ai_act.risk_level
                if result
                else None,
                "approved_for_library": result.approved_for_library
                if result
                else False,
                "approved_for_delivery": result.approved_for_delivery
                if result
                else False,
                "requires_human_sign_off": result.requires_human_sign_off
                if result
                else True,
            },
            metadata={
                "frameworks": "EU AI Act · ISO/IEC 42001 · NIST AI RMF · GDPR AI"
            },
            next_agent=None,
            errors=[] if result else ["Guardian returned no result"],
        )
    except Exception as e:
        logger.error(f"Guardian API error: {e}")
        return AgentResponse(
            agent="guardian",
            status="error",
            timestamp=datetime.now().isoformat(),
            input=request.model_dump(),
            output={},
            metadata={},
            errors=[str(e)],
        )


@app.post("/api/v1/pioneer/pipeline")
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """
    Full Pioneer Team pipeline for a single process.
    Runs Builder → Packager → Guardian in sequence.
    """
    logger.info(f"API Pipeline: {request.process_id}")
    results = {"process_id": request.process_id, "steps": {}, "final_status": "pending"}

    try:
        if request.run_builder:
            from pioneer_team.builder.builder import build_agent

            builder_result = build_agent(request.process_id)
            results["steps"]["builder"] = {
                "status": "success" if builder_result else "error",
                "agent_name": builder_result.agent_spec.agent_name
                if builder_result
                else None,
            }
            if not builder_result:
                results["final_status"] = "failed_at_builder"
                return results

        if request.run_packager:
            from pioneer_team.packager.packager import package_agent

            packager_result = package_agent(request.process_id)
            results["steps"]["packager"] = {
                "status": "success" if packager_result else "error",
                "price_eur": packager_result.pricing.total_price_eur
                if packager_result
                else None,
            }
            if not packager_result:
                results["final_status"] = "failed_at_packager"
                return results

        if request.run_guardian:
            from pioneer_team.guardian.guardian import certify_agent

            guardian_result = certify_agent(request.process_id)
            results["steps"]["guardian"] = {
                "status": guardian_result.certificate.overall_status
                if guardian_result
                else "error",
                "certificate_id": guardian_result.certificate.certificate_id
                if guardian_result
                else None,
                "approved_for_library": guardian_result.approved_for_library
                if guardian_result
                else False,
            }

        results["final_status"] = "completed"
        results["timestamp"] = datetime.now().isoformat()
        return results

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        results["final_status"] = "error"
        results["error"] = str(e)
        return results


# ── ROI ENDPOINTS (M3) ────────────────────────────────────────────────────────
@app.get("/api/v1/roi/{process_id}")
async def get_roi(
    process_id: str, sector: str = "manufacturing", hourly_rate: Optional[float] = None
):
    """Calculate ROI for a process from the library"""
    try:
        sys.path.insert(0, str(ROOT))
        from core.roi_calculator import ROICalculator

        process = get_process_by_id(process_id)
        if not process:
            raise HTTPException(
                status_code=404, detail=f"Process {process_id} not found"
            )

        calc = ROICalculator()
        result = calc.calculate_from_process(
            process=process, sector=sector, custom_hourly_rate=hourly_rate
        )

        return {
            "process_id": process_id,
            "process_name": process.get("name"),
            "sector": sector,
            "roi": {
                "manual_monthly_eur": result.manual_monthly_cost_eur,
                "agent_monthly_eur": result.agent_monthly_cost_eur,
                "setup_eur": result.setup_cost_eur,
                "monthly_savings_eur": result.monthly_savings_eur,
                "annual_savings_eur": result.annual_savings_eur,
                "payback_months": result.payback_months,
                "roi_12_months_pct": result.roi_12_months_pct,
                "roi_24_months_pct": result.roi_24_months_pct,
                "roi_36_months_pct": result.roi_36_months_pct,
            },
            "efficiency": {
                "time_saved_hours_month": result.time_saved_hours_month,
                "error_reduction_pct": result.error_reduction_pct,
                "compliance_time_saved_hours_month": result.compliance_time_saved_hours_month,
            },
            "recommendation": result.recommendation,
            "confidence": result.confidence_level,
            "qualitative_benefits": result.qualitative_benefits,
            "assumptions": result.assumptions,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ROI calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/roi/compare/{process_id}")
async def compare_roi_sectors(process_id: str):
    """Compare ROI across all sectors for a process"""
    try:
        sys.path.insert(0, str(ROOT))
        from core.roi_calculator import ROICalculator, INDUSTRY_BENCHMARKS

        process = get_process_by_id(process_id)
        if not process:
            raise HTTPException(
                status_code=404, detail=f"Process {process_id} not found"
            )

        calc = ROICalculator()
        comparison = {}

        for sector in INDUSTRY_BENCHMARKS.keys():
            result = calc.calculate_from_process(process=process, sector=sector)
            comparison[sector] = {
                "monthly_savings_eur": result.monthly_savings_eur,
                "annual_savings_eur": result.annual_savings_eur,
                "roi_12_months_pct": result.roi_12_months_pct,
                "payback_months": result.payback_months,
                "recommendation": result.recommendation,
            }

        # Sort by ROI
        sorted_sectors = sorted(
            comparison.items(), key=lambda x: x[1]["roi_12_months_pct"], reverse=True
        )

        return {
            "process_id": process_id,
            "process_name": process.get("name"),
            "best_sector": sorted_sectors[0][0],
            "best_roi_pct": sorted_sectors[0][1]["roi_12_months_pct"],
            "comparison": dict(sorted_sectors),
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    logger.info(f"Starting Agentic Zero API on {host}:{port}")
    logger.info(f"Docs: http://localhost:{port}/docs")
    uvicorn.run("api_gateway:app", host=host, port=port, reload=True)
