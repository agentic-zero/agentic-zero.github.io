"""
AGENTIC ZERO - SWARM
Swarm Generator v1.0

Role:
  Materializes the real 10_swarm/ filesystem structure from a topology
  that swarm_splitter.py has already validated. This module does not
  invent organism boundaries or business logic - it derives every field
  it writes directly from the swarm_coordination_<process>.json organism
  entries the Architect already produced.

  This automates exactly what was done by hand earlier this project to
  build the dis_solar fixture - same conventions, same organism_to_slug()
  rule, same business_rules template observed across every real organism
  file in the distribuciones_norte fixture.

  REFUSES to run against an unvalidated or invalid topology - generation
  requires a passing split_validation.json from swarm_splitter.py (or
  --skip-validation-check for explicit, logged override during local
  testing only).

Input:
  <coordination_file>                      (swarm_coordination_<process>.json)
  <split_validation_file>                   (from swarm_splitter.py, must be valid=true)

Output:
  <client_root>/10_swarm/coordination/swarm_coordination_<process>.json
  <client_root>/10_swarm/organisms/<SLUG>/siop_internal.json
  <client_root>/10_swarm/organisms/<SLUG>/organism_blueprint_seed.json
  <client_root>/10_swarm/generation_manifest.json
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Identical across every real organism file observed in the
# distribuciones_norte fixture - this is the project's standing template,
# not invented per organism. If the Architect ever wants organism-specific
# business rules, that belongs in the coordination file's organism entry
# (a new field) and this generator should read it from there - not here.
STANDARD_BUSINESS_RULES = [
    "Do not act on incomplete upstream context.",
    "Escalate low-confidence or conflicting recommendations.",
    "Emit audit and learning events for every decision.",
]

STANDARD_ACCEPTANCE_KPIS = [
    "Inputs are validated before action.",
    "Outputs are traceable.",
    "Low-confidence decisions are escalated.",
    "All decisions emit audit and learning events.",
]

STANDARD_ACCEPTANCE_TESTS = [
    "Organism receives upstream context.",
    "Organism produces traceable output.",
    "Organism emits audit and learning events.",
    "Low-confidence output escalates.",
]

STANDARD_BLUEPRINT_REQUIREMENTS = {
    "must_emit_swarm_events": True,
    "must_emit_audit_events": True,
    "must_emit_learning_events": True,
    "must_support_dry_run": True,
    "must_support_escalation": True,
    "must_support_shield_arbitration": True,
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


def organism_to_slug(organism_name: str) -> str:
    """MUST stay byte-identical to the rule in swarm_splitter.py,
    event_catalog.py, observer.py, policy_engine.py, compliance_engine.py.
    """
    name = re.sub(r"\s*Organism\s*$", "", organism_name.strip())
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


@dataclass
class GenerationManifest:
    generated_at: str
    coordination_siop_id: str
    organisms_generated: list[str]
    coordination_file_written: str
    skipped_validation_check: bool


class SwarmGenerator:
    def __init__(self, client_root: str | Path):
        self.client_root = Path(client_root)
        self.coordination_dir = self.client_root / "10_swarm" / "coordination"
        self.organisms_dir = self.client_root / "10_swarm" / "organisms"

    def build_process_flow(self, org: dict[str, Any]) -> list[dict[str, Any]]:
        """STEP-01 and STEP-03 are a fixed standing template - confirmed
        byte-identical (same confidence values, same rule text) across
        every organism observed in the real distribuciones_norte fixture
        (DEMAND_PLANNING, SUPPLY_PLANNING, FINANCE_RECONCILIATION,
        QUALITY_MANAGEMENT). Only STEP-02 is organism-specific, derived
        from this organism's own purpose/systems/inputs/outputs.
        """
        name = org.get("name", org.get("organism", ""))
        systems = org.get("systems", [])
        inputs = org.get("inputs", [])
        outputs = org.get("outputs", [])

        return [
            {
                "step_id": "STEP-01",
                "name": "Receive upstream context",
                "system": "Swarm Coordinator",
                "inputs": inputs,
                "outputs": ["validated context"],
                "rule": "Only validated swarm context can trigger organism execution.",
                "confidence": 0.9,
            },
            {
                "step_id": "STEP-02",
                "name": f"Execute {name}",
                "system": ", ".join(systems),
                "inputs": inputs,
                "outputs": outputs,
                "rule": org.get("purpose", ""),
                "confidence": 0.88,
            },
            {
                "step_id": "STEP-03",
                "name": "Publish organism output",
                "system": "Swarm Event Bus",
                "inputs": outputs,
                "outputs": ["swarm event", "audit event", "learning event"],
                "rule": "Every organism output must be published as a traceable swarm event.",
                "confidence": 0.92,
            },
        ]

    def build_siop_internal(self, org: dict[str, Any]) -> dict[str, Any]:
        return {
            "siop_id": org.get("siop_id", ""),
            "process_id": org.get("siop_id", ""),
            "process_name": org.get("name", org.get("organism", "")),
            "parent_process": org.get("parent_process", ""),
            "organism": org.get("organism", ""),
            "agent_type": org.get("agent_type", ""),
            "domain": org.get("domain", ""),
            "executive_summary": {
                "process_name": org.get("name", org.get("organism", "")),
                "validated_description": org.get("purpose", ""),
                "business_goal": (
                    f"Autonomously support {org.get('name', org.get('organism', ''))} "
                    f"as part of a coordinated swarm."
                ),
                "roi_baseline": "To be calculated by swarm economics engine.",
            },
            "business_context": {
                "sector": "",
                "erp": "",
                "systems": org.get("systems", []),
                "frameworks": org.get("frameworks", []),
                "parent_process": org.get("parent_process", ""),
                "domain": org.get("domain", ""),
            },
            "process_flow": self.build_process_flow(org),
            "data_requirements": {
                "inputs": org.get("inputs", []),
                "outputs": org.get("outputs", []),
                "systems": org.get("systems", []),
            },
            "business_rules": list(STANDARD_BUSINESS_RULES),
            "compliance": {
                "frameworks": org.get("frameworks", []),
                "scor_level_1_2": org.get("scor_level_1_2", []),
                "scor_level_3": org.get("scor_level_3", []),
                "bpmn_processes": org.get("bpmn_processes", []),
            },
            "autonomy_design": org.get("autonomy_design", {}),
            "acceptance_criteria": {
                "kpis": list(STANDARD_ACCEPTANCE_KPIS),
                "tests": list(STANDARD_ACCEPTANCE_TESTS),
            },
            "learning_hooks": org.get("learning_hooks", {}),
            "dependencies": {
                "upstream": org.get("upstream_dependencies", []),
                "downstream": org.get("downstream_dependencies", []),
            },
            "ready_for_swarm_blueprint": True,
        }

    def build_blueprint_seed(self, org: dict[str, Any]) -> dict[str, Any]:
        return {
            "organism_id": org.get("siop_id", ""),
            "organism_name": org.get("organism", ""),
            "agent_type": org.get("agent_type", ""),
            "domain": org.get("domain", ""),
            "purpose": org.get("purpose", ""),
            "systems": org.get("systems", []),
            "frameworks": org.get("frameworks", []),
            "inputs": org.get("inputs", []),
            "outputs": org.get("outputs", []),
            "dependencies": {
                "upstream": org.get("upstream_dependencies", []),
                "downstream": org.get("downstream_dependencies", []),
            },
            "autonomy_design": org.get("autonomy_design", {}),
            "learning_hooks": org.get("learning_hooks", {}),
            "blueprint_requirements": dict(STANDARD_BLUEPRINT_REQUIREMENTS),
            "ready_for_blueprint_generation": True,
        }

    def generate(
        self,
        *,
        coordination: dict[str, Any],
        coordination_filename: str,
    ) -> GenerationManifest:
        organisms = coordination.get("organisms", [])
        generated: list[str] = []

        for org in organisms:
            slug = organism_to_slug(org.get("organism", ""))
            if not slug:
                continue

            organism_dir = self.organisms_dir / slug
            write_json(organism_dir / "siop_internal.json", self.build_siop_internal(org))
            write_json(
                organism_dir / "organism_blueprint_seed.json",
                self.build_blueprint_seed(org),
            )
            generated.append(slug)

        coordination_path = self.coordination_dir / coordination_filename
        write_json(coordination_path, coordination)

        manifest = GenerationManifest(
            generated_at=now(),
            coordination_siop_id=coordination.get("coordination_siop_id", ""),
            organisms_generated=generated,
            coordination_file_written=str(coordination_path),
            skipped_validation_check=False,
        )

        write_json(self.client_root / "10_swarm" / "generation_manifest.json", asdict(manifest))
        return manifest


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Swarm Generator")
    parser.add_argument("--coordination-file", required=True)
    parser.add_argument("--client-root", required=True)
    parser.add_argument("--split-validation-file", default="")
    parser.add_argument(
        "--skip-validation-check",
        action="store_true",
        help="DANGEROUS - bypasses the requirement that swarm_splitter.py already "
        "validated this topology. Only for local testing, never for a real client.",
    )
    args = parser.parse_args()

    coordination_path = Path(args.coordination_file)
    coordination = read_json(coordination_path, {})

    if not args.skip_validation_check:
        if not args.split_validation_file:
            print(
                "\nREFUSED: no --split-validation-file provided. Run swarm_splitter.py "
                "first and pass its split_validation.json here, or pass "
                "--skip-validation-check if you understand the risk (local testing only).\n"
            )
            raise SystemExit(1)

        validation = read_json(Path(args.split_validation_file), {})
        if not validation.get("valid"):
            print(
                "\nREFUSED: the referenced split_validation.json says valid=false. "
                "Fix the topology and re-run swarm_splitter.py before generating.\n"
            )
            for issue in validation.get("issues", []):
                if issue.get("severity") == "ERROR":
                    print(f"  [ERROR] {issue.get('code')}: {issue.get('message')}")
            raise SystemExit(1)

    generator = SwarmGenerator(client_root=args.client_root)
    manifest = generator.generate(
        coordination=coordination,
        coordination_filename=coordination_path.name,
    )

    if args.skip_validation_check:
        manifest.skipped_validation_check = True

    print("\nSwarm Generator complete")
    print(f"Organisms generated: {len(manifest.organisms_generated)}")
    for slug in manifest.organisms_generated:
        print(f"  - {slug}")
    print(f"\nCoordination file: {manifest.coordination_file_written}")
    print(f"Manifest: {Path(args.client_root) / '10_swarm' / 'generation_manifest.json'}")


if __name__ == "__main__":
    run_cli()
