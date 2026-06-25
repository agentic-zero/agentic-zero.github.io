"""
AGENTIC ZERO - SWARM
Swarm Splitter v1.0

Role:
  The validation gate between the Architect's decomposition (which already
  exists in pioneer_team/architect/ - siop_decomposer.py, enterprise_architect.py)
  and the real swarm materialization (swarm_generator.py).

  This module does NOT decide business splits - it does not decide that
  "Demand Planning" and "Supply Planning" should be separate organisms,
  that decision already happened upstream and is encoded in the
  swarm_coordination_<process>.json the Architect produces (today found in
  00_enterprise_intent/). What this module does is VALIDATE that proposed
  topology is structurally sound before anything gets written to disk as
  real organism folders:

    - every organism name resolves to a unique, non-colliding slug
      (the same organism_to_slug() rule used by event_catalog.py,
      observer.py, policy_engine.py, compliance_engine.py - if this
      module used a different rule, the swarm would silently desync
      from every module that already depends on that convention)
    - every event_route references an organism that actually exists in
      the organisms list (no dangling "from"/"to")
    - no organism is its own upstream/downstream dependency (no
      self-loops)
    - no circular dependency chain across the whole topology (a cycle
      would mean swarm_coordinator.py could never determine a valid
      execution order)
    - every organism carries the minimum fields downstream modules
      already require: agent_type, learning_hooks.observation_points,
      autonomy_design (approval_required/always_human/autonomous_actions)
    - at least one organism exists, and not absurdly many for a single
      process (configurable ceiling - catches a decomposition that
      over-split a process into hundreds of one-purpose-each organisms)

  A topology that fails validation is REJECTED with a list of structural
  reasons - swarm_generator.py refuses to materialize a rejected split.

Input:
  00_enterprise_intent/swarm_coordination_<process>.json
  (or any swarm_coordination_*.json - this module is process-agnostic)

Output:
  <output_dir>/split_validation.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MAX_ORGANISMS = 40
REQUIRED_ORGANISM_FIELDS = ["organism", "agent_type"]


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
    """Same rule as event_catalog.py / observer.py / policy_engine.py /
    compliance_engine.py. This MUST stay byte-identical to those - it is
    the shared contract every Shield and Machine module already depends
    on. If this drifts, organisms silently stop resolving across modules.
    """
    name = re.sub(r"\s*Organism\s*$", "", organism_name.strip())
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


@dataclass
class SplitIssue:
    severity: str  # ERROR (blocks) or WARNING (allowed, flagged)
    code: str
    message: str


@dataclass
class SplitValidationResult:
    valid: bool
    organism_count: int
    organisms: list[str]
    issues: list[dict[str, Any]]
    slug_map: dict[str, str]
    validated_at: str


class SwarmSplitter:
    def __init__(self, max_organisms: int = DEFAULT_MAX_ORGANISMS):
        self.max_organisms = max_organisms

    def validate(self, coordination: dict[str, Any]) -> SplitValidationResult:
        issues: list[SplitIssue] = []
        organisms = coordination.get("organisms", [])
        event_routes = coordination.get("event_routes", [])

        if not organisms:
            issues.append(
                SplitIssue("ERROR", "NO_ORGANISMS", "Topology has zero organisms.")
            )

        if len(organisms) > self.max_organisms:
            issues.append(
                SplitIssue(
                    "WARNING",
                    "TOO_MANY_ORGANISMS",
                    f"{len(organisms)} organisms exceeds the configured ceiling of "
                    f"{self.max_organisms}. This may indicate over-splitting a "
                    f"process into organisms too granular to coordinate sensibly.",
                )
            )

        slug_map: dict[str, str] = {}
        slug_collisions: dict[str, list[str]] = {}

        for org in organisms:
            name = org.get("organism", "")
            slug = organism_to_slug(name)

            if not name:
                issues.append(
                    SplitIssue("ERROR", "MISSING_ORGANISM_NAME", "An organism entry has no 'organism' name.")
                )
                continue

            if slug in slug_map.values():
                slug_collisions.setdefault(slug, []).append(name)
            slug_map[name] = slug

            for field in REQUIRED_ORGANISM_FIELDS:
                if not org.get(field):
                    issues.append(
                        SplitIssue(
                            "ERROR",
                            "MISSING_REQUIRED_FIELD",
                            f"Organism '{name}' is missing required field '{field}'.",
                        )
                    )

            learning_hooks = org.get("learning_hooks", {})
            if not learning_hooks.get("observation_points"):
                issues.append(
                    SplitIssue(
                        "ERROR",
                        "MISSING_OBSERVATION_POINTS",
                        f"Organism '{name}' has no learning_hooks.observation_points - "
                        f"observer.py would never be able to ground episodes against it.",
                    )
                )

            autonomy = org.get("autonomy_design", {})
            if not any(
                autonomy.get(k) for k in ("autonomous_actions", "approval_required", "always_human")
            ):
                issues.append(
                    SplitIssue(
                        "WARNING",
                        "EMPTY_AUTONOMY_DESIGN",
                        f"Organism '{name}' has no autonomy_design entries at all - "
                        f"policy_engine.py will have nothing organism-specific to match "
                        f"against and will fall back to swarm-wide/global thresholds for "
                        f"every action this organism proposes.",
                    )
                )

        for slug, colliding_names in slug_collisions.items():
            issues.append(
                SplitIssue(
                    "ERROR",
                    "SLUG_COLLISION",
                    f"Slug '{slug}' is produced by multiple organism names: "
                    f"{colliding_names}. Rename one - they would overwrite the same "
                    f"10_swarm/organisms/{slug}/ folder.",
                )
            )

        known_slugs = set(slug_map.values())
        for route in event_routes:
            from_slug = organism_to_slug(route.get("from", ""))
            to_slug = organism_to_slug(route.get("to", ""))

            if from_slug not in known_slugs:
                issues.append(
                    SplitIssue(
                        "ERROR",
                        "DANGLING_ROUTE_SOURCE",
                        f"event_route references unknown source organism: "
                        f"'{route.get('from')}' (event: {route.get('event')}).",
                    )
                )
            if to_slug not in known_slugs:
                issues.append(
                    SplitIssue(
                        "ERROR",
                        "DANGLING_ROUTE_TARGET",
                        f"event_route references unknown target organism: "
                        f"'{route.get('to')}' (event: {route.get('event')}).",
                    )
                )
            if from_slug == to_slug and from_slug:
                issues.append(
                    SplitIssue(
                        "ERROR",
                        "SELF_LOOP",
                        f"Organism '{route.get('from')}' routes an event to itself "
                        f"(event: {route.get('event')}).",
                    )
                )

        cycle = self._detect_cycle(known_slugs, event_routes)
        if cycle:
            issues.append(
                SplitIssue(
                    "ERROR",
                    "CIRCULAR_DEPENDENCY",
                    f"Circular dependency detected across organisms: {' -> '.join(cycle)}. "
                    f"swarm_coordinator.py cannot determine a valid execution order.",
                )
            )

        valid = not any(i.severity == "ERROR" for i in issues)

        return SplitValidationResult(
            valid=valid,
            organism_count=len(organisms),
            organisms=[org.get("organism", "") for org in organisms],
            issues=[asdict(i) for i in issues],
            slug_map=slug_map,
            validated_at=now(),
        )

    def _detect_cycle(
        self, known_slugs: set[str], event_routes: list[dict[str, Any]]
    ) -> list[str] | None:
        graph: dict[str, set[str]] = {slug: set() for slug in known_slugs}
        for route in event_routes:
            from_slug = organism_to_slug(route.get("from", ""))
            to_slug = organism_to_slug(route.get("to", ""))
            if from_slug in graph and to_slug in graph and from_slug != to_slug:
                graph[from_slug].add(to_slug)

        visited: dict[str, int] = {}

        def dfs(node: str, path: list[str]) -> list[str] | None:
            visited[node] = 1
            for neighbor in graph.get(node, set()):
                if visited.get(neighbor) == 1:
                    return path + [node, neighbor]
                if visited.get(neighbor) != 2:
                    result = dfs(neighbor, path + [node])
                    if result:
                        return result
            visited[node] = 2
            return None

        for node in graph:
            if visited.get(node) is None:
                result = dfs(node, [])
                if result:
                    return result
        return None


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Swarm Splitter")
    parser.add_argument("--coordination-file", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-organisms", type=int, default=DEFAULT_MAX_ORGANISMS)
    args = parser.parse_args()

    coordination = read_json(Path(args.coordination_file), {})
    splitter = SwarmSplitter(max_organisms=args.max_organisms)
    result = splitter.validate(coordination)

    output_path = Path(args.output_dir) / "split_validation.json"
    write_json(output_path, asdict(result))

    print("\nSwarm Splitter complete")
    print(f"Valid:            {result.valid}")
    print(f"Organism count:   {result.organism_count}")
    errors = [i for i in result.issues if i["severity"] == "ERROR"]
    warnings = [i for i in result.issues if i["severity"] == "WARNING"]
    print(f"Errors:           {len(errors)}")
    print(f"Warnings:         {len(warnings)}")
    for issue in result.issues:
        print(f"  [{issue['severity']}] {issue['code']}: {issue['message']}")
    print(f"\nOutput: {output_path}")

    if not result.valid:
        raise SystemExit(1)


if __name__ == "__main__":
    run_cli()
