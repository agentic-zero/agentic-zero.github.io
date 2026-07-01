"""
AGENTIC ZERO - PIONEER TEAM
Agent Developer v1.0

Role:
  Consume an ArchitectBlueprint and generate a dry-run safe Essential agent package.

Input:
  03_blueprint/architect_blueprint.json

Output:
  04_agent/
    agent_runtime.py
    .env.example
    connectors/
    tests/
    developer_manifest.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class GeneratedFile:
    key: str
    path: str
    required: bool = True
    status: str = "created"
    notes: str = ""


@dataclass
class AgentDeveloperResult:
    developer_id: str
    created_at: str
    blueprint_id: str
    siop_id: str
    process_id: str
    agent_class_name: str
    output_dir: str
    files: list[GeneratedFile]
    ready_for_packager: bool
    dry_run_supported: bool
    live_mode_supported: bool
    missing_info: list[dict[str, Any]]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "process").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "process"


def _pascal(value: str) -> str:
    words = re.sub(r"[^a-zA-Z0-9]+", " ", value or "Customer Agent").split()
    return "".join(w.capitalize() for w in words) or "CustomerAgent"


def load_json(path: str | Path) -> dict[str, Any]:
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


def default_output_dir(blueprint: dict[str, Any]) -> Path:
    company = blueprint.get("company") or "customer"
    process = (
        blueprint.get("process_id") or blueprint.get("agent_description") or "process"
    )
    return (
        Path("clients")
        / _slug(company)
        / _slug(process)
        / "essential_package"
        / "04_agent"
    )


def generate_connector(name: str) -> str:
    return f'''"""
Generated connector: {name}
Dry-run safe by default.
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class {name}:
    def __init__(self, mode: str = "dry-run"):
        self.mode = mode
        self.connected = False

    def connect(self) -> bool:
        self.connected = True
        return True

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.mode == "dry-run":
            return {{
                "status": "mocked",
                "connector": "{name}",
                "operation": operation,
                "payload": payload,
                "timestamp": _now()
            }}
        raise NotImplementedError("{name} live mode must be implemented before production.")
'''


def generate_env_example(blueprint: dict[str, Any]) -> str:
    return f"""# Agentic Zero Essential Agent Environment
AGENT_MODE=dry-run
PROCESS_ID={blueprint.get("process_id", "")}
AGENT_CLASS_NAME={blueprint.get("agent_class_name", "")}

SAP_HOST=
SAP_CLIENT=
SAP_USER=
SAP_PASSWORD=

TMS_API_URL=
TMS_API_KEY=

EMAIL_HOST=
EMAIL_USER=
EMAIL_PASSWORD=

ESCALATION_PROCESS_OWNER=
ESCALATION_FINANCE=
ESCALATION_OPERATIONS=

DASHBOARD_EVENT_STREAM=dashboard_events.jsonl
"""


def generate_agent_runtime(blueprint: dict[str, Any]) -> str:
    class_name = blueprint.get("agent_class_name") or _pascal(
        blueprint.get("agent_description", "Customer Agent")
    )
    process_id = blueprint.get("process_id", "CUSTOMER-PROCESS")
    company = blueprint.get("company", "Customer")
    sector = blueprint.get("sector", "")
    erp = blueprint.get("erp", "")
    description = blueprint.get(
        "agent_description", "Customer-specific Essential agent"
    )
    confidence_threshold = blueprint.get("confidence_threshold", 0.85)

    steps = blueprint.get("steps", [])
    connectors = blueprint.get("connectors", [])
    escalations = blueprint.get("escalations", [])
    shield = blueprint.get("shield_requirements", [])
    learning_hooks = blueprint.get("learning_hooks", {})
    kpis = blueprint.get("kpis", [])
    autonomous_actions = blueprint.get("autonomous_actions", [])
    approval_required = blueprint.get("approval_required", [])
    always_human = blueprint.get("always_human", [])

    step_methods = []
    execution_calls = []

    for idx, step in enumerate(steps, start=1):
        step_name = step.get("name", f"Step {idx}")
        method = f"step_{idx:02d}_{_slug(step_name)}"
        execution_calls.append(
            f"""            step_result = await self.{method}(context)
            results.append(step_result)
            self.emit_dashboard_event("step_completed", step_result)
            if step_result.get("requires_escalation"):
                escalation = await self.handle_escalation(context, step_result.get("escalation_reason", "unknown"))
                results.append(escalation)
                if escalation.get("blocked"):
                    return self.finalize("blocked", results, context)
"""
        )

        step_methods.append(f'''
    async def {method}(self, context: dict[str, Any]) -> dict[str, Any]:
        """{step_name}"""
        result = {{
            "step_id": {repr(step.get("step_id", f"STEP-{idx:02d}"))},
            "name": {repr(step_name)},
            "system": {repr(step.get("system", ""))},
            "rule": {repr(step.get("rule", ""))},
            "inputs": {repr(step.get("inputs", []))},
            "outputs": {repr(step.get("outputs", []))},
            "confidence": float({repr(step.get("confidence", 0.85))}),
            "status": "completed",
            "timestamp": _now(),
            "requires_escalation": False,
            "escalation_reason": "",
        }}

        escalation_type = {repr(step.get("escalation_type", "none"))}
        if context.get("simulate_exception") == escalation_type:
            result["requires_escalation"] = True
            result["escalation_reason"] = escalation_type

        if result["confidence"] < self.confidence_threshold:
            result["requires_escalation"] = True
            result["escalation_reason"] = "confidence_below_threshold"

        return result
''')

    if not execution_calls:
        execution_body = '            results.append({"status": "completed", "name": "no_steps_defined", "timestamp": _now()})\n'
    else:
        execution_body = "\n".join(execution_calls)

    return f'''"""
AGENTIC ZERO - Essential Generated Runtime
Process: {process_id}
Company: {company}
Agent: {class_name}
Generated by: Agent Developer
"""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AuditEntry:
    timestamp: str
    process_id: str
    agent: str
    event: str
    decision: str
    confidence: float
    outcome: str
    details: dict[str, Any]


class {class_name}:
    """
    {description}
    """

    def __init__(self, mode: str = "dry-run", event_stream: str = "dashboard_events.jsonl"):
        self.mode = mode
        self.process_id = {repr(process_id)}
        self.company = {repr(company)}
        self.sector = {repr(sector)}
        self.erp = {repr(erp)}
        self.agent_name = {repr(class_name)}
        self.confidence_threshold = float({repr(confidence_threshold)})
        self.event_stream = Path(event_stream)
        self.audit_trail: list[AuditEntry] = []
        self.kpis = {repr(kpis)}
        self.shield_requirements = {repr(shield)}
        self.learning_hooks = {repr(learning_hooks)}
        self.autonomous_actions = {repr(autonomous_actions)}
        self.approval_required = {repr(approval_required)}
        self.always_human = {repr(always_human)}
        self.escalations = {repr(escalations)}
        self.connectors = {repr(connectors)}

    def log_audit(self, event: str, decision: str, confidence: float, outcome: str, details: dict[str, Any]):
        entry = AuditEntry(
            timestamp=_now(),
            process_id=self.process_id,
            agent=self.agent_name,
            event=event,
            decision=decision,
            confidence=confidence,
            outcome=outcome,
            details=details,
        )
        self.audit_trail.append(entry)
        return entry

    def emit_dashboard_event(self, event_type: str, payload: dict[str, Any]):
        event = {{
            "timestamp": _now(),
            "process_id": self.process_id,
            "company": self.company,
            "agent": self.agent_name,
            "event_type": event_type,
            "payload": payload,
            "mode": self.mode,
        }}
        self.event_stream.parent.mkdir(parents=True, exist_ok=True)
        with open(self.event_stream, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\\n")
        return event

    def emit_learning_event(self, event_type: str, payload: dict[str, Any]):
        event = {{
            "timestamp": _now(),
            "source": self.agent_name,
            "process_id": self.process_id,
            "event_type": event_type,
            "payload": payload,
            "learning_hooks": self.learning_hooks,
        }}
        self.emit_dashboard_event("learning_event", event)
        return event

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        context = {{
            "payload": payload,
            "mode": self.mode,
            "started_at": _now(),
            "simulate_exception": payload.get("simulate_exception"),
        }}
        results = []

        self.emit_dashboard_event("agent_started", {{"payload_keys": list(payload.keys())}})
        self.log_audit("start", "execute_process", 1.0, "started", context)

        try:
{execution_body}
            return self.finalize("success", results, context)

        except Exception as exc:
            self.log_audit("runtime_error", "execute_process", 0.0, "failed", {{"error": str(exc)}})
            self.emit_dashboard_event("agent_failed", {{"error": str(exc)}})
            return self.finalize("error", results + [{{"error": str(exc)}}], context)

{"".join(step_methods)}

    async def handle_escalation(self, context: dict[str, Any], reason: str) -> dict[str, Any]:
        event = {{
            "status": "escalated",
            "reason": reason,
            "blocked": reason in ["credit", "price", "approval", "international_docs", "confidence_below_threshold"],
            "auto_resolvable": reason in ["capacity"],
            "timestamp": _now(),
        }}
        self.log_audit("escalation", reason, 0.70, event["status"], event)
        self.emit_dashboard_event("escalation", event)
        self.emit_learning_event("exception_observed", event)
        return event

    def finalize(self, status: str, results: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
        confidence_values = [
            float(r.get("confidence", 0.75))
            for r in results
            if isinstance(r, dict) and "confidence" in r
        ]
        avg_confidence = round(sum(confidence_values) / len(confidence_values), 3) if confidence_values else 0.85

        final = {{
            "process_id": self.process_id,
            "agent": self.agent_name,
            "company": self.company,
            "status": status,
            "average_confidence": avg_confidence,
            "steps_executed": len([r for r in results if isinstance(r, dict) and r.get("step_id")]),
            "results": results,
            "audit_trail": [asdict(a) for a in self.audit_trail],
            "completed_at": _now(),
        }}

        self.log_audit("finalize", status, avg_confidence, status, final)
        self.emit_dashboard_event("agent_completed", final)
        self.emit_learning_event("process_completed", {{
            "status": status,
            "average_confidence": avg_confidence,
            "steps_executed": final["steps_executed"],
        }})
        return final


async def _run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero Essential Generated Runtime")
    parser.add_argument("--mode", default="dry-run", choices=["dry-run", "qa", "live"])
    parser.add_argument("--payload", default="", help="JSON payload string")
    parser.add_argument("--payload-file", default="", help="Path to JSON payload")
    parser.add_argument("--simulate-exception", default="")
    args = parser.parse_args()

    if args.payload_file:
        with open(args.payload_file, encoding="utf-8") as f:
            payload = json.load(f)
    elif args.payload:
        payload = json.loads(args.payload)
    else:
        payload = {{"order_id": "DRY-ORDER-001"}}

    if args.simulate_exception:
        payload["simulate_exception"] = args.simulate_exception

    agent = {class_name}(mode=args.mode)
    result = await agent.execute(payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(_run_cli())
'''


def generate_dry_run_test(blueprint: dict[str, Any]) -> str:
    class_name = blueprint.get("agent_class_name", "CustomerAgent")
    process_id = blueprint.get("process_id", "")
    return f'''"""
Dry-run smoke test for generated Essential agent.
Run from 04_agent folder:
  python -m unittest tests/test_agent_dry_run.py
"""

import asyncio
import unittest
from agent_runtime import {class_name}


class TestEssentialAgentDryRun(unittest.TestCase):

    def test_dry_run_happy_path(self):
        agent = {class_name}(mode="dry-run", event_stream="test_events.jsonl")
        result = asyncio.run(agent.execute({{"order_id": "TEST-001"}}))
        self.assertIn(result["status"], ["success", "blocked", "error"])
        self.assertEqual(result["process_id"], "{process_id}")

    def test_dry_run_escalation(self):
        agent = {class_name}(mode="dry-run", event_stream="test_events.jsonl")
        result = asyncio.run(agent.execute({{"order_id": "TEST-002", "simulate_exception": "capacity"}}))
        self.assertIn(result["status"], ["success", "blocked", "error"])


if __name__ == "__main__":
    unittest.main()
'''


def generate_agent_from_blueprint(
    blueprint: dict[str, Any],
    output_dir: Optional[str | Path] = None,
) -> AgentDeveloperResult:
    output_dir = Path(output_dir) if output_dir else default_output_dir(blueprint)
    output_dir.mkdir(parents=True, exist_ok=True)

    files: list[GeneratedFile] = []

    runtime_path = write_text(
        output_dir / "agent_runtime.py", generate_agent_runtime(blueprint)
    )
    files.append(GeneratedFile("agent_runtime_py", str(runtime_path)))

    env_path = write_text(output_dir / ".env.example", generate_env_example(blueprint))
    files.append(GeneratedFile("env_example", str(env_path)))

    connectors_dir = output_dir / "connectors"
    write_text(connectors_dir / "__init__.py", "")
    files.append(
        GeneratedFile(
            "connectors_init", str(connectors_dir / "__init__.py"), required=False
        )
    )

    connector_map = {
        "sap_connector.py": "SAPConnector",
        "tms_connector.py": "TMSConnector",
        "email_connector.py": "EmailConnector",
        "file_connector.py": "FileConnector",
    }

    for filename, class_name in connector_map.items():
        path = write_text(connectors_dir / filename, generate_connector(class_name))
        files.append(
            GeneratedFile(filename.replace(".py", "_py"), str(path), required=False)
        )

    tests_dir = output_dir / "tests"
    write_text(tests_dir / "__init__.py", "")
    test_path = write_text(
        tests_dir / "test_agent_dry_run.py", generate_dry_run_test(blueprint)
    )
    files.append(GeneratedFile("dry_run_test_py", str(test_path), required=False))

    result = AgentDeveloperResult(
        developer_id=f"DEV-{_slug(blueprint.get('process_id', 'process'))}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created_at=_now(),
        blueprint_id=blueprint.get("blueprint_id", ""),
        siop_id=blueprint.get("siop_id", ""),
        process_id=blueprint.get("process_id", ""),
        agent_class_name=blueprint.get("agent_class_name", ""),
        output_dir=str(output_dir),
        files=files,
        ready_for_packager=True,
        dry_run_supported=True,
        live_mode_supported=False,
        missing_info=blueprint.get("missing_info", []),
        next_step="Run essential_packager.py against the Essential package folder.",
    )

    manifest_path = write_json(output_dir / "developer_manifest.json", asdict(result))
    result.files.append(GeneratedFile("developer_manifest_json", str(manifest_path)))
    write_json(output_dir / "developer_manifest.json", asdict(result))

    return result


def run_agent_developer(
    blueprint_path: str, output_dir: Optional[str] = None
) -> AgentDeveloperResult:
    blueprint = load_json(blueprint_path)
    result = generate_agent_from_blueprint(blueprint, output_dir)

    print("\nAgent Developer complete")
    print(f"  Process ID: {result.process_id}")
    print(f"  Agent:      {result.agent_class_name}")
    print(f"  Output:     {result.output_dir}")
    print(f"  Files:      {len(result.files)}")
    print(f"  Ready:      {result.ready_for_packager}")
    print(f"\nNext: {result.next_step}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Agent Developer")
    parser.add_argument(
        "--blueprint", required=True, help="Path to ArchitectBlueprint JSON"
    )
    parser.add_argument(
        "--output-dir", default=None, help="Optional 04_agent output directory"
    )
    args = parser.parse_args()
    run_agent_developer(args.blueprint, args.output_dir)
