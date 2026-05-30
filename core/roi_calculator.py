"""
AGENTIC ZERO — CORE
Module: ROI Calculator (M3)
Role: Calculate ROI of agent automation vs manual process

Used in:
  - AUDIT sessions (show ROI before client commits)
  - Sales demos
  - Packager Agent (pricing score)
  - Web tool (future)

No LLM required. Pure calculation logic.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from loguru import logger

# ── MODELS ────────────────────────────────────────────────────────────────────
class ManualProcessCost(BaseModel):
    """Cost of running a process manually"""
    process_id: str
    process_name: str

    # Human resources
    fte_involved: float              # Full-time equivalents involved
    hours_per_execution: float       # Hours per single execution
    executions_per_month: int        # How many times per month
    hourly_cost_eur: float           # Fully loaded hourly cost

    # Error and rework
    error_rate_pct: float            # % of executions with errors
    rework_hours_per_error: float    # Hours to fix each error
    error_cost_per_incident: float   # Cost per error incident

    # Compliance and audit
    compliance_hours_per_month: float # Hours spent on compliance docs
    audit_prep_hours_per_year: float  # Hours preparing for audits

    # Opportunity cost
    strategic_hours_lost: float      # Hours/month lost to non-strategic work

class AgentCost(BaseModel):
    """Cost of running the process with an AI agent"""
    process_id: str

    # Agentic Zero costs
    agent_monthly_fee_eur: float     # Monthly retainer or amortized fee
    setup_cost_eur: float            # One-time setup (AUDIT + deployment)
    tokens_per_execution: int        # LLM tokens per execution
    token_cost_per_1k: float         # Cost per 1000 tokens

    # Maintenance
    maintenance_hours_per_month: float  # Human oversight hours
    maintenance_hourly_cost: float

class ROIResult(BaseModel):
    """Complete ROI analysis"""
    process_id: str
    process_name: str
    calculation_date: str

    # Costs
    manual_monthly_cost_eur: float
    agent_monthly_cost_eur: float
    setup_cost_eur: float

    # Savings
    monthly_savings_eur: float
    annual_savings_eur: float
    payback_months: float

    # ROI metrics
    roi_12_months_pct: float
    roi_24_months_pct: float
    roi_36_months_pct: float

    # Efficiency metrics
    time_saved_hours_month: float
    error_reduction_pct: float
    compliance_time_saved_hours_month: float

    # Qualitative benefits
    qualitative_benefits: list[str]

    # Summary
    recommendation: str
    confidence_level: str           # high / medium / low
    assumptions: list[str]

# ── INDUSTRY BENCHMARKS ───────────────────────────────────────────────────────
INDUSTRY_BENCHMARKS = {
    "pharma": {
        "avg_hourly_cost": 85.0,
        "compliance_multiplier": 2.5,
        "error_cost_multiplier": 3.0,
        "audit_prep_hours_year": 240,
        "description": "GxP environment with high compliance overhead"
    },
    "defense": {
        "avg_hourly_cost": 90.0,
        "compliance_multiplier": 2.8,
        "error_cost_multiplier": 4.0,
        "audit_prep_hours_year": 200,
        "description": "AS9100 environment with strict quality requirements"
    },
    "chemical": {
        "avg_hourly_cost": 75.0,
        "compliance_multiplier": 2.0,
        "error_cost_multiplier": 2.5,
        "audit_prep_hours_year": 160,
        "description": "REACH/HARPC environment with safety criticality"
    },
    "food": {
        "avg_hourly_cost": 65.0,
        "compliance_multiplier": 1.8,
        "error_cost_multiplier": 2.0,
        "audit_prep_hours_year": 120,
        "description": "HACCP/FSMA environment"
    },
    "automotive": {
        "avg_hourly_cost": 72.0,
        "compliance_multiplier": 1.6,
        "error_cost_multiplier": 2.2,
        "audit_prep_hours_year": 100,
        "description": "IATF/APQP environment"
    },
    "manufacturing": {
        "avg_hourly_cost": 60.0,
        "compliance_multiplier": 1.4,
        "error_cost_multiplier": 1.8,
        "audit_prep_hours_year": 80,
        "description": "Standard manufacturing environment"
    },
    "distribution": {
        "avg_hourly_cost": 55.0,
        "compliance_multiplier": 1.3,
        "error_cost_multiplier": 1.5,
        "audit_prep_hours_year": 60,
        "description": "Logistics and distribution environment"
    }
}

PROCESS_BENCHMARKS = {
    "L1": {
        "avg_hours_per_execution": 0.5,
        "avg_executions_per_month": 20,
        "avg_fte": 0.5,
        "avg_error_rate": 0.05,
        "automation_efficiency": 0.90
    },
    "L2": {
        "avg_hours_per_execution": 2.0,
        "avg_executions_per_month": 10,
        "avg_fte": 1.0,
        "avg_error_rate": 0.08,
        "automation_efficiency": 0.85
    },
    "L3": {
        "avg_hours_per_execution": 6.0,
        "avg_executions_per_month": 5,
        "avg_fte": 1.5,
        "avg_error_rate": 0.12,
        "automation_efficiency": 0.75
    },
    "L4": {
        "avg_hours_per_execution": 16.0,
        "avg_executions_per_month": 2,
        "avg_fte": 2.0,
        "avg_error_rate": 0.15,
        "automation_efficiency": 0.65
    },
    "L5": {
        "avg_hours_per_execution": 40.0,
        "avg_executions_per_month": 1,
        "avg_fte": 3.0,
        "avg_error_rate": 0.20,
        "automation_efficiency": 0.55
    }
}

AGENTIC_ZERO_PRICING = {
    "L1": {"monthly_fee": 149,  "setup": 2500},
    "L2": {"monthly_fee": 499,  "setup": 8000},
    "L3": {"monthly_fee": 1500, "setup": 18000},
    "L4": {"monthly_fee": 3500, "setup": 35000},
    "L5": {"monthly_fee": 8000, "setup": 80000}
}

# ── CALCULATOR ────────────────────────────────────────────────────────────────
class ROICalculator:

    def calculate_from_process(
        self,
        process: dict,
        sector: str = "manufacturing",
        company_size: str = "medium",
        custom_hourly_rate: float = None
    ) -> ROIResult:
        """
        Calculate ROI from a library process entry.
        Uses industry benchmarks when specific data not available.
        """
        process_id = process.get("process_id", "UNKNOWN")
        process_name = process.get("name", "Unknown Process")
        level = process.get("level", "L2")

        benchmark_sector = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS["manufacturing"])
        benchmark_process = PROCESS_BENCHMARKS.get(level, PROCESS_BENCHMARKS["L2"])
        pricing = AGENTIC_ZERO_PRICING.get(level, AGENTIC_ZERO_PRICING["L2"])

        hourly_cost = custom_hourly_rate or benchmark_sector["avg_hourly_cost"]

        # Manual costs
        manual = ManualProcessCost(
            process_id=process_id,
            process_name=process_name,
            fte_involved=benchmark_process["avg_fte"],
            hours_per_execution=benchmark_process["avg_hours_per_execution"],
            executions_per_month=benchmark_process["avg_executions_per_month"],
            hourly_cost_eur=hourly_cost,
            error_rate_pct=benchmark_process["avg_error_rate"],
            rework_hours_per_error=benchmark_process["avg_hours_per_execution"] * 0.5,
            error_cost_per_incident=hourly_cost * benchmark_process["avg_hours_per_execution"] * 0.5,
            compliance_hours_per_month=benchmark_sector["audit_prep_hours_year"] / 12,
            audit_prep_hours_per_year=benchmark_sector["audit_prep_hours_year"],
            strategic_hours_lost=benchmark_process["avg_fte"] * 8 * 5
        )

        # Agent costs
        token_cost = 0.0  # Groq free tier
        agent = AgentCost(
            process_id=process_id,
            agent_monthly_fee_eur=pricing["monthly_fee"],
            setup_cost_eur=pricing["setup"],
            tokens_per_execution=5000,
            token_cost_per_1k=token_cost,
            maintenance_hours_per_month=2.0,
            maintenance_hourly_cost=hourly_cost
        )

        return self.calculate(manual, agent, sector, benchmark_process)

    def calculate(
        self,
        manual: ManualProcessCost,
        agent: AgentCost,
        sector: str = "manufacturing",
        process_benchmark: dict = None
    ) -> ROIResult:
        """Core ROI calculation"""
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS["manufacturing"])
        proc_bench = process_benchmark or PROCESS_BENCHMARKS["L2"]

        # ── MANUAL MONTHLY COST ───────────────────────────────────────────────
        execution_cost = (
            manual.hours_per_execution *
            manual.executions_per_month *
            manual.hourly_cost_eur
        )

        error_cost = (
            manual.executions_per_month *
            manual.error_rate_pct *
            manual.error_cost_per_incident *
            benchmark["error_cost_multiplier"]
        )

        compliance_cost = (
            manual.compliance_hours_per_month *
            manual.hourly_cost_eur *
            benchmark["compliance_multiplier"]
        )

        opportunity_cost = (
            manual.strategic_hours_lost *
            manual.hourly_cost_eur * 0.3
        )

        manual_monthly = execution_cost + error_cost + compliance_cost + opportunity_cost

        # ── AGENT MONTHLY COST ────────────────────────────────────────────────
        token_monthly = (
            manual.executions_per_month *
            agent.tokens_per_execution *
            agent.token_cost_per_1k / 1000
        )

        maintenance_monthly = (
            agent.maintenance_hours_per_month *
            agent.maintenance_hourly_cost
        )

        agent_monthly = agent.agent_monthly_fee_eur + token_monthly + maintenance_monthly

        # ── SAVINGS ───────────────────────────────────────────────────────────
        monthly_savings = manual_monthly - agent_monthly
        annual_savings = monthly_savings * 12
        payback_months = agent.setup_cost_eur / monthly_savings if monthly_savings > 0 else 999

        # ── ROI ───────────────────────────────────────────────────────────────
        def calc_roi(months: int) -> float:
            total_savings = monthly_savings * months
            total_cost = agent.setup_cost_eur + (agent_monthly * months)
            if total_cost == 0:
                return 0
            return ((total_savings - agent.setup_cost_eur) / agent.setup_cost_eur) * 100

        roi_12 = calc_roi(12)
        roi_24 = calc_roi(24)
        roi_36 = calc_roi(36)

        # ── EFFICIENCY METRICS ────────────────────────────────────────────────
        automation_efficiency = proc_bench.get("automation_efficiency", 0.80)
        time_saved = (
            manual.hours_per_execution *
            manual.executions_per_month *
            automation_efficiency
        )

        error_reduction = manual.error_rate_pct * automation_efficiency * 100
        compliance_saved = manual.compliance_hours_per_month * 0.7

        # ── QUALITATIVE BENEFITS ──────────────────────────────────────────────
        qualitative = [
            f"24/7 autonomous operation — no human bottlenecks",
            f"Audit trail generated automatically for every execution",
            f"Consistent execution — no variance between runs",
            f"Scales to {manual.executions_per_month * 10}x volume without additional cost",
            f"EU AI Act compliant from day 1",
            f"Frees {time_saved:.0f}h/month of expert time for strategic work"
        ]

        if sector in ["pharma", "defense", "medtech"]:
            qualitative.append(f"GxP/regulatory compliance embedded — audit-ready always")
        if sector in ["pharma", "food"]:
            qualitative.append(f"Eliminates human error in critical control points")

        # ── RECOMMENDATION ────────────────────────────────────────────────────
        if roi_12 > 200:
            recommendation = f"STRONG BUY — {roi_12:.0f}% ROI in 12 months. Payback in {payback_months:.1f} months."
            confidence = "high"
        elif roi_12 > 100:
            recommendation = f"RECOMMENDED — {roi_12:.0f}% ROI in 12 months. Solid business case."
            confidence = "high"
        elif roi_12 > 50:
            recommendation = f"POSITIVE — {roi_12:.0f}% ROI in 12 months. Good long-term value."
            confidence = "medium"
        else:
            recommendation = f"MARGINAL — Consider higher-complexity processes for better ROI."
            confidence = "medium"

        assumptions = [
            f"Sector: {sector} — hourly cost €{manual.hourly_cost_eur:.0f}",
            f"Process level: {manual.process_id.split('-')[0] if '-' in manual.process_id else 'L2'}",
            f"Executions: {manual.executions_per_month}/month",
            f"Automation efficiency: {automation_efficiency*100:.0f}%",
            f"Error reduction: {error_reduction:.0f}%",
            "Token costs: €0.00 (Groq free tier)",
            "Based on industry benchmarks — validate with client data"
        ]

        return ROIResult(
            process_id=manual.process_id,
            process_name=manual.process_name,
            calculation_date=datetime.now().isoformat(),
            manual_monthly_cost_eur=round(manual_monthly, 2),
            agent_monthly_cost_eur=round(agent_monthly, 2),
            setup_cost_eur=agent.setup_cost_eur,
            monthly_savings_eur=round(monthly_savings, 2),
            annual_savings_eur=round(annual_savings, 2),
            payback_months=round(payback_months, 1),
            roi_12_months_pct=round(roi_12, 1),
            roi_24_months_pct=round(roi_24, 1),
            roi_36_months_pct=round(roi_36, 1),
            time_saved_hours_month=round(time_saved, 1),
            error_reduction_pct=round(error_reduction, 1),
            compliance_time_saved_hours_month=round(compliance_saved, 1),
            qualitative_benefits=qualitative,
            recommendation=recommendation,
            confidence_level=confidence,
            assumptions=assumptions
        )

    def print_report(self, result: ROIResult):
        """Print formatted ROI report"""
        print(f"\n{'='*60}")
        print(f"ROI ANALYSIS — Agentic Zero")
        print(f"{'='*60}")
        print(f"Process: {result.process_name}")
        print(f"ID:      {result.process_id}")
        print(f"Date:    {result.calculation_date[:10]}")
        print(f"\n{'─'*60}")
        print(f"COST COMPARISON (monthly)")
        print(f"{'─'*60}")
        print(f"  Manual process:     €{result.manual_monthly_cost_eur:>10,.2f}/month")
        print(f"  Agentic Zero:       €{result.agent_monthly_cost_eur:>10,.2f}/month")
        print(f"  Monthly savings:    €{result.monthly_savings_eur:>10,.2f}/month")
        print(f"  Annual savings:     €{result.annual_savings_eur:>10,.2f}/year")
        print(f"  Setup cost:         €{result.setup_cost_eur:>10,.2f} (one-time)")
        print(f"  Payback period:     {result.payback_months:>10.1f} months")
        print(f"\n{'─'*60}")
        print(f"ROI PROJECTION")
        print(f"{'─'*60}")
        print(f"  12 months:          {result.roi_12_months_pct:>9.1f}%")
        print(f"  24 months:          {result.roi_24_months_pct:>9.1f}%")
        print(f"  36 months:          {result.roi_36_months_pct:>9.1f}%")
        print(f"\n{'─'*60}")
        print(f"EFFICIENCY GAINS")
        print(f"{'─'*60}")
        print(f"  Time saved:         {result.time_saved_hours_month:>9.1f} h/month")
        print(f"  Error reduction:    {result.error_reduction_pct:>9.1f}%")
        print(f"  Compliance saved:   {result.compliance_time_saved_hours_month:>9.1f} h/month")
        print(f"\n{'─'*60}")
        print(f"QUALITATIVE BENEFITS")
        print(f"{'─'*60}")
        for b in result.qualitative_benefits:
            print(f"  ✓ {b}")
        print(f"\n{'─'*60}")
        print(f"RECOMMENDATION ({result.confidence_level.upper()} confidence)")
        print(f"{'─'*60}")
        print(f"  {result.recommendation}")
        print(f"\n{'─'*60}")
        print(f"ASSUMPTIONS")
        print(f"{'─'*60}")
        for a in result.assumptions:
            print(f"  • {a}")
        print(f"{'='*60}\n")

    def save_report(self, result: ROIResult, output_path: Path = None):
        """Save ROI report as JSON"""
        if output_path is None:
            output_path = Path("logs") / f"roi_{result.process_id}_{datetime.now().strftime('%Y%m%d')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
        return output_path

# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    import argparse
    import sys
    ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(ROOT))

    parser = argparse.ArgumentParser(description="Agentic Zero ROI Calculator (M3)")
    parser.add_argument("process_id", help="Process ID to calculate ROI for (e.g. SCOR-P1.1)")
    parser.add_argument("--sector", default="manufacturing",
                       choices=list(INDUSTRY_BENCHMARKS.keys()),
                       help="Industry sector")
    parser.add_argument("--hourly-rate", type=float, help="Custom hourly cost in EUR")
    parser.add_argument("--save", action="store_true", help="Save report as JSON")
    args = parser.parse_args()

    # Load process from library
    from dotenv import load_dotenv
    load_dotenv()

    library_path = Path(os.getenv("LIBRARY_PATH", str(ROOT / "library")))
    process = None

    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        proc_file = library_path / folder / "processes" / f"{args.process_id}.json"
        if proc_file.exists():
            with open(proc_file, "r", encoding="utf-8") as f:
                process = json.load(f)
            break

    if not process:
        print(f"❌ Process {args.process_id} not found in library")
        sys.exit(1)

    calc = ROICalculator()
    result = calc.calculate_from_process(
        process=process,
        sector=args.sector,
        custom_hourly_rate=args.hourly_rate
    )

    calc.print_report(result)

    if args.save:
        path = calc.save_report(result)
        print(f"Report saved: {path}")

if __name__ == "__main__":
    main()
