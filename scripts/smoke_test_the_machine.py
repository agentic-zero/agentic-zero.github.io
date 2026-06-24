"""
AGENTIC ZERO
Smoke Test - The Machine Initial Model v1.0

Run from repo root:

    python scripts/smoke_test_the_machine.py

Optional:

    python scripts/smoke_test_the_machine.py --client clients/distribuciones_norte/sop/essential_package
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StepResult:
    name: str
    command: list[str]
    returncode: int
    status: str
    stdout: str
    stderr: str


@dataclass
class FileCheck:
    label: str
    path: str
    exists: bool
    valid: bool
    kind: str
    error: str = ""


class SmokeTestTheMachine:
    def __init__(
        self,
        client: str | Path,
        python_bin: str = sys.executable,
        repo_root: str | Path = ".",
    ):
        self.repo_root = Path(repo_root).resolve()
        self.client = Path(client)
        self.python_bin = python_bin

        self.runtime_dir = self.client / "13_swarm_runtime"
        self.event_dir = self.runtime_dir / "events"
        self.swarm_config_dir = self.client / "10_swarm" / "runtime"
        self.coordination_file = self.detect_coordination_file()

        self.report_dir = self.repo_root / "test_reports"
        self.report_file = self.report_dir / "smoke_test_the_machine_report.json"

        self.shield_decisions_root = self.repo_root / "agentic_shield" / "decisions"
        self.shield_config_root = self.repo_root / "agentic_shield" / "config"
        self.shield_audit_root = self.repo_root / "agentic_shield" / "audit"
        self.shield_state_root = self.repo_root / "agentic_shield" / "state"

        self.steps: list[StepResult] = []
        self.file_checks: list[FileCheck] = []

    def detect_coordination_file(self) -> Path | None:
        """Auto-detect coordination/swarm_coordination_<process>.json so the
        smoke test works for any process type (sop, otc, ibp...) without
        hardcoding a filename. Returns None if not found (Event Catalog
        step then falls back to infra-only seed events).
        """
        coordination_dir = self.client / "10_swarm" / "coordination"
        if not coordination_dir.exists():
            return None
        matches = sorted(coordination_dir.glob("swarm_coordination_*.json"))
        return matches[0] if matches else None

    def ensure_dirs(self):
        for path in [
            self.repo_root / "scripts",
            self.repo_root / "runtime_core",
            self.repo_root / "the_machine",
            self.repo_root / "memory" / "working",
            self.repo_root / "memory" / "episodic",
            self.repo_root / "memory" / "semantic",
            self.repo_root / "memory" / "governance",
            self.event_dir,
            self.report_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def run_command(self, name: str, command: list[str]) -> StepResult:
        print("\n" + "-" * 72)
        print(f"STEP: {name}")
        print("CMD:  " + " ".join(command))
        print("-" * 72)

        completed = subprocess.run(
            command,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        status = "PASS" if completed.returncode == 0 else "FAIL"

        if completed.stdout:
            print(completed.stdout)
        if completed.stderr:
            print(completed.stderr)

        result = StepResult(
            name=name,
            command=command,
            returncode=completed.returncode,
            status=status,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

        self.steps.append(result)

        if completed.returncode != 0:
            raise RuntimeError(f"FAILED STEP: {name}")

        return result

    def run_steps(self):
        py = self.python_bin
        client = str(self.client)
        runtime = str(self.runtime_dir)
        events = str(self.event_dir)

        commands = [
            (
                "Event Bus",
                [
                    py,
                    "runtime_core/event_bus.py",
                    "--root-dir",
                    events,
                    "--emit-test",
                    "--status",
                ],
            ),
            (
                "Pulse Aggregator",
                [
                    py,
                    "runtime_core/pulse_aggregator.py",
                    "--event-dir",
                    events,
                ],
            ),
            (
                "Runtime Registry Init",
                [
                    py,
                    "runtime_core/runtime_registry.py",
                    "--root-dir",
                    runtime,
                    "--init-demo",
                ],
            ),
            (
                "Heartbeat Manager",
                [
                    py,
                    "runtime_core/heartbeat_manager.py",
                    "--root-dir",
                    runtime,
                    "--heartbeat-all",
                ],
            ),
            (
                "Health Manager",
                [
                    py,
                    "runtime_core/health_manager.py",
                    "--root-dir",
                    runtime,
                    "--event-dir",
                    events,
                    "--supervise",
                ],
            ),
            (
                "Degradation Manager",
                [
                    py,
                    "runtime_core/degradation_manager.py",
                    "--root-dir",
                    runtime,
                    "--detect",
                ],
            ),
            (
                "Event Catalog",
                [
                    py,
                    "runtime_core/event_catalog.py",
                    "--runtime-config-dir",
                    str(self.swarm_config_dir),
                    "--coordination-file",
                    str(self.coordination_file) if self.coordination_file else "",
                    "--events-dir",
                    events,
                    "--normalize",
                ],
            ),
            (
                "Event Router",
                [
                    py,
                    "runtime_core/event_router.py",
                    "--runtime-dir",
                    runtime,
                    "--emit-test",
                    "--route-all",
                ],
            ),
            (
                "Observer",
                [
                    py,
                    "the_machine/observer.py",
                    "--event-dir",
                    events,
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                    "--client-root",
                    client,
                ],
            ),
            (
                "Pattern Detector",
                [
                    py,
                    "the_machine/pattern_detector.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                    "--min-count",
                    "1",
                    "--emit-test",
                ],
            ),
            (
                "Prescriptor",
                [
                    py,
                    "the_machine/prescriptor.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Shield Policy Engine",
                [
                    py,
                    "agentic_shield/policy_engine.py",
                    "--memory-root",
                    "memory",
                    "--decisions-root",
                    str(self.shield_decisions_root),
                    "--state-root",
                    str(self.shield_state_root),
                    "--coordination-file",
                    str(self.coordination_file) if self.coordination_file else "",
                    "--client-root",
                    client,
                    "--thresholds-file",
                    str(self.shield_config_root / "thresholds.json"),
                    "--decide",
                ],
            ),
            (
                "Shield Compliance Engine",
                [
                    py,
                    "agentic_shield/compliance_engine.py",
                    "--decisions-root",
                    str(self.shield_decisions_root),
                    "--state-root",
                    str(self.shield_state_root),
                    "--client-root",
                    client,
                    "--review",
                ],
            ),
            (
                "Shield Threshold Engine",
                [
                    py,
                    "agentic_shield/threshold_engine.py",
                    "--decisions-root",
                    str(self.shield_decisions_root),
                    "--config-root",
                    str(self.shield_config_root),
                    "--state-root",
                    str(self.shield_state_root),
                    "--calibrate",
                ],
            ),
            (
                "Shield Approval Engine",
                [
                    py,
                    "agentic_shield/approval_engine.py",
                    "--decisions-root",
                    str(self.shield_decisions_root),
                    "--state-root",
                    str(self.shield_state_root),
                    "--process",
                ],
            ),
            (
                "Shield Human Accountability",
                [
                    py,
                    "agentic_shield/human_accountability.py",
                    "--decisions-root",
                    str(self.shield_decisions_root),
                    "--state-root",
                    str(self.shield_state_root),
                    "--queue",
                ],
            ),
            (
                "Shield Audit Trails",
                [
                    py,
                    "agentic_shield/audit_trails.py",
                    "--decisions-root",
                    str(self.shield_decisions_root),
                    "--audit-root",
                    str(self.shield_audit_root),
                    "--state-root",
                    str(self.shield_state_root),
                    "--consolidate",
                ],
            ),
            (
                "Improvement Engine",
                [
                    py,
                    "the_machine/improvement_engine.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Tautology Engine",
                [
                    py,
                    "the_machine/tautology_engine.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Evolution Engine",
                [
                    py,
                    "the_machine/evolution_engine.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Memory Governor",
                [
                    py,
                    "the_machine/memory_governor.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Confidence Engine",
                [
                    py,
                    "the_machine/confidence_engine.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Knowledge Injection",
                [
                    py,
                    "the_machine/knowledge_injection.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                    "--text",
                    (
                        "Initial smoke-test knowledge: The Machine must observe, learn, "
                        "prescribe, propose improvements and require human validation "
                        "before governance enforcement."
                    ),
                    "--title",
                    "Smoke Test Knowledge",
                    "--tags",
                    "smoke-test,the-machine",
                ],
            ),
            (
                "Cognitive Extensions",
                [
                    py,
                    "the_machine/cognitive_extensions.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Machine Dashboard State",
                [
                    py,
                    "the_machine/machine_dashboard_state.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
            (
                "Forgetting Engine",
                [
                    py,
                    "the_machine/forgetting_engine.py",
                    "--memory-root",
                    "memory",
                    "--state-root",
                    "the_machine/state",
                ],
            ),
        ]

        for name, command in commands:
            self.run_command(name, command)

    def validate_json(self, path: Path) -> tuple[bool, str]:
        if not path.exists():
            return False, "missing file"
        try:
            json.loads(path.read_text(encoding="utf-8"))
            return True, ""
        except Exception as exc:
            return False, str(exc)

    def validate_jsonl(self, path: Path) -> tuple[bool, str]:
        if not path.exists():
            return False, "missing file"

        lines = path.read_text(encoding="utf-8").splitlines()

        if not lines:
            return False, "empty jsonl"

        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except Exception as exc:
                return False, f"line {idx}: {exc}"

        return True, ""

    def check_file(self, label: str, path: str | Path, kind: str):
        path = Path(path)

        if kind == "json":
            valid, error = self.validate_json(path)
        elif kind == "jsonl":
            valid, error = self.validate_jsonl(path)
        else:
            exists = path.exists()
            valid = exists
            error = "" if exists else "missing file"

        check = FileCheck(
            label=label,
            path=str(path),
            exists=path.exists(),
            valid=valid,
            kind=kind,
            error=error,
        )

        self.file_checks.append(check)

        status = "OK" if check.exists and check.valid else "FAIL"
        print(f"{status}: {label} -> {path}")

        if not check.exists or not check.valid:
            raise RuntimeError(f"Invalid output: {label} -> {path} :: {error}")

    def validate_outputs(self):
        print("\n" + "=" * 72)
        print("VALIDATING OUTPUTS")
        print("=" * 72)

        e = self.event_dir
        r = self.runtime_dir

        checks = [
            ("Enterprise Health", e / "enterprise_health.json", "json"),
            ("Pulse Summary", e / "pulse_summary.json", "json"),
            ("Runtime Registry", r / "runtime_registry.json", "json"),
            ("Runtime Status", r / "runtime_status.json", "json"),
            ("Health Report", r / "health_report.json", "json"),
            ("Degradation Status", r / "degradation_status.json", "json"),
            ("Event Catalog", self.swarm_config_dir / "event_catalog.json", "json"),
            ("Shield Decisions", self.shield_decisions_root / "shield_decisions.json", "json"),
            ("Shield Compliance Review", self.shield_decisions_root / "compliance_review.json", "json"),
            ("Shield Thresholds", self.shield_config_root / "thresholds.json", "json"),
            ("Shield Approval Log", self.shield_decisions_root / "approval_log.json", "json"),
            ("Shield Sandbox Queue", self.shield_decisions_root / "sandbox_queue.json", "json"),
            ("Shield Human Review Queue", self.shield_decisions_root / "human_review_queue.json", "json"),
            ("Shield Consolidated Trail", self.shield_audit_root / "consolidated_trail.json", "json"),
            ("Heartbeat Events", r / "heartbeat_events.jsonl", "jsonl"),
            ("Swarm Events", e / "swarm_events.jsonl", "jsonl"),
            ("Audit Events", e / "audit_events.jsonl", "jsonl"),
            ("Learning Events", e / "learning_events.jsonl", "jsonl"),
            ("Pulse Events", e / "pulse_events.jsonl", "jsonl"),
            ("Routed Events", e / "routed_events.jsonl", "jsonl"),
            ("Routing Status", e / "routing_status.json", "json"),
            ("Episodic Memory", "memory/episodic/episodic_memory.jsonl", "jsonl"),
            ("Observed Patterns", "memory/semantic/observed_patterns.json", "json"),
            ("Detected Patterns", "memory/semantic/detected_patterns.json", "json"),
            ("Prescriptions", "memory/semantic/prescriptions.json", "json"),
            (
                "Improvement Proposals",
                "memory/semantic/improvement_proposals.json",
                "json",
            ),
            ("Tautology Rules", "memory/semantic/tautology_rules.json", "json"),
            ("Evolution Delta", "memory/semantic/evolution_delta.json", "json"),
            (
                "Memory Governance Report",
                "memory/governance/memory_governance_report.json",
                "json",
            ),
            (
                "Memory Retention Policy",
                "memory/governance/memory_retention_policy.json",
                "json",
            ),
            (
                "Meta Memory Candidates",
                "memory/governance/meta_memory_candidates.json",
                "json",
            ),
            (
                "Confidence Assessment",
                "memory/semantic/confidence_assessment.json",
                "json",
            ),
            ("Injected Knowledge", "memory/semantic/injected_knowledge.json", "json"),
            (
                "Forgetting Candidates",
                "memory/governance/forgetting_candidates.json",
                "json",
            ),
            ("Machine State", "the_machine/state/machine_state.json", "json"),
            (
                "Pattern Detector State",
                "the_machine/state/pattern_detector_state.json",
                "json",
            ),
            ("Prescriptor State", "the_machine/state/prescriptor_state.json", "json"),
            (
                "Improvement Engine State",
                "the_machine/state/improvement_engine_state.json",
                "json",
            ),
            (
                "Tautology Engine State",
                "the_machine/state/tautology_engine_state.json",
                "json",
            ),
            (
                "Evolution Engine State",
                "the_machine/state/evolution_engine_state.json",
                "json",
            ),
            (
                "Memory Governor State",
                "the_machine/state/memory_governor_state.json",
                "json",
            ),
            (
                "Confidence Engine State",
                "the_machine/state/confidence_engine_state.json",
                "json",
            ),
            (
                "Knowledge Injection State",
                "the_machine/state/knowledge_injection_state.json",
                "json",
            ),
            (
                "Cognitive Extensions State",
                "the_machine/state/cognitive_extensions_state.json",
                "json",
            ),
            ("Cortex Status", "the_machine/state/cortex_status.json", "json"),
            ("Latest Learning", "the_machine/state/latest_learning.json", "json"),
            ("Board Brief", "the_machine/state/board_brief.json", "json"),
            (
                "Machine Dashboard State",
                "the_machine/state/machine_dashboard_state.json",
                "json",
            ),
            (
                "Forgetting Engine State",
                "the_machine/state/forgetting_engine_state.json",
                "json",
            ),
        ]

        for label, path, kind in checks:
            self.check_file(label, path, kind)

    def read_json_file(self, path: str | Path, default: Any = None) -> Any:
        path = Path(path)
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def build_report(self, status: str, error: str = "") -> dict[str, Any]:
        dashboard = self.read_json_file(
            "the_machine/state/machine_dashboard_state.json", {}
        )
        evolution = self.read_json_file("memory/semantic/evolution_delta.json", {})
        pulse = self.read_json_file(self.event_dir / "enterprise_health.json", {})

        report = {
            "created_at": now(),
            "status": status,
            "error": error,
            "client": str(self.client),
            "runtime_dir": str(self.runtime_dir),
            "event_dir": str(self.event_dir),
            "steps": [asdict(s) for s in self.steps],
            "file_checks": [asdict(c) for c in self.file_checks],
            "summary": {
                "machine_status": dashboard.get("machine", {}).get("status", ""),
                "learning_status": dashboard.get("machine", {}).get(
                    "learning_status", ""
                ),
                "evolution_status": dashboard.get("evolution", {}).get("status", ""),
                "enterprise_health": pulse.get("health", None),
                "autonomy_delta": evolution.get("autonomy_delta", None),
                "intelligence_delta": evolution.get("intelligence_delta", None),
                "resilience_delta": evolution.get("resilience_delta", None),
                "governance_delta": evolution.get("governance_delta", None),
                "final_demo_line": dashboard.get("ui", {}).get("final_demo_line", ""),
            },
        }

        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        return report

    def run(self) -> int:
        print("\n" + "=" * 72)
        print("AGENTIC ZERO - THE MACHINE SMOKE TEST")
        print("=" * 72)
        print(f"Repo root: {self.repo_root}")
        print(f"Client:    {self.client}")
        print(f"Runtime:   {self.runtime_dir}")
        print(f"Events:    {self.event_dir}")

        try:
            self.ensure_dirs()
            self.run_steps()
            self.validate_outputs()
            report = self.build_report("PASS")

            print("\n" + "=" * 72)
            print("THE MACHINE SMOKE TEST PASSED")
            print("=" * 72)
            print(f"Machine status:      {report['summary']['machine_status']}")
            print(f"Learning status:     {report['summary']['learning_status']}")
            print(f"Evolution status:    {report['summary']['evolution_status']}")
            print(f"Enterprise health:   {report['summary']['enterprise_health']}%")
            print(f"Autonomy delta:      +{report['summary']['autonomy_delta']}%")
            print(f"Intelligence delta:  +{report['summary']['intelligence_delta']}%")
            print(f"Resilience delta:    +{report['summary']['resilience_delta']}%")
            print(f"Governance delta:    +{report['summary']['governance_delta']}%")
            print("\nFinal demo line:")
            print(f"  {report['summary']['final_demo_line']}")
            print(f"\nReport: {self.report_file}")

            return 0

        except Exception as exc:
            report = self.build_report("FAIL", str(exc))

            print("\n" + "=" * 72)
            print("THE MACHINE SMOKE TEST FAILED")
            print("=" * 72)
            print(str(exc))
            print(f"\nReport: {self.report_file}")

            return 1


def run_cli():
    parser = argparse.ArgumentParser(
        description="Agentic Zero - The Machine Smoke Test"
    )
    parser.add_argument(
        "--client",
        default="clients/distribuciones_norte/sop/essential_package",
        help="Client package directory",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root",
    )
    args = parser.parse_args()

    test = SmokeTestTheMachine(
        client=args.client,
        python_bin=args.python,
        repo_root=args.repo_root,
    )

    raise SystemExit(test.run())


if __name__ == "__main__":
    run_cli()
