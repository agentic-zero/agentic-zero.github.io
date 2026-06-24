"""
AGENTIC ZERO - THE MACHINE
Observer v2.0

Role:
  Observe runtime events from swarms, agents, Shield, Pulse and Factory.
  Convert raw events into normalized episodes for The Machine.

  v2 adds REAL client telemetry grounding (Phase 2.5): when --client-root
  is provided, the observer loads each organism's siop_internal.json
  (learning_hooks + autonomy_design) and uses it to decide requires_human,
  pattern_candidate and kpi-deviation matches against that organism's own
  declared contract - instead of guessing from generic keyword matches in
  the raw event JSON. Without --client-root, v1 keyword-based behavior is
  preserved unchanged (Phase 1 smoke test stays green).

Input:
  runtime event streams:
    swarm_events.jsonl
    audit_events.jsonl
    learning_events.jsonl
    shield_events.jsonl
    routed_events.jsonl
    heartbeat_events.jsonl
    pulse_events.jsonl
  10_swarm/organisms/<SLUG>/siop_internal.json   (optional, --client-root)

Output:
  memory/episodic/episodic_memory.jsonl
  memory/semantic/observed_patterns.json
  the_machine/state/machine_state.json
"""

from __future__ import annotations

import argparse
import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def append_jsonl(path: Path, payload: dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def stable_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class OrganismRegistry:
    """Loads 10_swarm/organisms/<SLUG>/siop_internal.json for every organism
    of a client package and indexes them by agent_type AND by slug.
    """

    def __init__(self, client_root: str | Path | None):
        self.profiles_by_agent_type: dict[str, dict[str, Any]] = {}
        self.profiles_by_slug: dict[str, dict[str, Any]] = {}

        if not client_root:
            return

        organisms_dir = Path(client_root) / "10_swarm" / "organisms"
        if not organisms_dir.exists():
            return

        for organism_dir in sorted(organisms_dir.iterdir()):
            profile_file = organism_dir / "siop_internal.json"
            if not profile_file.exists():
                continue
            profile = read_json(profile_file, {})
            if not profile:
                continue

            slug = organism_dir.name
            agent_type = profile.get("agent_type", "")

            profile_lite = {
                "slug": slug,
                "agent_type": agent_type,
                "process_name": profile.get("process_name", slug),
                "observation_points": set(
                    profile.get("learning_hooks", {}).get("observation_points", [])
                ),
                "failure_patterns": profile.get("learning_hooks", {}).get(
                    "failure_patterns", []
                ),
                "kpi_deviation_signals": profile.get("learning_hooks", {}).get(
                    "kpi_deviation_signals", []
                ),
                "approval_required": [
                    a.lower()
                    for a in profile.get("autonomy_design", {}).get(
                        "approval_required", []
                    )
                ],
                "always_human": [
                    a.lower()
                    for a in profile.get("autonomy_design", {}).get(
                        "always_human", []
                    )
                ],
            }

            self.profiles_by_slug[slug] = profile_lite
            if agent_type:
                self.profiles_by_agent_type[agent_type] = profile_lite

    @property
    def loaded(self) -> bool:
        return bool(self.profiles_by_slug)

    def resolve(self, organism_hint: str, source_hint: str = "") -> dict[str, Any] | None:
        if not self.loaded:
            return None

        candidates = [organism_hint, source_hint]
        for candidate in candidates:
            if not candidate:
                continue
            slug_guess = candidate.strip().upper().replace(" ", "_").replace("-", "_")
            slug_guess = slug_guess.replace("_ORGANISM", "")
            if slug_guess in self.profiles_by_slug:
                return self.profiles_by_slug[slug_guess]
            if candidate in self.profiles_by_agent_type:
                return self.profiles_by_agent_type[candidate]
            # source like "demand_planning_agent_started"
            for agent_type, profile in self.profiles_by_agent_type.items():
                if candidate.startswith(agent_type):
                    return profile
        return None


@dataclass
class Episode:
    episode_id: str
    created_at: str
    source_stream: str
    source: str
    event_type: str
    organism: str
    process_id: str
    outcome: str
    confidence: float
    risk_score: float
    requires_human: bool
    requires_shield: bool
    learning_relevant: bool
    pattern_candidate: str
    grounded: bool
    matched_observation_point: bool
    payload: dict[str, Any]


class MachineObserver:
    def __init__(
        self,
        event_dir: str | Path,
        memory_root: str | Path = "memory",
        state_root: str | Path = "the_machine/state",
        client_root: str | Path | None = None,
    ):
        self.event_dir = Path(event_dir)
        self.memory_root = Path(memory_root)
        self.state_root = Path(state_root)
        self.registry = OrganismRegistry(client_root)

        self.episodic_file = self.memory_root / "episodic" / "episodic_memory.jsonl"
        self.patterns_file = self.memory_root / "semantic" / "observed_patterns.json"
        self.state_file = self.state_root / "machine_state.json"

        self.streams = {
            "swarm": self.event_dir / "swarm_events.jsonl",
            "audit": self.event_dir / "audit_events.jsonl",
            "learning": self.event_dir / "learning_events.jsonl",
            "shield": self.event_dir / "shield_events.jsonl",
            "routed": self.event_dir / "routed_events.jsonl",
            "heartbeat": self.event_dir / "heartbeat_events.jsonl",
            "pulse": self.event_dir / "pulse_events.jsonl",
        }

        self.state = read_json(
            self.state_file,
            {
                "status": "observing",
                "episodes_observed": 0,
                "last_observation": "",
                "sources": {},
                "patterns": {},
                "registry_loaded": self.registry.loaded,
            },
        )

    def normalize_event(self, stream: str, event: dict[str, Any]) -> Episode:
        payload = event.get("payload", {})
        event_type = (
            event.get("event_type") or event.get("event_name") or "unknown_event"
        )
        source = event.get("source", payload.get("source", "unknown"))

        organism = (
            payload.get("organism")
            or payload.get("source_organism")
            or event.get("organism")
            or source
        )

        process_id = (
            event.get("process_id")
            or payload.get("process_id")
            or payload.get("scenario_id")
            or ""
        )

        confidence = event.get(
            "confidence",
            payload.get("confidence", payload.get("confidence_score", 0.88)),
        )
        risk_score = event.get("risk_score", payload.get("risk_score", 0.20))

        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.88

        try:
            risk_score = float(risk_score)
        except Exception:
            risk_score = 0.20

        if confidence > 1:
            confidence = confidence / 100
        if risk_score > 1:
            risk_score = risk_score / 100

        raw = json.dumps(event, ensure_ascii=False).lower()

        # --- v2 GROUNDING: check organism profile if registry loaded
        profile = self.registry.resolve(organism, source) if self.registry.loaded else None
        grounded = profile is not None
        matched_observation_point = False

        if profile:
            # Check if event_type matches one of this organism's observation_points
            matched_observation_point = event_type in profile["observation_points"]

            # requires_human: check if event_type matches approval_required or always_human
            requires_human = any(
                keyword in event_type.lower() for keyword in profile["approval_required"]
            ) or any(
                keyword in event_type.lower() for keyword in profile["always_human"]
            )
        else:
            # --- v1 FALLBACK: keyword-based heuristics (Phase 1 smoke test compatibility)
            requires_human = any(
                x in raw
                for x in [
                    "human",
                    "manual",
                    "approval_required",
                    "human_override",
                    "process owner",
                ]
            )

        requires_shield = any(
            x in raw
            for x in [
                "shield",
                "blocked",
                "policy_boundary",
                "compliance",
                "financial impact",
            ]
        )

        learning_relevant = (
            stream == "learning"
            or "learning" in raw
            or "conflict" in raw
            or "stale" in raw
            or "missing_context" in raw
            or "low_confidence" in raw
        )

        outcome = "observed"
        if any(x in raw for x in ["failed", "error", "blocked", "stale", "degraded"]):
            outcome = "negative"
        elif any(x in raw for x in ["completed", "ok", "success", "normal"]):
            outcome = "positive"

        pattern_candidate = self.detect_pattern_candidate(
            event_type, raw, confidence, risk_score, profile
        )

        episode_payload = {
            "stream": stream,
            "event": event,
        }

        return Episode(
            episode_id=f"EP-{stable_hash(episode_payload)}",
            created_at=now(),
            source_stream=stream,
            source=source,
            event_type=event_type,
            organism=organism,
            process_id=process_id,
            outcome=outcome,
            confidence=round(confidence, 4),
            risk_score=round(risk_score, 4),
            requires_human=requires_human,
            requires_shield=requires_shield,
            learning_relevant=learning_relevant,
            pattern_candidate=pattern_candidate,
            grounded=grounded,
            matched_observation_point=matched_observation_point,
            payload=event,
        )

    def detect_pattern_candidate(
        self,
        event_type: str,
        raw: str,
        confidence: float,
        risk_score: float,
        profile: dict[str, Any] | None = None,
    ) -> str:
        if "missing_context" in raw:
            return "missing_context"
        if "conflict" in raw:
            return "organism_conflict"
        if "stale" in raw or "heartbeat" in raw and "degraded" in raw:
            return "stale_organism"
        if "blocked" in raw:
            return "shield_blocked_action"
        if "human_override" in raw or "manual" in raw:
            return "human_intervention"

        # v2: check profile failure_patterns if grounded
        if profile:
            event_type_lower = event_type.lower()
            for pattern in profile.get("failure_patterns", []):
                if pattern.lower() in event_type_lower:
                    return f"profile_failure:{pattern}"

        if confidence < 0.70:
            return "low_confidence"
        if risk_score > 0.70:
            return "high_risk"
        if "route_status" in raw and "no_target" in raw:
            return "unrouted_event"
        return "normal_operation"

    def already_seen(self) -> set[str]:
        seen = set()
        for episode in read_jsonl(self.episodic_file):
            if episode.get("episode_id"):
                seen.add(episode["episode_id"])
        return seen

    def observe(self) -> dict[str, Any]:
        seen = self.already_seen()
        new_episodes = []
        stream_counts = {}

        for stream, path in self.streams.items():
            events = read_jsonl(path)
            stream_counts[stream] = len(events)

            for event in events:
                episode = self.normalize_event(stream, event)
                if episode.episode_id in seen:
                    continue

                append_jsonl(self.episodic_file, asdict(episode))
                seen.add(episode.episode_id)
                new_episodes.append(episode)

        self.update_patterns(new_episodes)
        self.update_state(new_episodes, stream_counts)

        return {
            "new_episodes": len(new_episodes),
            "total_seen": len(seen),
            "streams": stream_counts,
            "grounded_episodes": sum(1 for e in new_episodes if e.grounded),
            "episodic_memory": str(self.episodic_file),
            "patterns": str(self.patterns_file),
            "state": str(self.state_file),
        }

    def update_patterns(self, episodes: list[Episode]):
        patterns = read_json(
            self.patterns_file,
            {
                "created_at": now(),
                "updated_at": "",
                "patterns": {},
                "organisms": {},
                "streams": {},
            },
        )

        for ep in episodes:
            p = ep.pattern_candidate or "unknown"
            patterns["patterns"].setdefault(
                p,
                {
                    "count": 0,
                    "last_seen": "",
                    "risk_total": 0.0,
                    "confidence_total": 0.0,
                },
            )
            patterns["patterns"][p]["count"] += 1
            patterns["patterns"][p]["last_seen"] = ep.created_at
            patterns["patterns"][p]["risk_total"] += ep.risk_score
            patterns["patterns"][p]["confidence_total"] += ep.confidence

            org = ep.organism or "unknown"
            patterns["organisms"].setdefault(org, 0)
            patterns["organisms"][org] += 1

            patterns["streams"].setdefault(ep.source_stream, 0)
            patterns["streams"][ep.source_stream] += 1

        for p, data in patterns["patterns"].items():
            count = max(data.get("count", 1), 1)
            data["avg_risk"] = round(data.get("risk_total", 0.0) / count, 4)
            data["avg_confidence"] = round(data.get("confidence_total", 0.0) / count, 4)

        patterns["updated_at"] = now()
        write_json(self.patterns_file, patterns)

    def update_state(self, episodes: list[Episode], stream_counts: dict[str, int]):
        previous_total = int(self.state.get("episodes_observed", 0))
        total = previous_total + len(episodes)

        negative = sum(1 for e in episodes if e.outcome == "negative")
        learning = sum(1 for e in episodes if e.learning_relevant)
        human = sum(1 for e in episodes if e.requires_human)
        shield = sum(1 for e in episodes if e.requires_shield)
        grounded = sum(1 for e in episodes if e.grounded)

        self.state.update(
            {
                "status": "observing",
                "last_observation": now(),
                "episodes_observed": total,
                "last_batch": {
                    "new_episodes": len(episodes),
                    "negative": negative,
                    "learning_relevant": learning,
                    "requires_human": human,
                    "requires_shield": shield,
                    "grounded_episodes": grounded,
                },
                "sources": stream_counts,
                "memory": {
                    "episodic_memory": str(self.episodic_file),
                    "observed_patterns": str(self.patterns_file),
                },
                "registry_loaded": self.registry.loaded,
                "next_step": "Run pattern_detector.py",
            }
        )

        write_json(self.state_file, self.state)


def run_cli():
    parser = argparse.ArgumentParser(description="Agentic Zero - The Machine Observer")
    parser.add_argument("--event-dir", required=True)
    parser.add_argument("--memory-root", default="memory")
    parser.add_argument("--state-root", default="the_machine/state")
    parser.add_argument("--client-root", default="", help="Path to client package root for organism profile grounding")
    args = parser.parse_args()

    observer = MachineObserver(
        event_dir=args.event_dir,
        memory_root=args.memory_root,
        state_root=args.state_root,
        client_root=args.client_root or None,
    )

    result = observer.observe()

    print("\nThe Machine Observer complete")
    print(f"New episodes:      {result['new_episodes']}")
    print(f"Total seen:        {result['total_seen']}")
    print(f"Grounded episodes: {result['grounded_episodes']}")
    print(f"Registry loaded:   {observer.registry.loaded}")

    print("\nStreams:")
    for k, v in result["streams"].items():
        print(f"  {k}: {v}")

    print("\nOutput:")
    print(f"  episodic_memory: {result['episodic_memory']}")
    print(f"  patterns:        {result['patterns']}")
    print(f"  state:           {result['state']}")


if __name__ == "__main__":
    run_cli()
