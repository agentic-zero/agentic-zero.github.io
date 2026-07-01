# security/security_dashboard.py

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from security.entitlement_guard import EntitlementGuard
from security.license_manager import LicenseManager


SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


@dataclass
class AuditSummary:
    total_events: int
    by_severity: dict[str, int]
    last_event_at: Optional[str]
    recent_critical: list[dict[str, Any]]


@dataclass
class ClientSummary:
    client_id: str
    license_status: str
    license_valid: bool
    license_plan: Optional[str]
    license_product: Optional[str]
    license_expires_at: Optional[str]
    entitlement_status: str
    execution_allowed: bool
    connectors_enabled: Optional[bool]
    swarm_enabled: Optional[bool]
    audit: dict[str, Any]


@dataclass
class FleetSummary:
    generated_at: str
    total_clients: int
    by_entitlement_status: dict[str, int]
    clients_with_invalid_license: list[str]
    clients_with_recent_critical_events: list[str]
    clients: list[dict[str, Any]]


class SecurityDashboard:
    """
    Read-only reporting layer over the security/ state already produced
    by every other module in this folder. Never mutates anything - this
    is a view, not a control surface. Re-derives license/entitlement
    status through LicenseManager.validate() / EntitlementGuard.check()
    rather than reading raw JSON files directly, so the dashboard reports
    the same fail-closed truth the rest of the system actually enforces
    (a corrupted license file shows up here as MISSING, exactly as
    SecurityGateway would treat it - not as whatever garbage happens to
    be in the file).
    """

    def __init__(
        self,
        security_root: str | Path = "security/state",
        license_manager: Optional[LicenseManager] = None,
        entitlement_guard: Optional[EntitlementGuard] = None,
    ) -> None:
        self.security_root = Path(security_root)
        self.license_manager = license_manager or LicenseManager(
            license_root=self.security_root / "licenses"
        )
        self.entitlement_guard = entitlement_guard or EntitlementGuard(
            entitlement_root=self.security_root / "entitlements"
        )
        self.audit_root = self.security_root / "audit_logs"

    def list_clients(self) -> list[str]:
        """A client is anything with a license, an entitlement, or an
        audit log - union, not intersection, since a client mid-offboarding
        might have a revoked license but still-present audit history.
        """
        client_ids: set[str] = set()

        licenses_dir = self.security_root / "licenses"
        entitlements_dir = self.security_root / "entitlements"

        for d in (licenses_dir, entitlements_dir):
            if d.exists():
                client_ids.update(p.stem for p in d.glob("*.json"))

        if self.audit_root.exists():
            client_ids.update(p.stem for p in self.audit_root.glob("*.jsonl"))

        return sorted(client_ids)

    def audit_summary(self, client_id: str, recent_limit: int = 5) -> AuditSummary:
        events = read_jsonl(self.audit_root / f"{client_id}.jsonl")

        by_severity = {s: 0 for s in SEVERITIES}
        for event in events:
            severity = event.get("severity", "INFO")
            if severity in by_severity:
                by_severity[severity] += 1

        critical_events = [e for e in events if e.get("severity") == "CRITICAL"]

        return AuditSummary(
            total_events=len(events),
            by_severity=by_severity,
            last_event_at=events[-1].get("timestamp_utc") if events else None,
            recent_critical=critical_events[-recent_limit:],
        )

    def client_summary(self, client_id: str) -> ClientSummary:
        license_validation = self.license_manager.validate(client_id)
        entitlement_decision = self.entitlement_guard.check(client_id)
        audit = self.audit_summary(client_id)

        license_record = self.license_manager.load_license(client_id)

        return ClientSummary(
            client_id=client_id,
            license_status=license_validation.status,
            license_valid=license_validation.valid,
            license_plan=license_record.plan if license_record else None,
            license_product=license_record.product if license_record else None,
            license_expires_at=license_record.expires_at if license_record else None,
            entitlement_status=entitlement_decision.status.value,
            execution_allowed=entitlement_decision.execution_allowed,
            connectors_enabled=self.entitlement_guard._load_entitlement(client_id).get("connectors_enabled"),
            swarm_enabled=self.entitlement_guard._load_entitlement(client_id).get("swarm_enabled"),
            audit=asdict(audit),
        )

    def fleet_summary(self, recent_critical_window: int = 5) -> FleetSummary:
        client_ids = self.list_clients()
        summaries = [self.client_summary(cid) for cid in client_ids]

        by_status: dict[str, int] = {}
        invalid_license = []
        recent_critical = []

        for s in summaries:
            by_status[s.entitlement_status] = by_status.get(s.entitlement_status, 0) + 1
            if not s.license_valid:
                invalid_license.append(s.client_id)
            if s.audit["by_severity"].get("CRITICAL", 0) > 0:
                recent_critical.append(s.client_id)

        return FleetSummary(
            generated_at=now(),
            total_clients=len(summaries),
            by_entitlement_status=by_status,
            clients_with_invalid_license=invalid_license,
            clients_with_recent_critical_events=recent_critical,
            clients=[asdict(s) for s in summaries],
        )


def print_client_report(summary: ClientSummary) -> None:
    print(f"\nClient: {summary.client_id}")
    print("-" * (8 + len(summary.client_id)))
    print(f"  License:      {summary.license_status:12s} valid={summary.license_valid}  plan={summary.license_plan}  product={summary.license_product}")
    print(f"  Entitlement:  {summary.entitlement_status:12s} execution_allowed={summary.execution_allowed}  connectors={summary.connectors_enabled}  swarm={summary.swarm_enabled}")
    audit = summary.audit
    print(f"  Audit:        {audit['total_events']} events  (CRITICAL={audit['by_severity'].get('CRITICAL',0)}  ERROR={audit['by_severity'].get('ERROR',0)}  WARNING={audit['by_severity'].get('WARNING',0)}  INFO={audit['by_severity'].get('INFO',0)})"
    )
    if audit["recent_critical"]:
        print("  Recent CRITICAL events:")
        for e in audit["recent_critical"]:
            print(f"    [{e.get('timestamp_utc','')[:19]}] {e.get('event_type')}: {e.get('reason')}")


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Security Dashboard")
    parser.add_argument("--client-id", default="", help="Report for one client only")
    parser.add_argument("--fleet", action="store_true", help="Report aggregated across all clients")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", default="", help="Optional path to also write the JSON report")
    args = parser.parse_args()

    dashboard = SecurityDashboard()

    if args.client_id:
        summary = dashboard.client_summary(args.client_id)
        if args.format == "json":
            print(json.dumps(asdict(summary), indent=2, ensure_ascii=False))
        else:
            print_client_report(summary)
        if args.output:
            write_json(Path(args.output), asdict(summary))
        return

    fleet = dashboard.fleet_summary()

    if args.format == "json":
        print(json.dumps(asdict(fleet), indent=2, ensure_ascii=False))
    else:
        print("\n" + "=" * 60)
        print("AGENTIC ZERO - SECURITY DASHBOARD (fleet view)")
        print("=" * 60)
        print(f"Generated at:  {fleet.generated_at}")
        print(f"Total clients: {fleet.total_clients}")
        print("\nBy entitlement status:")
        for status, count in fleet.by_entitlement_status.items():
            print(f"  {status:15s} {count}")
        if fleet.clients_with_invalid_license:
            print(f"\nClients with INVALID license ({len(fleet.clients_with_invalid_license)}):")
            for cid in fleet.clients_with_invalid_license:
                print(f"  - {cid}")
        if fleet.clients_with_recent_critical_events:
            print(f"\nClients with CRITICAL audit events ({len(fleet.clients_with_recent_critical_events)}):")
            for cid in fleet.clients_with_recent_critical_events:
                print(f"  - {cid}")
        print("\nUse --client-id <id> for a detailed per-client report.")

    if args.output:
        write_json(Path(args.output), asdict(fleet))


if __name__ == "__main__":
    run_cli()
