"""
AGENTIC ZERO - RUNTIME CORE
Health Manager v1.0

Role:
  Continuous health supervision of the runtime organism population.
  Consolidates runtime_status.json (HeartbeatManager) and
  pulse_summary.json / enterprise_health.json (PulseAggregator) into a
  single supervised health verdict, with threshold-based alerting.

Input:
  runtime_status.json
  pulse_summary.json
  enterprise_health.json

Output:
  health_report.json
  health_alerts.jsonl
  state/health_manager_state.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_THRESHOLDS = {
    "critical_below": 50,
    "warning_below": 75,
    "healthy_at_or_above": 90,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


class HealthManager:
    def __init__(
        self,
        runtime_dir: str | Path,
        event_dir: str | Path | None = None,
        state_root: str | Path = "runtime_core/state",
        thresholds: dict[str, int] | None = None,
    ):
        self.runtime_dir = Path(runtime_dir)
        self.event_dir = Path(event_dir) if event_dir else self.runtime_dir / "events"
        self.state_root = Path(state_root)

        self.runtime_status_file = self.runtime_dir / "runtime_status.json"
        self.pulse_summary_file = self.event_dir / "pulse_summary.json"
        self.enterprise_health_file = self.event_dir / "enterprise_health.json"

        self.health_report_file = self.runtime_dir / "health_report.json"
        self.health_alerts_file = self.runtime_dir / "health_alerts.jsonl"
        self.state_file = self.state_root / "health_manager_state.json"

        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    def classify(self, score: float) -> str:
        if score < self.thresholds["critical_below"]:
            return "CRITICAL"
        if score < self.thresholds["warning_below"]:
            return "WARNING"
        if score >= self.thresholds["healthy_at_or_above"]:
            return "HEALTHY"
        return "NOMINAL"

    def emit_alert(self, level: str, source: str, message: str, detail: dict[str, Any]):
        append_jsonl(
            self.health_alerts_file,
            {
                "timestamp": now(),
                "level": level,
                "source": source,
                "message": message,
                "detail": detail,
            },
        )

    def supervise(self) -> dict[str, Any]:
        runtime_status = read_json(self.runtime_status_file, {})
        pulse_summary = read_json(self.pulse_summary_file, {})
        enterprise_health = read_json(self.enterprise_health_file, {})

        runtime_health = float(runtime_status.get("runtime_health", 0) or 0)
        pulse_health = float(pulse_summary.get("health", pulse_summary.get("score", 0)) or 0)
        enterprise_score = float(enterprise_health.get("health", 0) or 0)

        sources = [
            ("runtime_registry", runtime_health, bool(runtime_status)),
            ("pulse_aggregator", pulse_health, bool(pulse_summary)),
            ("enterprise_health", enterprise_score, bool(enterprise_health)),
        ]

        available = [(name, score) for name, score, present in sources if present]

        if available:
            consolidated = round(sum(score for _, score in available) / len(available), 1)
        else:
            consolidated = 0.0

        verdict = self.classify(consolidated)

        component_health = []
        for name, score in available:
            level = self.classify(score)
            component_health.append({"component": name, "score": score, "level": level})
            if level in ("CRITICAL", "WARNING"):
                self.emit_alert(
                    level=level,
                    source=name,
                    message=f"{name} health at {score} ({level})",
                    detail={"score": score, "threshold": self.thresholds},
                )

        if not available:
            self.emit_alert(
                level="WARNING",
                source="health_manager",
                message="No health sources available yet (runtime not warmed up)",
                detail={"checked": [s[0] for s in sources]},
            )

        report = {
            "timestamp": now(),
            "consolidated_health": consolidated,
            "verdict": verdict,
            "thresholds": self.thresholds,
            "components": component_health,
            "human_intervention_required": verdict in ("CRITICAL", "WARNING"),
            "sources_available": len(available),
            "sources_checked": len(sources),
        }

        write_json(self.health_report_file, report)
        write_json(
            self.state_file,
            {
                "timestamp": now(),
                "module": "health_manager",
                "status": "HEALTH_SUPERVISION_ACTIVE",
                "last_verdict": verdict,
                "last_score": consolidated,
            },
        )

        return report


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - Health Manager")
    parser.add_argument("--root-dir", required=True, help="Runtime directory")
    parser.add_argument("--event-dir", default="", help="Event directory (defaults to <root-dir>/events)")
    parser.add_argument("--state-root", default="runtime_core/state")
    parser.add_argument("--critical-below", type=int, default=DEFAULT_THRESHOLDS["critical_below"])
    parser.add_argument("--warning-below", type=int, default=DEFAULT_THRESHOLDS["warning_below"])
    parser.add_argument("--healthy-at-or-above", type=int, default=DEFAULT_THRESHOLDS["healthy_at_or_above"])
    parser.add_argument("--supervise", action="store_true", help="Run a supervision pass")
    args = parser.parse_args()

    manager = HealthManager(
        runtime_dir=args.root_dir,
        event_dir=args.event_dir or None,
        state_root=args.state_root,
        thresholds={
            "critical_below": args.critical_below,
            "warning_below": args.warning_below,
            "healthy_at_or_above": args.healthy_at_or_above,
        },
    )

    report = manager.supervise()

    print("\nAgentic Zero Health Manager complete")
    print(f"Consolidated health: {report['consolidated_health']}")
    print(f"Verdict:             {report['verdict']}")
    print(f"Human intervention:  {report['human_intervention_required']}")
    print("\nOutput:")
    print(f"  health_report: {manager.health_report_file}")
    print(f"  health_alerts: {manager.health_alerts_file}")
    print(f"  state:         {manager.state_file}")


if __name__ == "__main__":
    run_cli()
