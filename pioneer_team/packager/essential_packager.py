
"""
AGENTIC ZERO - PIONEER TEAM
Essential Packager v1.0

Recommended location:
  pioneer_team/packager/essential_packager.py
"""

from __future__ import annotations

import argparse, json, re, shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class PackageFile:
    key: str
    path: str
    exists: bool
    required: bool = True
    notes: str = ""


@dataclass
class EssentialPackageResult:
    package_id: str
    created_at: str
    package_dir: str
    company: str
    process_name: str
    process_id: str
    agent_class_name: str
    files: list[PackageFile]
    delivery_ready: bool
    warnings: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    next_step: str = ""
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "process").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "process"


def read_json(path: str | Path, default: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return default or {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_text(path: str | Path, content: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_json(path: str | Path, data: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def find_first(base: Path, patterns: list[str]) -> Optional[Path]:
    for pattern in patterns:
        matches = list(base.glob(pattern))
        if matches:
            return matches[0]
    return None


def bullet_list(values: Any) -> str:
    if not values:
        return "- Not defined"
    if isinstance(values, dict):
        values = list(values.values())
    if not isinstance(values, list):
        values = [values]
    return chr(10).join(f"- {v}" for v in values if str(v).strip()) or "- Not defined"


def load_context(package_dir: str | Path) -> dict[str, Any]:
    package_dir = Path(package_dir)

    functional_path = find_first(package_dir, ["01_functional_analysis/functional_analysis.json", "01_functional_analysis/*.json"])
    siop_path = find_first(package_dir, ["02_siop/siop_internal.json", "02_siop/SIOP*.json", "02_siop/*.json"])
    validation_path = find_first(package_dir, ["02_siop/siop_validation.json", "02_siop/VAL*.json"])
    blueprint_path = find_first(package_dir, ["03_blueprint/architect_blueprint.json", "03_blueprint/*blueprint*.json", "03_blueprint/*.json"])
    developer_manifest_path = find_first(package_dir, ["04_agent/developer_manifest.json"])

    functional = read_json(functional_path) if functional_path else {}
    siop = read_json(siop_path) if siop_path else {}
    validation = read_json(validation_path) if validation_path else {}
    blueprint = read_json(blueprint_path) if blueprint_path else {}
    developer = read_json(developer_manifest_path) if developer_manifest_path else {}

    bc = siop.get("business_context", {}) or functional.get("business_context", {})
    es = siop.get("executive_summary", {}) or {}

    company = blueprint.get("company") or bc.get("company") or functional.get("business_context", {}).get("company") or "Customer"
    process_name = es.get("process_name") or functional.get("process_context", {}).get("process_name") or blueprint.get("agent_description") or blueprint.get("process_id") or "Customer Process"

    return {
        "package_dir": str(package_dir),
        "paths": {
            "functional": str(functional_path) if functional_path else "",
            "siop": str(siop_path) if siop_path else "",
            "validation": str(validation_path) if validation_path else "",
            "blueprint": str(blueprint_path) if blueprint_path else "",
            "developer_manifest": str(developer_manifest_path) if developer_manifest_path else "",
        },
        "functional": functional,
        "siop": siop,
        "validation": validation,
        "blueprint": blueprint,
        "developer": developer,
        "company": company,
        "process_name": process_name,
        "process_id": blueprint.get("process_id") or siop.get("siop_id") or "",
        "agent_class_name": blueprint.get("agent_class_name") or developer.get("agent_class_name") or "",
    }


def generate_client_summary(ctx: dict[str, Any]) -> str:
    functional, siop, blueprint = ctx["functional"], ctx["siop"], ctx["blueprint"]
    bc = siop.get("business_context", {}) or functional.get("business_context", {})
    es = siop.get("executive_summary", {})
    autonomy = siop.get("autonomy_design", {})
    ac = siop.get("acceptance_criteria", {})
    return "\n".join([
        "# Agentic Zero Essential Package - Client Summary",
        "",
        "## Client",
        "",
        f"**Company:** {ctx['company']}  ",
        f"**Sector:** {bc.get('sector', '')}  ",
        f"**ERP/Core system:** {bc.get('erp', blueprint.get('erp', ''))}  ",
        f"**Volume:** {bc.get('volume', blueprint.get('volume', ''))}  ",
        f"**Team size:** {bc.get('team_size', '')}",
        "",
        "## Process",
        "",
        f"**Process:** {ctx['process_name']}  ",
        f"**Process ID:** {ctx.get('process_id', '')}  ",
        f"**Generated agent:** {ctx.get('agent_class_name', '')}",
        "",
        "## Business Goal",
        "",
        es.get("business_goal", "Enable safe agentic automation while preserving control, traceability and continuous improvement."),
        "",
        "## Validated Description",
        "",
        es.get("validated_description", blueprint.get("agent_description", "Customer-specific autonomous process agent.")),
        "",
        "## Autonomous Actions",
        "",
        bullet_list(autonomy.get("autonomous_actions", blueprint.get("autonomous_actions", []))),
        "",
        "## Approval Required",
        "",
        bullet_list(autonomy.get("approval_required", blueprint.get("approval_required", []))),
        "",
        "## Always Human",
        "",
        bullet_list(autonomy.get("always_human", blueprint.get("always_human", []))),
        "",
        "## KPIs",
        "",
        bullet_list(ac.get("kpis", blueprint.get("kpis", []))),
        "",
        "## Living Enterprise Layer",
        "",
        "This package includes learning hooks, audit trail, escalation signals and dashboard events so The Machine can learn from future execution.",
        "",
        "**Mantra:** Does this make it feel like a living enterprise?",
    ])


def generate_escalation_policy(ctx: dict[str, Any]) -> str:
    blueprint, siop = ctx["blueprint"], ctx["siop"]
    escalations = blueprint.get("escalations", [])
    autonomy = siop.get("autonomy_design", {})
    lines = [
        "# Escalation Policy", "",
        f"**Company:** {ctx['company']}",
        f"**Process:** {ctx['process_name']}",
        f"**Agent:** {ctx.get('agent_class_name', '')}",
        "", "## Purpose", "",
        "Define when the Essential agent acts autonomously, when it pauses, and when it escalates to a human owner.",
        "", "## Autonomous Actions", "",
        bullet_list(autonomy.get("autonomous_actions", blueprint.get("autonomous_actions", []))),
        "", "## Approval Required", "",
        bullet_list(autonomy.get("approval_required", blueprint.get("approval_required", []))),
        "", "## Always Human", "",
        bullet_list(autonomy.get("always_human", blueprint.get("always_human", []))),
        "", "## Escalation Scenarios", ""
    ]
    if escalations:
        for e in escalations:
            lines += [
                f"### {e.get('trigger', 'Escalation')}", "",
                f"- **Condition:** {e.get('condition', '')}",
                f"- **Recipient env var:** {e.get('recipient_env_var', '')}",
                f"- **Action:** {e.get('action', '')}",
                f"- **Auto-resolvable:** {e.get('auto_resolvable', False)}",
                f"- **Resolution hint:** {e.get('resolution_hint', '')}", ""
            ]
    else:
        lines.append("- No explicit escalations detected. Default: low-confidence decisions escalate to process owner.")
    lines += ["", "## Shield Controls", "", bullet_list(blueprint.get("shield_requirements", [])), "", "## Operating Rule", "", "Any action outside the validated autonomy boundaries must be blocked and escalated before execution."]
    return "\n".join(lines)


def generate_integration_guide(ctx: dict[str, Any]) -> str:
    blueprint = ctx["blueprint"]
    connectors = blueprint.get("connectors", [])
    lines = [
        "# Integration Guide", "",
        f"**Company:** {ctx['company']}",
        f"**Process:** {ctx['process_name']}",
        f"**ERP/Core system:** {blueprint.get('erp', '')}",
        "", "## Deployment Modes", "",
        "- dry-run: safe simulation with mock connectors.",
        "- qa: integration testing against QA/sandbox systems.",
        "- live: production mode after approval.",
        "", "## Agent Runtime", "",
        "```bash", "cd 04_agent", "python agent_runtime.py --mode dry-run", "```",
        "", "## Environment Variables", "",
        "Configure .env.example and rename it to .env when moving to QA/live.",
        "", "## Connectors", ""
    ]
    if connectors:
        for c in connectors:
            lines += [
                f"### {c.get('name', 'Connector')}", "",
                f"- **Type:** {c.get('type', '')}",
                f"- **System:** {c.get('system', '')}",
                f"- **Host env var:** {c.get('env_var_host', '')}",
                f"- **Credential env var:** {c.get('env_var_key', '')}",
                f"- **Operations:** {', '.join(c.get('operations', []))}",
                f"- **Dry-run mock:** {c.get('dry_run_mock', '')}", ""
            ]
    else:
        lines.append("- No connector metadata detected. Use dry-run mode until systems are mapped.")
    lines += ["", "## Validation Before Live", "", "1. Confirm system credentials.", "2. Confirm API/RFC access in QA.", "3. Run dry-run smoke tests.", "4. Run QA transaction tests.", "5. Validate audit trail.", "6. Validate escalation owners.", "7. Request Guardian/Auditor delivery approval."]
    return "\n".join(lines)


def generate_dashboard_html(ctx: dict[str, Any]) -> str:
    company, process, agent = ctx["company"], ctx["process_name"], ctx.get("agent_class_name", "")
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Agentic Zero Essential Dashboard - {company}</title>
<style>
body{{font-family:Arial,sans-serif;background:#07111f;color:#edf7ff;margin:0;padding:32px}}
.card{{background:#0d1b2f;border:1px solid #1d3a5c;border-radius:16px;padding:20px;margin:14px 0}}
h1{{color:#00e676}} h2{{color:#00d4ff}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.metric{{font-size:32px;font-weight:bold;color:#00e676}}
.small{{color:#9fb3c8;font-size:13px}}
</style></head><body>
<h1>Agentic Zero Essential Dashboard</h1>
<div class="small">Company: {company} - Process: {process} - Agent: {agent}</div>
<div class="grid">
<div class="card"><h2>Automation Status</h2><div class="metric">DRY-RUN</div><div class="small">Ready for QA validation</div></div>
<div class="card"><h2>Enterprise Pulse</h2><div class="metric">96%</div><div class="small">Simulated health baseline</div></div>
<div class="card"><h2>Human Oversight</h2><div class="metric">ACTIVE</div><div class="small">Escalation paths enabled</div></div>
</div>
<div class="card"><h2>Live Event Stream</h2><pre id="events">Waiting for dashboard_events.jsonl...</pre></div>
<div class="card"><h2>Learning Hooks</h2><p>The generated agent emits learning events for The Machine: process completion, exceptions, confidence deviation and escalation frequency.</p></div>
<script>document.getElementById("events").textContent="Dry-run dashboard generated. Connect dashboard_events.jsonl ingestion in QA/live mode.";</script>
</body></html>""".format(company=company, process=process, agent=agent)


def generate_roi_placeholder_html(ctx: dict[str, Any]) -> str:
    company, process = ctx["company"], ctx["process_name"]
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Agentic Zero ROI Calculator - {company}</title>
<style>
body{{font-family:Arial,sans-serif;background:#07111f;color:#edf7ff;margin:0;padding:32px}}
.card{{background:#0d1b2f;border:1px solid #1d3a5c;border-radius:16px;padding:20px;margin:14px 0}}
h1{{color:#00e676}} input{{padding:8px;margin:4px;background:#10233a;color:white;border:1px solid #315b82}}
button{{padding:10px 16px;background:#00e676;border:0;border-radius:8px;font-weight:bold}}
.metric{{font-size:28px;color:#00e676;font-weight:bold}}
</style></head><body>
<h1>ROI Calculator</h1><p>{company} - {process}</p>
<div class="card">
<label>Daily volume <input id="vol" type="number" value="50"></label><br>
<label>Manual minutes / transaction <input id="min" type="number" value="12"></label><br>
<label>Cost per hour EUR <input id="cost" type="number" value="25"></label><br>
<label>Automation rate (%) <input id="auto" type="number" value="75"></label><br>
<button onclick="calc()">Calculate</button>
</div>
<div class="card"><div>Annual manual saving</div><div class="metric" id="saving">EUR 0</div><div>Hours released / year</div><div class="metric" id="hours">0</div></div>
<script>
function calc(){{
 let vol=+document.getElementById('vol').value;
 let min=+document.getElementById('min').value;
 let cost=+document.getElementById('cost').value;
 let auto=+document.getElementById('auto').value/100;
 let hours=vol*min/60*220*auto;
 let saving=hours*cost;
 document.getElementById('saving').textContent='EUR '+Math.round(saving).toLocaleString();
 document.getElementById('hours').textContent=Math.round(hours).toLocaleString();
}}
calc();
</script></body></html>""".format(company=company, process=process)


def generate_sop_from_context(ctx: dict[str, Any]) -> tuple[str, bool]:
    """Returns (sop_markdown, has_steps). has_steps=False signals an empty/incomplete
    upstream SIOP or Blueprint -- callers should treat this as a packaging warning,
    not a silent success."""
    siop, blueprint = ctx["siop"], ctx["blueprint"]
    steps = siop.get("process_flow", []) or blueprint.get("steps", [])
    lines = [
        f"# SOP - {ctx['process_name']}", "",
        f"**Company:** {ctx['company']}",
        f"**Process ID:** {ctx.get('process_id', '')}",
        f"**Agent:** {ctx.get('agent_class_name', '')}",
        "", "## Purpose", "",
        "Define the operating procedure used by the generated Essential agent.",
        "", "## Process Steps", ""
    ]
    has_steps = bool(steps)
    if steps:
        for i, s in enumerate(steps, 1):
            lines += [
                f"{i}. **{s.get('name', 'Step')}**",
                f"   - System: {s.get('system', '')}",
                f"   - Inputs: {', '.join(s.get('inputs', []) or s.get('input', []))}",
                f"   - Outputs: {', '.join(s.get('outputs', []) or s.get('output', []))}",
                f"   - Rule: {s.get('rule', s.get('business_rule', ''))}", ""
            ]
    else:
        lines.append("No process steps detected. Re-run Functional Translator / Advanced AUDIT.")
    lines += ["", "## Exception Handling", "", "Exceptions are handled according to the Escalation Policy and Agentic Shield requirements.", "", "## Audit Trail", "", "Every autonomous decision must generate an audit entry with timestamp, rule, confidence and outcome.", "", "## Learning", "", "The agent emits learning hooks for The Machine to detect recurring exceptions, KPI deviations and improvement opportunities."]
    return "\n".join(lines), has_steps


def normalize_core_artifacts(ctx: dict[str, Any]) -> list[str]:
    package_dir = Path(ctx["package_dir"])
    warnings = []
    copy_map = [
        ("functional", "01_functional_analysis/functional_analysis.json"),
        ("siop", "02_siop/siop_internal.json"),
        ("validation", "02_siop/siop_validation.json"),
        ("blueprint", "03_blueprint/architect_blueprint.json"),
    ]
    for key, rel in copy_map:
        src = ctx["paths"].get(key)
        dst = package_dir / rel
        if src and Path(src).exists() and Path(src).resolve() != dst.resolve():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        elif not src:
            warnings.append(f"missing upstream artifact: {key}")
    return warnings


def collect_files(package_dir: str | Path) -> list[PackageFile]:
    package_dir = Path(package_dir)
    expected = {
        "functional_analysis_json": "01_functional_analysis/functional_analysis.json",
        "siop_internal_json": "02_siop/siop_internal.json",
        "siop_validation_json": "02_siop/siop_validation.json",
        "architect_blueprint_json": "03_blueprint/architect_blueprint.json",
        "agent_runtime_py": "04_agent/agent_runtime.py",
        "developer_manifest_json": "04_agent/developer_manifest.json",
        "sop_md": "05_delivery/sop.md",
        "integration_guide_md": "05_delivery/integration_guide.md",
        "escalation_policy_md": "05_delivery/escalation_policy.md",
        "client_executive_summary_md": "05_delivery/client_executive_summary.md",
        "dashboard_html": "05_delivery/dashboard.html",
        "roi_calculator_html": "05_delivery/roi_calculator.html",
        "guardian_certificate": "06_compliance/guardian_certificate.txt",
        "guardian_result_json": "06_compliance/guardian_result.json",
        "auditor_decision_json": "06_compliance/auditor_decision.json",
        "delivery_manifest_json": "delivery_manifest.json",
    }
    optional = {"guardian_certificate", "guardian_result_json", "auditor_decision_json"}
    return [
        PackageFile(k, str(package_dir / rel), (package_dir / rel).exists(), k not in optional, "optional until Guardian/Auditor run" if k in optional else "")
        for k, rel in expected.items()
    ]


def package_essential(package_dir: str | Path) -> EssentialPackageResult:
    package_dir = Path(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    ctx = load_context(package_dir)
    warnings = normalize_core_artifacts(ctx)
    delivery_dir = package_dir / "05_delivery"
    compliance_dir = package_dir / "06_compliance"
    delivery_dir.mkdir(parents=True, exist_ok=True)
    compliance_dir.mkdir(parents=True, exist_ok=True)

    write_text(delivery_dir / "client_executive_summary.md", generate_client_summary(ctx))
    write_text(delivery_dir / "escalation_policy.md", generate_escalation_policy(ctx))
    write_text(delivery_dir / "integration_guide.md", generate_integration_guide(ctx))
    write_text(delivery_dir / "dashboard.html", generate_dashboard_html(ctx))
    write_text(delivery_dir / "roi_calculator.html", generate_roi_placeholder_html(ctx))
    sop_text, sop_has_steps = generate_sop_from_context(ctx)
    write_text(delivery_dir / "sop.md", sop_text)
    if not sop_has_steps:
        warnings.append(
            "sop.md generated with NO process steps -- SIOP/Blueprint upstream "
            "appear empty. Do not deliver until re-run with valid upstream artifacts."
        )

    files = collect_files(package_dir)
    # delivery_manifest.json is written by THIS function, a few lines below --
    # it is the output of this run, not a prerequisite for it. Treating it as
    # a blocking "missing required file" check here always failed on a brand
    # new package's first run (the file genuinely doesn't exist yet at the
    # point collect_files() inspects the folder), even though every other
    # artifact was already correctly generated. Excluded from the blocking
    # check; still listed in `files` for visibility.
    blocking = [
        f"missing required file: {f.key}"
        for f in files
        if f.required and not f.exists and f.key != "delivery_manifest_json"
    ]
    ready = len(blocking) == 0
    result = EssentialPackageResult(
        package_id=f"EP-{_slug(ctx['company'])}-{_slug(ctx['process_name'])}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        package_dir=str(package_dir),
        company=ctx["company"],
        process_name=ctx["process_name"],
        process_id=ctx.get("process_id", ""),
        agent_class_name=ctx.get("agent_class_name", ""),
        files=files,
        delivery_ready=ready,
        warnings=warnings,
        blocking_issues=blocking,
        next_step="Run Guardian and Auditor, then re-run essential_packager.py to update compliance artifacts." if ready else "Generate missing required artifacts before delivery.",
    )
    write_json(package_dir / "delivery_manifest.json", asdict(result))
    return result


def run_cli(package_dir: str):
    result = package_essential(package_dir)
    print("\nEssential Packager complete")
    print(f"  Package: {result.package_id}")
    print(f"  Company: {result.company}")
    print(f"  Process: {result.process_name}")
    print(f"  Ready:   {result.delivery_ready}")
    print(f"  Files:   {len(result.files)}")
    if result.blocking_issues:
        print("\nBlocking issues:")
        for issue in result.blocking_issues:
            print(f"  - {issue}")
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Essential Packager")
    parser.add_argument("--package-dir", required=True, help="Path to customer essential_package folder")
    args = parser.parse_args()
    run_cli(args.package_dir)
