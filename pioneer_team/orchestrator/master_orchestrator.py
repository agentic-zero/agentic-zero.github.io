"""
AGENTIC ZERO - PIONEER TEAM
Master Orchestrator v1.0

Role:
  Coordinate the Agentic Zero factory build pipeline.

Important separation:
  - master_orchestrator.py coordinates the FACTORY.
  - agent_runner.py keeps the CUSTOMER AGENT alive.
  - The Machine observes both.

Recommended location:
  pioneer_team/orchestrator/master_orchestrator.py

Input:
  --package-dir clients/{client}/{process}/essential_package
  --mode FULL_BUILD | REBUILD_FROM_SIOP | REBUILD_FROM_BLUEPRINT | DELIVERY_ONLY | DRY_RUN

Output:
  09_orchestrator/
    pipeline_execution.json
    execution_history.jsonl
    orchestrator_state.json
    factory_learning_events.jsonl

Mantra:
  Does this make it feel like a living enterprise?
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------


@dataclass
class PipelineStep:
    name: str
    command: list[str]
    required: bool = True
    status: str = "WAITING"  # WAITING | RUNNING | SUCCESS | WARNING | FAILED | SKIPPED
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0
    return_code: int = 0
    stdout_tail: str = ""
    stderr_tail: str = ""


@dataclass
class FactoryEvent:
    timestamp: str
    event_type: str
    package_dir: str
    component: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorResult:
    package_dir: str
    mode: str
    started_at: str
    finished_at: str
    status: str
    duration_seconds: float
    steps: list[PipelineStep]
    delivery_score: float
    rework_required: bool
    human_intervention_required: bool
    outputs: dict[str, str]
    next_step: str
    mantra: str = "Does this make it feel like a living enterprise?"


# ---------------------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(
    path: str | Path, default: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return default or {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def append_jsonl(path: str | Path, payload: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path


def tail(text: str, limit: int = 2000) -> str:
    return (text or "")[-limit:]


def normalize_score(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, str):
        value = value.replace("%", "").strip()
        try:
            value = float(value)
        except Exception:
            return 0.0
    if isinstance(value, (int, float)):
        if value > 1:
            return round(float(value) / 100, 2)
        return round(float(value), 2)
    return 0.0


def repo_root() -> Path:
    root = Path.cwd()
    while root.name != "agentic-zero" and root.parent != root:
        root = root.parent
    return root


# ---------------------------------------------------------------------------
# ORCHESTRATOR
# ---------------------------------------------------------------------------


class MasterOrchestrator:
    def __init__(self, package_dir: str | Path, mode: str = "FULL_BUILD"):
        self.root = repo_root()
        self.package_dir = Path(package_dir)
        self.mode = mode.upper()
        self.out_dir = self.package_dir / "09_orchestrator"
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.execution_path = self.out_dir / "pipeline_execution.json"
        self.history_path = self.out_dir / "execution_history.jsonl"
        self.state_path = self.out_dir / "orchestrator_state.json"
        self.learning_events_path = self.out_dir / "factory_learning_events.jsonl"

    # -----------------------------------------------------------------------
    # EVENTING
    # -----------------------------------------------------------------------

    def emit(
        self,
        event_type: str,
        component: str,
        status: str,
        payload: Optional[dict[str, Any]] = None,
    ):
        event = FactoryEvent(
            timestamp=_now(),
            event_type=event_type,
            package_dir=str(self.package_dir),
            component=component,
            status=status,
            payload=payload or {},
        )
        append_jsonl(self.history_path, asdict(event))
        append_jsonl(self.learning_events_path, self.to_learning_event(event))
        return event

    def to_learning_event(self, event: FactoryEvent) -> dict[str, Any]:
        """
        Factory learning language consumed later by The Machine.

        These are meta-learning events: they describe how Agentic Zero builds
        agents, not how the customer process operates.
        """
        return {
            "timestamp": event.timestamp,
            "source": "master_orchestrator",
            "event_type": event.event_type,
            "component": event.component,
            "status": event.status,
            "package_dir": event.package_dir,
            "learning_hooks": {
                "failure_pattern": event.payload.get("failure_pattern", ""),
                "build_duration": event.payload.get("duration_seconds", 0),
                "rework_required": event.payload.get("rework_required", False),
                "human_intervention": event.payload.get(
                    "human_intervention_required", False
                ),
                "delivery_score": event.payload.get("delivery_score", 0),
            },
            "payload": event.payload,
        }

    # -----------------------------------------------------------------------
    # PIPELINE DEFINITION
    # -----------------------------------------------------------------------

    def build_steps(self) -> list[PipelineStep]:
        py = sys.executable

        all_steps = [
            PipelineStep(
                name="essential_packager",
                command=[
                    py,
                    "pioneer_team/packager/essential_packager.py",
                    "--package-dir",
                    str(self.package_dir),
                ],
            ),
            PipelineStep(
                name="guardian_adapter",
                command=[
                    py,
                    "pioneer_team/guardian/guardian_adapter.py",
                    "--package-dir",
                    str(self.package_dir),
                ],
            ),
            PipelineStep(
                name="auditor_adapter",
                command=[
                    py,
                    "pioneer_team/auditor/auditor_adapter.py",
                    "--package-dir",
                    str(self.package_dir),
                ],
            ),
            PipelineStep(
                name="delivery_gate",
                command=[
                    py,
                    "pioneer_team/delivery/delivery_gate.py",
                    "--package-dir",
                    str(self.package_dir),
                ],
            ),
        ]

        if self.mode == "DELIVERY_ONLY":
            return all_steps

        if self.mode == "DRY_RUN":
            return [
                PipelineStep(
                    name="dry_run_structure_check",
                    command=[
                        py,
                        "-c",
                        (
                            "from pathlib import Path; "
                            f"p=Path(r'{self.package_dir}'); "
                            "print('package_exists=', p.exists()); "
                            "print('children=', [x.name for x in p.iterdir()] if p.exists() else [])"
                        ),
                    ],
                )
            ]

        if self.mode == "REBUILD_FROM_BLUEPRINT":
            return [
                PipelineStep(
                    name="agent_developer",
                    command=[
                        py,
                        "pioneer_team/builder/agent_developer.py",
                        "--blueprint",
                        str(
                            self.package_dir
                            / "03_blueprint"
                            / "architect_blueprint.json"
                        ),
                        "--output-dir",
                        str(self.package_dir / "04_agent"),
                    ],
                ),
                *all_steps,
            ]

        if self.mode == "REBUILD_FROM_SIOP":
            return [
                PipelineStep(
                    name="architect_siop_bridge",
                    command=[
                        py,
                        "pioneer_team/architect/architect_siop_bridge.py",
                        "--siop",
                        str(self.package_dir / "02_siop" / "siop_internal.json"),
                        "--output",
                        str(
                            self.package_dir
                            / "03_blueprint"
                            / "architect_blueprint.json"
                        ),
                    ],
                    required=False,
                ),
                PipelineStep(
                    name="agent_developer",
                    command=[
                        py,
                        "pioneer_team/builder/agent_developer.py",
                        "--blueprint",
                        str(
                            self.package_dir
                            / "03_blueprint"
                            / "architect_blueprint.json"
                        ),
                        "--output-dir",
                        str(self.package_dir / "04_agent"),
                    ],
                ),
                *all_steps,
            ]

        # FULL_BUILD currently assumes upstream customer_pipeline already produced
        # functional/SIOP/blueprint or the package folder has those artifacts.
        # We keep it non-destructive and compatible with existing structure.
        return [
            PipelineStep(
                name="essential_blueprint_contract",
                command=[
                    py,
                    "pioneer_team/architect/essential_blueprint.py",
                    "--client",
                    str(
                        self.package_dir
                        / "01_functional_analysis"
                        / "functional_analysis.json"
                    ),
                    "--package-dir",
                    str(self.package_dir),
                    "--siop",
                    str(self.package_dir / "02_siop" / "siop_internal.json"),
                    "--blueprint",
                    str(self.package_dir / "03_blueprint" / "architect_blueprint.json"),
                ],
                required=False,
            ),
            PipelineStep(
                name="agent_developer",
                command=[
                    py,
                    "pioneer_team/builder/agent_developer.py",
                    "--blueprint",
                    str(self.package_dir / "03_blueprint" / "architect_blueprint.json"),
                    "--output-dir",
                    str(self.package_dir / "04_agent"),
                ],
            ),
            *all_steps,
        ]

    # -----------------------------------------------------------------------
    # EXECUTION
    # -----------------------------------------------------------------------

    def run_step(self, step: PipelineStep) -> PipelineStep:
        step.status = "RUNNING"
        step.started_at = _now()
        start = time.time()

        self.emit("COMPONENT_STARTED", step.name, "RUNNING", {"command": step.command})
        self.save_state("RUNNING")

        try:
            completed = subprocess.run(
                step.command,
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=600,
            )
            step.return_code = completed.returncode
            step.stdout_tail = tail(completed.stdout)
            step.stderr_tail = tail(completed.stderr)

            if completed.returncode == 0:
                step.status = "SUCCESS"
                self.emit(
                    "COMPONENT_COMPLETED",
                    step.name,
                    "SUCCESS",
                    {
                        "duration_seconds": round(time.time() - start, 2),
                        "stdout_tail": step.stdout_tail,
                    },
                )
            else:
                step.status = "FAILED" if step.required else "WARNING"
                self.emit(
                    "COMPONENT_FAILED",
                    step.name,
                    step.status,
                    {
                        "return_code": completed.returncode,
                        "stderr_tail": step.stderr_tail,
                        "stdout_tail": step.stdout_tail,
                        "failure_pattern": self.classify_failure(
                            step.stderr_tail + "\n" + step.stdout_tail
                        ),
                        "rework_required": True,
                        "human_intervention_required": step.required,
                    },
                )

        except subprocess.TimeoutExpired as exc:
            step.status = "FAILED" if step.required else "WARNING"
            step.return_code = -1
            step.stderr_tail = f"Timeout: {exc}"
            self.emit(
                "COMPONENT_FAILED",
                step.name,
                step.status,
                {
                    "failure_pattern": "timeout",
                    "rework_required": True,
                    "human_intervention_required": step.required,
                },
            )

        except Exception as exc:
            step.status = "FAILED" if step.required else "WARNING"
            step.return_code = -2
            step.stderr_tail = str(exc)
            self.emit(
                "COMPONENT_FAILED",
                step.name,
                step.status,
                {
                    "failure_pattern": self.classify_failure(str(exc)),
                    "rework_required": True,
                    "human_intervention_required": step.required,
                },
            )

        step.finished_at = _now()
        step.duration_seconds = round(time.time() - start, 2)
        self.save_state(step.status)
        return step

    def classify_failure(self, text: str) -> str:
        text = (text or "").lower()
        if "not found" in text or "filenotfound" in text:
            return "missing_artifact"
        if "json" in text and ("decode" in text or "invalid" in text):
            return "invalid_json"
        if "syntaxerror" in text:
            return "syntax_error"
        if "guardian" in text:
            return "compliance_failure"
        if "auditor" in text:
            return "audit_failure"
        if "timeout" in text:
            return "timeout"
        return "unknown_failure"

    # -----------------------------------------------------------------------
    # RESULT
    # -----------------------------------------------------------------------

    def delivery_score(self) -> float:
        status_path = (
            self.package_dir / "08_delivery_gate" / "final_delivery_status.json"
        )
        status = read_json(status_path)
        return normalize_score(status.get("score"))

    def save_state(self, status: str):
        write_json(
            self.state_path,
            {
                "package_dir": str(self.package_dir),
                "mode": self.mode,
                "status": status,
                "updated_at": _now(),
            },
        )

    def run(self) -> OrchestratorResult:
        started = _now()
        start = time.time()
        steps = self.build_steps()

        self.emit(
            "PIPELINE_STARTED", "master_orchestrator", "RUNNING", {"mode": self.mode}
        )
        self.save_state("RUNNING")

        final_status = "SUCCESS"

        for step in steps:
            result = self.run_step(step)

            if result.status == "FAILED" and result.required:
                final_status = "FAILED"
                break

            if result.status == "WARNING" and final_status == "SUCCESS":
                final_status = "WARNING"

        score = self.delivery_score()
        failed_steps = [s for s in steps if s.status == "FAILED"]
        warning_steps = [s for s in steps if s.status == "WARNING"]

        rework_required = bool(failed_steps or warning_steps)
        human_intervention_required = bool(failed_steps)

        if final_status == "SUCCESS":
            delivery_gate = read_json(
                self.package_dir / "08_delivery_gate" / "final_delivery_status.json"
            )
            release_allowed = delivery_gate.get("release_allowed", False)
            if not release_allowed:
                final_status = "BLOCKED"
                rework_required = True
                human_intervention_required = True

        finished = _now()
        duration = round(time.time() - start, 2)

        result = OrchestratorResult(
            package_dir=str(self.package_dir),
            mode=self.mode,
            started_at=started,
            finished_at=finished,
            status=final_status,
            duration_seconds=duration,
            steps=steps,
            delivery_score=score,
            rework_required=rework_required,
            human_intervention_required=human_intervention_required,
            outputs={
                "pipeline_execution_json": str(self.execution_path),
                "execution_history_jsonl": str(self.history_path),
                "orchestrator_state_json": str(self.state_path),
                "factory_learning_events_jsonl": str(self.learning_events_path),
            },
            next_step=(
                "Customer handover"
                if final_status == "SUCCESS"
                else "Resolve failed/warning components and re-run orchestrator"
            ),
        )

        write_json(self.execution_path, asdict(result))
        self.save_state(final_status)

        self.emit(
            "PIPELINE_COMPLETED",
            "master_orchestrator",
            final_status,
            {
                "duration_seconds": duration,
                "delivery_score": score,
                "rework_required": rework_required,
                "human_intervention_required": human_intervention_required,
            },
        )

        return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def run_cli(package_dir: str, mode: str):
    orchestrator = MasterOrchestrator(package_dir=package_dir, mode=mode)
    result = orchestrator.run()

    print("\nMaster Orchestrator complete")
    print(f"Mode:     {result.mode}")
    print(f"Status:   {result.status}")
    print(f"Duration: {result.duration_seconds}s")
    print(f"Score:    {int(round(result.delivery_score * 100))}%")
    print(f"Rework:   {result.rework_required}")
    print(f"Human:    {result.human_intervention_required}")

    print("\nSteps:")
    for step in result.steps:
        print(f"  - {step.name}: {step.status} ({step.duration_seconds}s)")

    print("\nOutput:")
    for k, v in result.outputs.items():
        print(f"  {k}: {v}")

    print(f"\nNext: {result.next_step}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic Zero - Master Orchestrator")
    parser.add_argument(
        "--package-dir", required=True, help="Path to customer essential_package folder"
    )
    parser.add_argument(
        "--mode",
        default="FULL_BUILD",
        choices=[
            "FULL_BUILD",
            "REBUILD_FROM_SIOP",
            "REBUILD_FROM_BLUEPRINT",
            "DELIVERY_ONLY",
            "DRY_RUN",
        ],
    )
    args = parser.parse_args()
    run_cli(args.package_dir, args.mode)
