"""
AGENTIC ZERO -- PIONEER TEAM
customer_pipeline.py

Role:
  End-to-end pipeline from raw AUDIT ZERO data to Architect-ready blueprint.
  Orchestrates four agents in sequence with gates and automatic retry.

Pipeline:
  1. Functional Translator  (AUDIT ZERO JSON -> FunctionalAnalysisDraft)
  2. SIOP Generator         (FunctionalAnalysisDraft -> SIOPInternal)
  3. SIOP Validator         (SIOPInternal -> SIOPValidationResult + GATE)
  4. Architect SIOP Bridge  (SIOPInternal -> ArchitectBlueprint)

Gates:
  - After Validator: if FAIL -> stop and report blocking issues
  - After Validator: if PASS_WITH_WARNINGS -> proceed with warnings logged
  - After Bridge:    if not ready_for_builder -> notify human + stop

Output:
  library/architect_blueprints/{SIOP_ID}_blueprint.json
  -> consumed by Builder to generate the agent code automatically

Mantra:
  "Does this make it feel like a living enterprise?"

Usage:
  python customer_pipeline.py --audit path/to/audit_zero.json
  python customer_pipeline.py --audit path/to/audit.json --fast-track path/to/ft.json
  python customer_pipeline.py --audit path/to/audit.json --use-llm
  python customer_pipeline.py --fa path/to/functional_analysis.json   # skip translator
  python customer_pipeline.py --siop path/to/siop.json                # skip to validator
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.add(
    "logs/customer_pipeline_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | PIPELINE | {message}",
)

# -- PATHS ---------------------------------------------------------------------
FA_PATH         = Path(os.getenv("FUNCTIONAL_ANALYSIS_PATH", "library/functional_analysis"))
SIOP_PATH       = Path(os.getenv("SIOP_INTERNAL_PATH",       "library/siop_internal"))
VALIDATION_PATH = Path(os.getenv("SIOP_VALIDATION_PATH",     "library/siop_validations"))
BLUEPRINT_PATH  = Path(os.getenv("BLUEPRINT_PATH",           "library/architect_blueprints"))

for p in [FA_PATH, SIOP_PATH, VALIDATION_PATH, BLUEPRINT_PATH]:
    p.mkdir(parents=True, exist_ok=True)


# -- PIPELINE RESULT -----------------------------------------------------------
@dataclass
class StageResult:
    stage: str
    status: str           # "ok" | "skipped" | "warn" | "fail"
    output_path: str = ""
    output_id: str = ""
    score: float = 0.0
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration_sec: float = 0.0


@dataclass
class PipelineResult:
    pipeline_id: str
    started_at: str
    completed_at: str = ""
    company: str = ""
    process: str = ""
    status: str = "running"   # "running" | "complete" | "blocked" | "failed"
    stages: list[StageResult] = field(default_factory=list)
    blueprint_path: str = ""
    blueprint_id: str = ""
    ready_for_builder: bool = False
    blocking_issues: list[str] = field(default_factory=list)
    next_step: str = ""

    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"  AGENTIC ZERO -- Customer Pipeline")
        print(f"  Company : {self.company}")
        print(f"  Process : {self.process}")
        print(f"  Status  : {self.status.upper()}")
        print(f"{'='*60}")
        for s in self.stages:
            icon = {"ok": "OK", "warn": "WARN", "fail": "FAIL", "skipped": "SKIP"}.get(s.status, "?")
            score_str = f" | score={s.score:.2f}" if s.score else ""
            print(f"  [{icon}] {s.stage:<30}{score_str}")
            for issue in s.issues:
                print(f"       BLOCK: {issue}")
            for w in s.warnings[:3]:
                print(f"       WARN:  {w}")
        print(f"{'='*60}")
        if self.ready_for_builder:
            print(f"  Ready for Builder: YES")
            print(f"  Blueprint: {self.blueprint_path}")
            print(f"\n  Next:")
            print(f"    python builder.py --blueprint {self.blueprint_path}")
        else:
            print(f"  Ready for Builder: NO")
            if self.blocking_issues:
                print(f"\n  Blocking issues to resolve:")
                for issue in self.blocking_issues:
                    print(f"    -> {issue}")
            if self.next_step:
                print(f"\n  Next: {self.next_step}")
        print(f"{'='*60}\n")


def _save_pipeline_result(result: PipelineResult) -> Path:
    out = BLUEPRINT_PATH / f"pipeline_{result.pipeline_id}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    return out


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _duration(start: datetime) -> float:
    return round((datetime.now() - start).total_seconds(), 2)


# -- STAGE 1: FUNCTIONAL TRANSLATOR -------------------------------------------
def run_translator(
    audit_path: str,
    fast_track_path: Optional[str] = None,
    documentation_path: Optional[str] = None,
    use_llm: bool = False,
) -> StageResult:
    """
    Run Functional Translator on AUDIT ZERO JSON.
    Output: library/functional_analysis/{FA-ID}.json
    """
    stage_start = datetime.now()
    stage = StageResult(stage="1_functional_translator", status="running")
    logger.info(f"Stage 1: Functional Translator | audit={audit_path}")

    try:
        # Import here to avoid circular dependency issues
        from functional_translator import (
            load_json_file, load_text_file,
            translate_to_functional_analysis,
            FUNCTIONAL_TRANSLATOR_CONFIG,
        )

        audit_zero = load_json_file(audit_path)
        fast_track = load_json_file(fast_track_path) if fast_track_path else None
        doc_text   = load_text_file(documentation_path) if documentation_path else ""

        analysis = translate_to_functional_analysis(
            audit_zero, fast_track, doc_text,
            use_llm=use_llm,
            export_for_architect=True,
        )

        fa_path = Path(FUNCTIONAL_TRANSLATOR_CONFIG["output_path"]) / f"{analysis.functional_analysis_id}.json"

        stage.status      = "ok"
        stage.output_id   = analysis.functional_analysis_id
        stage.output_path = str(fa_path)
        stage.score       = float(analysis.confidence or 0)

        if not analysis.ready_for_architect:
            stage.status = "warn"
            stage.warnings.append(f"confidence={analysis.confidence} -- may need enrichment")

        missing_critical = [
            m for m in (analysis.missing_information or [])
            if isinstance(m, dict) and m.get("severity") == "critical"
        ]
        if missing_critical:
            stage.status = "warn"
            for m in missing_critical:
                stage.warnings.append(f"critical missing: {m.get('field','?')}: {m.get('reason','')}")

        logger.success(f"Stage 1 OK | fa_id={analysis.functional_analysis_id} | confidence={analysis.confidence}")

    except ImportError as e:
        stage.status = "fail"
        stage.issues.append(f"functional_translator.py not found or import error: {e}")
        logger.error(f"Stage 1 FAIL -- import: {e}")

    except Exception as e:
        stage.status = "fail"
        stage.issues.append(str(e))
        logger.error(f"Stage 1 FAIL: {e}", exc_info=True)

    stage.duration_sec = _duration(stage_start)
    return stage


# -- STAGE 2: SIOP GENERATOR ---------------------------------------------------
def run_siop_generator(fa_path: str) -> StageResult:
    """
    Run SIOP Generator on a FunctionalAnalysis JSON.
    Output: library/siop_internal/{SIOP-ID}.json
    """
    stage_start = datetime.now()
    stage = StageResult(stage="2_siop_generator", status="running")
    logger.info(f"Stage 2: SIOP Generator | fa={fa_path}")

    try:
        from siop_generator import (
            load_json, generate_siop, save_siop, SIOP_CONFIG
        )

        fa = load_json(fa_path)
        siop = generate_siop(fa)
        siop_file = save_siop(siop)

        stage.status      = "ok"
        stage.output_id   = siop.siop_id
        stage.output_path = str(siop_file)
        stage.score       = float(siop.executive_summary.confidence or 0)

        if not siop.ready_for_architect:
            stage.status = "warn"
            stage.warnings.append("SIOP ready_for_architect=False -- missing required fields")

        missing_critical = [
            m for m in (siop.missing_information or [])
            if isinstance(m, dict) and m.get("severity") == "critical"
        ]
        for m in missing_critical:
            stage.warnings.append(f"critical missing: {m.get('field','?')}")

        logger.success(f"Stage 2 OK | siop_id={siop.siop_id} | ready_for_architect={siop.ready_for_architect}")

    except ImportError as e:
        stage.status = "fail"
        stage.issues.append(f"siop_generator.py not found: {e}")
        logger.error(f"Stage 2 FAIL -- import: {e}")

    except Exception as e:
        stage.status = "fail"
        stage.issues.append(str(e))
        logger.error(f"Stage 2 FAIL: {e}", exc_info=True)

    stage.duration_sec = _duration(stage_start)
    return stage


# -- STAGE 3: SIOP VALIDATOR (GATE) --------------------------------------------
def run_siop_validator(siop_path: str) -> StageResult:
    """
    Run SIOP Validator. This is a GATE -- FAIL blocks the pipeline.
    Output: library/siop_validations/{VAL-ID}.json
    """
    stage_start = datetime.now()
    stage = StageResult(stage="3_siop_validator", status="running")
    logger.info(f"Stage 3: SIOP Validator | siop={siop_path}")

    try:
        from siop_validator import (
            load_json, validate_siop, save_validation
        )

        siop = load_json(siop_path)
        result = validate_siop(siop)
        save_validation(result)

        stage.score       = result.score
        stage.output_id   = result.validation_id
        stage.output_path = str(
            Path(os.getenv("SIOP_VALIDATION_PATH", "library/siop_validations"))
            / f"{result.validation_id}.json"
        )

        # Blocking issues -> stage fails -> pipeline stops
        for b in result.blocking_issues:
            stage.issues.append(f"{b.section}.{b.field}: {b.message}")

        # Warnings -> stage warns -> pipeline continues with caution
        for w in result.warnings[:5]:
            stage.warnings.append(f"{w.section}.{w.field}: {w.message}")

        if result.status == "FAIL":
            stage.status = "fail"
            logger.error(f"Stage 3 GATE BLOCKED | score={result.score} | blocking={len(result.blocking_issues)}")
        elif result.status == "PASS_WITH_WARNINGS":
            stage.status = "warn"
            logger.warning(f"Stage 3 PASS WITH WARNINGS | score={result.score} | warnings={len(result.warnings)}")
        else:
            stage.status = "ok"
            logger.success(f"Stage 3 PASS | score={result.score}")

    except ImportError as e:
        stage.status = "fail"
        stage.issues.append(f"siop_validator.py not found: {e}")
        logger.error(f"Stage 3 FAIL -- import: {e}")

    except Exception as e:
        stage.status = "fail"
        stage.issues.append(str(e))
        logger.error(f"Stage 3 FAIL: {e}", exc_info=True)

    stage.duration_sec = _duration(stage_start)
    return stage


# -- STAGE 4: ARCHITECT SIOP BRIDGE -------------------------------------------
def run_architect_bridge(siop_path: str) -> StageResult:
    """
    Run Architect SIOP Bridge to produce the ArchitectBlueprint.
    Output: library/architect_blueprints/{SIOP-ID}_blueprint.json
    """
    stage_start = datetime.now()
    stage = StageResult(stage="4_architect_bridge", status="running")
    logger.info(f"Stage 4: Architect SIOP Bridge | siop={siop_path}")

    try:
        from architect_siop_bridge import run_bridge

        blueprint = run_bridge(siop_path)

        blueprint_file = (
            BLUEPRINT_PATH / f"{blueprint.siop_id}_blueprint.json"
        )

        stage.status      = "ok" if blueprint.ready_for_builder else "warn"
        stage.output_id   = blueprint.blueprint_id
        stage.output_path = str(blueprint_file)
        stage.score       = float(blueprint.confidence_threshold or 0.85)

        if not blueprint.ready_for_builder:
            stage.warnings.append("Blueprint not ready for Builder -- missing_info blocks build")
            for m in blueprint.missing_info:
                if isinstance(m, dict) and m.get("severity") in ["critical", "high"]:
                    stage.issues.append(
                        f"missing [{m.get('severity','?')}]: {m.get('field','?')} -- {m.get('reason','')}"
                    )

        logger.success(
            f"Stage 4 OK | blueprint={blueprint.blueprint_id} "
            f"| steps={len(blueprint.steps)} | connectors={len(blueprint.connectors)} "
            f"| ready_for_builder={blueprint.ready_for_builder}"
        )

    except ImportError as e:
        stage.status = "fail"
        stage.issues.append(f"architect_siop_bridge.py not found: {e}")
        logger.error(f"Stage 4 FAIL -- import: {e}")

    except Exception as e:
        stage.status = "fail"
        stage.issues.append(str(e))
        logger.error(f"Stage 4 FAIL: {e}", exc_info=True)

    stage.duration_sec = _duration(stage_start)
    return stage


# -- PIPELINE ORCHESTRATOR -----------------------------------------------------
def run_customer_pipeline(
    audit_path: Optional[str] = None,
    fast_track_path: Optional[str] = None,
    documentation_path: Optional[str] = None,
    fa_path: Optional[str] = None,
    siop_path: Optional[str] = None,
    use_llm: bool = False,
) -> PipelineResult:
    """
    Run the full customer pipeline end-to-end.

    Entry points (three modes):
      1. Full:        audit_path provided -> runs all 4 stages
      2. From FA:     fa_path provided -> skips Stage 1
      3. From SIOP:   siop_path provided -> skips Stages 1-2

    Gates:
      - Stage 3 FAIL -> pipeline stops, reports blocking issues
      - Stage 4 issues -> pipeline completes but flags missing info
    """
    pipeline_id = datetime.now().strftime("%Y%m%d%H%M%S")
    result = PipelineResult(
        pipeline_id=pipeline_id,
        started_at=_now_iso(),
        status="running",
    )

    logger.info(f"Customer Pipeline starting | id={pipeline_id}")
    logger.info(f"Entry: audit={audit_path} | fa={fa_path} | siop={siop_path} | llm={use_llm}")

    # -- STAGE 1: FUNCTIONAL TRANSLATOR ----------------------------------------
    if siop_path:
        # Skipping stages 1 and 2 -- entry from SIOP
        s1 = StageResult(stage="1_functional_translator", status="skipped",
                         output_path=siop_path or "")
        result.stages.append(s1)
        s2 = StageResult(stage="2_siop_generator", status="skipped",
                         output_path=siop_path or "")
        result.stages.append(s2)
        current_siop_path = siop_path

    elif fa_path:
        # Skipping stage 1 -- entry from FunctionalAnalysis
        s1 = StageResult(stage="1_functional_translator", status="skipped",
                         output_path=fa_path)
        result.stages.append(s1)

        # Stage 2: SIOP Generator
        s2 = run_siop_generator(fa_path)
        result.stages.append(s2)

        if s2.status == "fail":
            result.status = "blocked"
            result.blocking_issues = s2.issues
            result.next_step = "Fix SIOP Generator input -- check functional_analysis.json"
            _finalize(result)
            return result

        current_siop_path = s2.output_path

    else:
        # Full pipeline: start from AUDIT ZERO
        if not audit_path:
            result.status = "failed"
            result.blocking_issues = ["No entry point provided: need --audit, --fa, or --siop"]
            _finalize(result)
            return result

        s1 = run_translator(audit_path, fast_track_path, documentation_path, use_llm)
        result.stages.append(s1)

        # Extract company and process name from FA for summary
        if s1.output_path:
            try:
                with open(s1.output_path, encoding="utf-8") as f:
                    fa_data = json.load(f)
                bc = fa_data.get("business_context", {})
                pc = fa_data.get("process_context", {})
                result.company = bc.get("company", "")
                result.process = pc.get("process_name", "")
            except Exception:
                pass

        if s1.status == "fail":
            result.status = "blocked"
            result.blocking_issues = s1.issues
            result.next_step = "Fix AUDIT ZERO JSON and retry"
            _finalize(result)
            return result

        # Stage 2: SIOP Generator
        s2 = run_siop_generator(s1.output_path)
        result.stages.append(s2)

        if s2.status == "fail":
            result.status = "blocked"
            result.blocking_issues = s2.issues
            result.next_step = "Fix functional_analysis output and retry from Stage 2"
            _finalize(result)
            return result

        current_siop_path = s2.output_path

    # -- STAGE 3: SIOP VALIDATOR (GATE) ----------------------------------------
    s3 = run_siop_validator(current_siop_path)
    result.stages.append(s3)

    if s3.status == "fail":
        result.status = "blocked"
        result.blocking_issues = s3.issues
        result.next_step = (
            "Resolve blocking issues in SIOP.\n"
            "Options:\n"
            "  1. Re-run AUDIT with more detail from the client\n"
            "  2. Use --use-llm flag for richer extraction\n"
            "  3. Manually enrich the functional_analysis.json"
        )
        _finalize(result)
        return result

    # PASS_WITH_WARNINGS: continue with caution, log all warnings
    if s3.status == "warn":
        logger.warning(f"Proceeding past Validator with {len(s3.warnings)} warnings")

    # -- STAGE 4: ARCHITECT SIOP BRIDGE ----------------------------------------
    s4 = run_architect_bridge(current_siop_path)
    result.stages.append(s4)

    if s4.status == "fail":
        result.status = "failed"
        result.blocking_issues = s4.issues
        result.next_step = "Fix Architect Bridge -- check architect_siop_bridge.py"
        _finalize(result)
        return result

    # -- PIPELINE COMPLETE -----------------------------------------------------
    result.blueprint_path    = s4.output_path
    result.blueprint_id      = s4.output_id
    result.ready_for_builder = (s4.status == "ok" and not s4.issues)

    # Collect all warnings and non-blocking issues
    all_warnings = []
    for stage in result.stages:
        all_warnings.extend(stage.warnings)

    # Missing info blocks builder readiness (not pipeline completion)
    high_missing = [i for i in s4.issues if "missing" in i.lower()]
    if high_missing:
        result.ready_for_builder = False
        result.next_step = (
            "Blueprint generated but missing critical technical info.\n"
            "Resolve missing_info items then re-run or proceed to Builder with dry-run mode."
        )
    else:
        result.next_step = f"python builder.py --blueprint {result.blueprint_path}"

    result.status = "complete"
    _finalize(result)
    return result


def _finalize(result: PipelineResult):
    result.completed_at = _now_iso()
    _save_pipeline_result(result)
    result.print_summary()
    total = sum(s.duration_sec for s in result.stages)
    logger.info(
        f"Pipeline {result.pipeline_id} {result.status.upper()} | "
        f"company={result.company} | process={result.process} | "
        f"duration={total:.1f}s | blueprint={result.blueprint_path}"
    )


# -- AUDIT ZERO BUILDER (for testing) ------------------------------------------
def build_audit_zero_from_inmaculada() -> dict:
    """
    Build the AUDIT ZERO JSON from Inmaculada's technical data sheet.
    In production this comes from audit.html Formspree submission.
    """
    return {
        "company":         "Empresa Transportes Inmaculada Sierra",
        "name":            "Inmaculada Sierra",
        "email":           "inmaculada@empresatransportes.com",
        "role":            "Directora de Operaciones",
        "sector":          "transport_distribution",
        "erp":             "SAP ECC 6.0 EHP8 SPS15",
        "volume":          "50",
        "team_size":       "1",
        "timing":          "immediate",
        "autonomy_level":  "AL1",
        "process_mapping": (
            "Order Management: Order Entry [BPMN-OTC-001] || "
            "Credit Management: Credit Check [SAP-FD32] || "
            "Transport Execution: Capacity Check [TMS-EXT]"
        ),
        "areas": "order_management,credit_management,transport_execution,billing",
        "notes": (
            "SAP ECC 6.0 EHP8 SPS15. Modulos: SD+MM+FI. TMS externo REST API. "
            "50 ordenes/dia: ZEST x35 + ZURG x8 + ZINT x5 + ZDEV x2. "
            "Credit check FD32. Price validation VK11 tolerancia 1pct. "
            "TMS capacidad en metros lineales. Operador: cmendoza@empresatransportes.com. "
            "S4HANA go-live Q4 2027."
        ),
    }


# -- CLI -----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Agentic Zero -- Customer Pipeline (AUDIT -> Blueprint)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Entry points:
  Full pipeline:     --audit path/to/audit_zero.json
  From FA:           --fa path/to/functional_analysis.json
  From SIOP:         --siop path/to/siop_internal.json
  Demo (Inmaculada): --demo

Examples:
  python customer_pipeline.py --audit clients/inmaculada/audit_zero.json
  python customer_pipeline.py --audit clients/inmaculada/audit_zero.json --use-llm
  python customer_pipeline.py --fa library/functional_analysis/FA-xxx.json
  python customer_pipeline.py --siop library/siop_internal/SIOP-xxx.json
  python customer_pipeline.py --demo
        """
    )

    parser.add_argument("--audit",      help="Path to AUDIT ZERO JSON (Formspree submission)")
    parser.add_argument("--fast-track", help="Path to Fast Track JSON (optional enrichment)")
    parser.add_argument("--docs",       help="Path to documentation text file (optional)")
    parser.add_argument("--fa",         help="Path to existing FunctionalAnalysis JSON (skip Stage 1)")
    parser.add_argument("--siop",       help="Path to existing SIOP JSON (skip Stages 1-2)")
    parser.add_argument("--use-llm",    action="store_true", help="Use LLM for richer extraction (Stage 1)")
    parser.add_argument("--demo",       action="store_true", help="Run demo with Inmaculada's data")

    args = parser.parse_args()

    if args.demo:
        # Demo mode: build AUDIT from Inmaculada's data, save it, run full pipeline
        import tempfile, os
        audit_data = build_audit_zero_from_inmaculada()
        demo_audit = Path("clients/inmaculada")
        demo_audit.mkdir(parents=True, exist_ok=True)
        demo_audit_file = demo_audit / "audit_zero.json"
        with open(demo_audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        print(f"Demo AUDIT saved: {demo_audit_file}")
        result = run_customer_pipeline(audit_path=str(demo_audit_file), use_llm=args.use_llm)

    elif args.siop:
        result = run_customer_pipeline(siop_path=args.siop)

    elif args.fa:
        result = run_customer_pipeline(fa_path=args.fa)

    elif args.audit:
        result = run_customer_pipeline(
            audit_path=args.audit,
            fast_track_path=args.fast_track,
            documentation_path=args.docs,
            use_llm=args.use_llm,
        )

    else:
        parser.print_help()
        sys.exit(1)
