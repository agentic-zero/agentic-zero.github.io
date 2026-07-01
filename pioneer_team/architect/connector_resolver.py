# pioneer_team/architect/connector_resolver.py

"""
AGENTIC ZERO - PIONEER TEAM
Connector Resolver v1.0

Role:
  Mirrors interconnected_systems_ontology.json's pattern (a fuzzy
  keyword-matchable knowledge base, used by system_detector.py to
  decide IF a Swarm is needed) - but for a different question: GIVEN a
  system name the client mentioned (SAP, Salesforce, Excel...), WHAT is
  the right way to connect to it.

  functional_consultant.py already extracts an "erp" field and a
  "systems" list per organism into the SIOP/Level2SIOP it produces -
  but until now nothing did anything with that information. This module
  closes that gap: it resolves a system name to a real connection
  specification (protocol, auth method, known constraints) and attaches
  it to the SIOP as a new "integration_design" block, so the Builder
  doesn't have to research "how do you actually talk to SAP ECC" from
  scratch for every single client who has it.

Honesty principle (same as functional_consultant.py's
needs_human_review flag for synthesized organisms):
  Entries marked verified=true are well-documented, stable, publicly
  known facts about how these systems are integrated (REST/OData for
  SAP S/4HANA Cloud, RFC/BAPI for on-premise ECC, etc.) - not invented.
  A system NOT in the library returns the fallback entry, explicitly
  unverified, explicitly flagged for human research before any
  integration work begins. This module never silently guesses a
  protocol for a system it doesn't actually know.

Input:
  A system name string (e.g. from SIOP business_context.erp, or one
  entry in an organism's systems list).

Output:
  ConnectorSpec - attached into the SIOP under a new "integration_design"
  key by enrich_siop_with_connectors().
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


def repo_root() -> Path:
    """Same approach as system_detector.py's repo_root() - find the repo
    root by looking for the actual marker file, not by assuming a fixed
    folder name (works in sandbox testing, forks, different machines).
    """
    marker = Path("pioneer_team") / "architect" / "knowledge" / "connector_library.json"
    root = Path.cwd()
    while True:
        if (root / marker).exists():
            return root
        if root.parent == root:
            return Path.cwd()
        root = root.parent


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9áéíóúñü\s\-/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_library(path: Optional[str | Path] = None) -> dict[str, Any]:
    if path:
        library_path = Path(path)
    else:
        library_path = repo_root() / "pioneer_team" / "architect" / "knowledge" / "connector_library.json"

    if not library_path.exists():
        raise FileNotFoundError(f"Connector library not found: {library_path}")

    return json.loads(library_path.read_text(encoding="utf-8"))


@dataclass
class ConnectorSpec:
    system_name_input: str
    matched_id: str
    matched_name: str
    verified: bool
    protocol: str
    auth_method: str
    latency_class: str = ""
    rate_limit_class: str = ""
    known_constraints: list[str] = field(default_factory=list)
    recommended_pattern: str = ""


def resolve_connector(system_name: str, library: Optional[dict[str, Any]] = None) -> ConnectorSpec:
    """
    Same word-boundary matching discipline as system_detector.py's
    keyword_match_score() (fixed weeks ago to avoid short-keyword false
    positives like "eam" matching inside "empresa") - reused here
    deliberately rather than re-implementing a looser match.
    """
    if not system_name or not system_name.strip():
        lib = library or load_library()
        fb = lib["fallback"]
        return ConnectorSpec(
            system_name_input=system_name,
            matched_id="",
            matched_name="(no system specified)",
            verified=False,
            protocol=fb["protocol"],
            auth_method=fb["auth_method"],
            known_constraints=list(fb["known_constraints"]),
            recommended_pattern=fb["recommended_pattern"],
        )

    lib = library or load_library()
    text = normalize_text(system_name)

    for connector in lib.get("connectors", []):
        for kw in connector.get("keywords", []):
            kw_norm = normalize_text(kw)
            if not kw_norm:
                continue
            pattern = r"\b" + re.escape(kw_norm) + r"\b"
            if re.search(pattern, text):
                return ConnectorSpec(
                    system_name_input=system_name,
                    matched_id=connector["id"],
                    matched_name=connector["name"],
                    verified=connector.get("verified", False),
                    protocol=connector.get("protocol", ""),
                    auth_method=connector.get("auth_method", ""),
                    latency_class=connector.get("latency_class", ""),
                    rate_limit_class=connector.get("rate_limit_class", ""),
                    known_constraints=list(connector.get("known_constraints", [])),
                    recommended_pattern=connector.get("recommended_pattern", ""),
                )

    fb = lib["fallback"]
    return ConnectorSpec(
        system_name_input=system_name,
        matched_id="",
        matched_name=system_name,
        verified=False,
        protocol=fb["protocol"],
        auth_method=fb["auth_method"],
        known_constraints=list(fb["known_constraints"]),
        recommended_pattern=fb["recommended_pattern"],
    )


def enrich_siop_with_connectors(siop: dict[str, Any]) -> dict[str, Any]:
    """
    Reads business_context.erp (single system) and any per-step systems
    mentioned in process_flow (functional_consultant.py's
    build_siop_internal() schema) and attaches a resolved
    integration_design block - one entry per distinct system name found,
    never duplicated.
    """
    library = load_library()
    system_names: list[str] = []

    erp = siop.get("business_context", {}).get("erp", "")
    if erp:
        system_names.append(erp)

    for step in siop.get("process_flow", []):
        system = step.get("system", "")
        if system and system not in system_names:
            system_names.append(system)

    seen_ids: set[str] = set()
    integration_design = []
    for name in system_names:
        spec = resolve_connector(name, library)
        key = spec.matched_id or spec.system_name_input
        if key in seen_ids:
            continue
        seen_ids.add(key)
        integration_design.append(asdict(spec))

    siop["integration_design"] = integration_design
    return siop


def run_cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero - Connector Resolver")
    parser.add_argument("--system-name", required=True)
    args = parser.parse_args()

    spec = resolve_connector(args.system_name)

    print("\nConnector Resolver")
    print("------------------")
    print(f"Input:               {spec.system_name_input}")
    print(f"Matched:             {spec.matched_name} ({'verified' if spec.verified else 'UNVERIFIED - needs research'})")
    print(f"Protocol:            {spec.protocol}")
    print(f"Auth method:         {spec.auth_method}")
    print(f"Recommended pattern: {spec.recommended_pattern}")
    if spec.known_constraints:
        print("Known constraints:")
        for c in spec.known_constraints:
            print(f"  - {c}")


if __name__ == "__main__":
    run_cli()
