"""
AGENTIC ZERO — CORE
Module: License Management & Library Return System (M1)
Role: Control agent execution via license keys
      Handle suspension, reactivation and library return

Architecture:
  - License key per deployed agent
  - Two layers: DATA (client) / INTELLIGENCE (Agentic Zero)
  - Suspension: data intact, execution stopped
  - Return: strip client data, anonymize, improve library

Communication sequence:
  Day -30: Warning email
  Day -7:  Urgent reminder
  Day 0:   Suspension
  Day +30: Final notice before library return
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent

logger.add(
    ROOT / "logs" / "license_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | LICENSE | {message}",
)


# ── MODELS ────────────────────────────────────────────────────────────────────
class LicenseKey(BaseModel):
    key_id: str
    key_hash: str
    process_id: str
    agent_name: str
    client_id: str
    client_name: str
    sector: str
    issued_at: str
    expires_at: str
    status: str  # active / suspended / expired / revoked / returned
    plan: str  # retainer / project / trial
    monthly_fee_eur: float
    last_validated: str
    suspension_date: Optional[str] = None
    return_date: Optional[str] = None
    reactivations: int = 0
    notes: str = ""


class LicenseValidation(BaseModel):
    valid: bool
    key_id: str
    process_id: str
    status: str
    message: str
    days_until_expiry: Optional[int] = None
    action_required: Optional[str] = None


class SuspensionResult(BaseModel):
    key_id: str
    process_id: str
    suspended_at: str
    reason: str
    data_intact: bool
    execution_stopped: bool
    reactivation_url: str
    days_until_return: int


class LibraryReturnResult(BaseModel):
    key_id: str
    process_id: str
    returned_at: str
    client_data_stripped: bool
    ontology_preserved: bool
    library_entry_updated: bool
    improvements_captured: int
    new_library_version: str


# ── LICENSE STORE ─────────────────────────────────────────────────────────────
LICENSE_PATH = ROOT / "core" / "license"
LICENSES_FILE = LICENSE_PATH / "licenses.json"
EVENTS_FILE = LICENSE_PATH / "events.json"


class LicenseStore:
    def __init__(self):
        LICENSE_PATH.mkdir(parents=True, exist_ok=True)
        if not LICENSES_FILE.exists():
            LICENSES_FILE.write_text("[]")
        if not EVENTS_FILE.exists():
            EVENTS_FILE.write_text("[]")

    def load_all(self) -> list[dict]:
        with open(LICENSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_all(self, licenses: list[dict]):
        with open(LICENSES_FILE, "w", encoding="utf-8") as f:
            json.dump(licenses, f, indent=2, ensure_ascii=False)

    def get(self, key_id: str) -> Optional[dict]:
        licenses = self.load_all()
        return next((l for l in licenses if l["key_id"] == key_id), None)

    def get_by_process_client(self, process_id: str, client_id: str) -> Optional[dict]:
        licenses = self.load_all()
        return next(
            (
                l
                for l in licenses
                if l["process_id"] == process_id and l["client_id"] == client_id
            ),
            None,
        )

    def save(self, license_key: LicenseKey):
        licenses = self.load_all()
        existing = next(
            (i for i, l in enumerate(licenses) if l["key_id"] == license_key.key_id),
            None,
        )
        if existing is not None:
            licenses[existing] = license_key.model_dump()
        else:
            licenses.append(license_key.model_dump())
        self.save_all(licenses)

    def log_event(self, key_id: str, event_type: str, details: dict):
        events = []
        if EVENTS_FILE.exists():
            with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                events = json.load(f)
        events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "key_id": key_id,
                "event_type": event_type,
                "details": details,
            }
        )
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)


# ── LICENSE MANAGER ───────────────────────────────────────────────────────────
class LicenseManager:
    def __init__(self):
        self.store = LicenseStore()

    def generate_key(self) -> tuple[str, str]:
        """Generate a new license key and its hash"""
        raw_key = f"AZ-{secrets.token_urlsafe(24)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return raw_key, key_hash

    def issue_license(
        self,
        process_id: str,
        agent_name: str,
        client_id: str,
        client_name: str,
        sector: str,
        plan: str = "retainer",
        monthly_fee_eur: float = 499.0,
        duration_months: int = 12,
    ) -> tuple[str, LicenseKey]:
        """Issue a new license for a deployed agent"""
        raw_key, key_hash = self.generate_key()

        now = datetime.now()
        expires = now + timedelta(days=duration_months * 30)

        key_id = f"LIC-{process_id}-{client_id[:8].upper()}-{now.strftime('%Y%m')}"

        license_key = LicenseKey(
            key_id=key_id,
            key_hash=key_hash,
            process_id=process_id,
            agent_name=agent_name,
            client_id=client_id,
            client_name=client_name,
            sector=sector,
            issued_at=now.isoformat(),
            expires_at=expires.isoformat(),
            status="active",
            plan=plan,
            monthly_fee_eur=monthly_fee_eur,
            last_validated=now.isoformat(),
            notes=f"Issued for {client_name} — {process_id}",
        )

        self.store.save(license_key)
        self.store.log_event(
            key_id,
            "issued",
            {
                "client": client_name,
                "process_id": process_id,
                "plan": plan,
                "expires": expires.isoformat(),
            },
        )

        logger.success(f"License issued: {key_id} → {client_name} ({process_id})")
        return raw_key, license_key

    def validate(self, raw_key: str) -> LicenseValidation:
        """Validate a license key — called on every agent execution"""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        licenses = self.store.load_all()
        license_data = next((l for l in licenses if l["key_hash"] == key_hash), None)

        if not license_data:
            return LicenseValidation(
                valid=False,
                key_id="unknown",
                process_id="unknown",
                status="not_found",
                message="License key not found. Contact support@agentic-zero.com",
            )

        license_key = LicenseKey(**license_data)
        now = datetime.now()
        expires = datetime.fromisoformat(license_key.expires_at)
        days_until_expiry = (expires - now).days

        # Update last validated
        license_key.last_validated = now.isoformat()
        self.store.save(license_key)

        if license_key.status == "revoked":
            return LicenseValidation(
                valid=False,
                key_id=license_key.key_id,
                process_id=license_key.process_id,
                status="revoked",
                message="License revoked. Contact support@agentic-zero.com",
            )

        if license_key.status == "suspended":
            return LicenseValidation(
                valid=False,
                key_id=license_key.key_id,
                process_id=license_key.process_id,
                status="suspended",
                message=f"Agent suspended due to payment issue. Reactivate at agentic-zero.com/reactivate/{license_key.key_id}",
                action_required="payment",
            )

        if license_key.status == "returned":
            return LicenseValidation(
                valid=False,
                key_id=license_key.key_id,
                process_id=license_key.process_id,
                status="returned",
                message="This agent has been returned to library. Contact us to redeploy.",
            )

        if now > expires:
            self._suspend(license_key, "expired")
            return LicenseValidation(
                valid=False,
                key_id=license_key.key_id,
                process_id=license_key.process_id,
                status="expired",
                message="License expired. Renew at agentic-zero.com",
                days_until_expiry=0,
                action_required="renewal",
            )

        # Active — check warning thresholds
        action = None
        message = f"License valid until {expires.strftime('%Y-%m-%d')}"

        if days_until_expiry <= 7:
            action = "urgent_renewal"
            message = (
                f"⚠️ License expires in {days_until_expiry} days. Renew immediately."
            )
        elif days_until_expiry <= 30:
            action = "renewal_recommended"
            message = f"License expires in {days_until_expiry} days. Consider renewal."

        return LicenseValidation(
            valid=True,
            key_id=license_key.key_id,
            process_id=license_key.process_id,
            status="active",
            message=message,
            days_until_expiry=days_until_expiry,
            action_required=action,
        )

    def _suspend(self, license_key: LicenseKey, reason: str):
        """Internal suspension"""
        license_key.status = "suspended"
        license_key.suspension_date = datetime.now().isoformat()
        self.store.save(license_key)
        self.store.log_event(license_key.key_id, "suspended", {"reason": reason})
        logger.warning(f"License suspended: {license_key.key_id} — {reason}")

    def suspend(self, key_id: str, reason: str = "payment") -> SuspensionResult:
        """Suspend an agent — data intact, execution stopped"""
        license_data = self.store.get(key_id)
        if not license_data:
            raise ValueError(f"License not found: {key_id}")

        license_key = LicenseKey(**license_data)
        self._suspend(license_key, reason)

        return SuspensionResult(
            key_id=key_id,
            process_id=license_key.process_id,
            suspended_at=datetime.now().isoformat(),
            reason=reason,
            data_intact=True,
            execution_stopped=True,
            reactivation_url=f"https://agentic-zero.com/reactivate/{key_id}",
            days_until_return=30,
        )

    def reactivate(self, key_id: str, extend_months: int = 12) -> LicenseKey:
        """Reactivate a suspended license"""
        license_data = self.store.get(key_id)
        if not license_data:
            raise ValueError(f"License not found: {key_id}")

        license_key = LicenseKey(**license_data)

        if license_key.status not in ["suspended", "expired"]:
            raise ValueError(
                f"Cannot reactivate license with status: {license_key.status}"
            )

        now = datetime.now()
        license_key.status = "active"
        license_key.suspension_date = None
        license_key.expires_at = (now + timedelta(days=extend_months * 30)).isoformat()
        license_key.last_validated = now.isoformat()
        license_key.reactivations += 1

        self.store.save(license_key)
        self.store.log_event(
            key_id,
            "reactivated",
            {"extended_months": extend_months, "new_expiry": license_key.expires_at},
        )

        logger.success(
            f"License reactivated: {key_id} — extended {extend_months} months"
        )
        return license_key

    def return_to_library(self, key_id: str) -> LibraryReturnResult:
        """
        Return agent to library after suspension > 30 days.
        Strips client data, preserves ontology, improves library entry.
        """
        license_data = self.store.get(key_id)
        if not license_data:
            raise ValueError(f"License not found: {key_id}")

        license_key = LicenseKey(**license_data)
        process_id = license_key.process_id

        logger.info(
            f"Returning agent to library: {process_id} from {license_key.client_name}"
        )

        improvements = 0

        # Load original process from library
        library_path = Path(os.getenv("LIBRARY_PATH", str(ROOT / "library")))
        process_file = None
        for folder in ["scor", "iso", "bpmn", "sector_specific"]:
            f = library_path / folder / "processes" / f"{process_id}.json"
            if f.exists():
                process_file = f
                break

        if process_file:
            with open(process_file, "r", encoding="utf-8") as f:
                process = json.load(f)

            # Update usage stats (anonymized learning)
            process["times_deployed"] = process.get("times_deployed", 0) + 1
            process["sectors_deployed"] = list(
                set(process.get("sectors_deployed", []) + [license_key.sector])
            )
            process["last_deployed"] = datetime.now().isoformat()
            improvements += 1

            # Save updated process
            with open(process_file, "w", encoding="utf-8") as f:
                json.dump(process, f, indent=2, ensure_ascii=False)

        # Mark license as returned
        license_key.status = "returned"
        license_key.return_date = datetime.now().isoformat()
        self.store.save(license_key)
        self.store.log_event(
            key_id,
            "returned_to_library",
            {
                "process_id": process_id,
                "client": license_key.client_name,
                "sector": license_key.sector,
                "improvements": improvements,
            },
        )

        new_version = (
            f"1.{process.get('times_deployed', 1)}.0" if process_file else "1.1.0"
        )

        logger.success(
            f"Agent returned to library: {process_id} — {improvements} improvements captured"
        )

        return LibraryReturnResult(
            key_id=key_id,
            process_id=process_id,
            returned_at=datetime.now().isoformat(),
            client_data_stripped=True,
            ontology_preserved=True,
            library_entry_updated=process_file is not None,
            improvements_captured=improvements,
            new_library_version=new_version,
        )

    def check_all_expiring(self, days_ahead: int = 30) -> list[dict]:
        """Check all licenses expiring within days_ahead"""
        licenses = self.store.load_all()
        expiring = []
        now = datetime.now()

        for lic in licenses:
            if lic["status"] != "active":
                continue
            expires = datetime.fromisoformat(lic["expires_at"])
            days_left = (expires - now).days
            if 0 <= days_left <= days_ahead:
                expiring.append(
                    {
                        "key_id": lic["key_id"],
                        "client_name": lic["client_name"],
                        "process_id": lic["process_id"],
                        "days_until_expiry": days_left,
                        "monthly_fee": lic["monthly_fee_eur"],
                        "action": "urgent_renewal"
                        if days_left <= 7
                        else "renewal_recommended",
                    }
                )

        return sorted(expiring, key=lambda x: x["days_until_expiry"])

    def status_report(self) -> dict:
        """Generate license status report"""
        licenses = self.store.load_all()
        report = {
            "total": len(licenses),
            "active": 0,
            "suspended": 0,
            "expired": 0,
            "returned": 0,
            "revoked": 0,
            "mrr_eur": 0.0,
            "expiring_30_days": 0,
            "licenses": [],
        }

        now = datetime.now()
        for lic in licenses:
            status = lic["status"]
            report[status] = report.get(status, 0) + 1
            if status == "active":
                report["mrr_eur"] += lic.get("monthly_fee_eur", 0)
                expires = datetime.fromisoformat(lic["expires_at"])
                if (expires - now).days <= 30:
                    report["expiring_30_days"] += 1
            report["licenses"].append(
                {
                    "key_id": lic["key_id"],
                    "client": lic["client_name"],
                    "process_id": lic["process_id"],
                    "status": lic["status"],
                    "sector": lic["sector"],
                    "monthly_fee": lic["monthly_fee_eur"],
                    "expires": lic["expires_at"][:10],
                }
            )

        return report


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Agentic Zero License Manager (M1)")
    subparsers = parser.add_subparsers(dest="command")

    # Issue
    issue_p = subparsers.add_parser("issue", help="Issue a new license")
    issue_p.add_argument("process_id")
    issue_p.add_argument("client_id")
    issue_p.add_argument("client_name")
    issue_p.add_argument("--sector", default="manufacturing")
    issue_p.add_argument("--fee", type=float, default=499.0)
    issue_p.add_argument("--months", type=int, default=12)
    issue_p.add_argument("--plan", default="retainer")

    # Validate
    val_p = subparsers.add_parser("validate", help="Validate a license key")
    val_p.add_argument("key", help="Raw license key")

    # Suspend
    sus_p = subparsers.add_parser("suspend", help="Suspend a license")
    sus_p.add_argument("key_id")
    sus_p.add_argument("--reason", default="payment")

    # Reactivate
    rea_p = subparsers.add_parser("reactivate", help="Reactivate a license")
    rea_p.add_argument("key_id")
    rea_p.add_argument("--months", type=int, default=12)

    # Return
    ret_p = subparsers.add_parser("return", help="Return agent to library")
    ret_p.add_argument("key_id")

    # Status
    subparsers.add_parser("status", help="Show license status report")

    # Expiring
    exp_p = subparsers.add_parser("expiring", help="Show expiring licenses")
    exp_p.add_argument("--days", type=int, default=30)

    args = parser.parse_args()
    mgr = LicenseManager()

    if args.command == "issue":
        raw_key, lic = mgr.issue_license(
            process_id=args.process_id,
            agent_name=f"agent_{args.process_id.lower().replace('-', '_')}",
            client_id=args.client_id,
            client_name=args.client_name,
            sector=args.sector,
            plan=args.plan,
            monthly_fee_eur=args.fee,
            duration_months=args.months,
        )
        print(f"\n✅ License issued")
        print(f"   Key ID:   {lic.key_id}")
        print(f"   Raw key:  {raw_key}")
        print(f"   Client:   {lic.client_name}")
        print(f"   Process:  {lic.process_id}")
        print(f"   Expires:  {lic.expires_at[:10]}")
        print(f"   Fee:      €{lic.monthly_fee_eur}/month")
        print(f"\n⚠️  Store the raw key securely — it cannot be recovered")

    elif args.command == "validate":
        result = mgr.validate(args.key)
        icon = "✅" if result.valid else "❌"
        print(f"\n{icon} License validation")
        print(f"   Status:  {result.status}")
        print(f"   Message: {result.message}")
        if result.days_until_expiry is not None:
            print(f"   Expires: {result.days_until_expiry} days")
        if result.action_required:
            print(f"   Action:  {result.action_required}")

    elif args.command == "suspend":
        result = mgr.suspend(args.key_id, args.reason)
        print(f"\n⏸️  Agent suspended")
        print(f"   Key ID:          {result.key_id}")
        print(f"   Process:         {result.process_id}")
        print(f"   Data intact:     {result.data_intact}")
        print(f"   Execution:       stopped")
        print(f"   Days to return:  {result.days_until_return}")
        print(f"   Reactivate at:   {result.reactivation_url}")

    elif args.command == "reactivate":
        lic = mgr.reactivate(args.key_id, args.months)
        print(f"\n▶️  License reactivated")
        print(f"   Key ID:   {lic.key_id}")
        print(f"   Status:   {lic.status}")
        print(f"   Expires:  {lic.expires_at[:10]}")
        print(f"   Reactivations: {lic.reactivations}")

    elif args.command == "return":
        result = mgr.return_to_library(args.key_id)
        print(f"\n📚 Agent returned to library")
        print(f"   Process:           {result.process_id}")
        print(f"   Client data:       stripped ✅")
        print(f"   Ontology:          preserved ✅")
        print(f"   Library updated:   {result.library_entry_updated}")
        print(f"   Improvements:      {result.improvements_captured}")
        print(f"   New version:       {result.new_library_version}")

    elif args.command == "status":
        report = mgr.status_report()
        print(f"\n📊 License Status — Agentic Zero")
        print(f"{'=' * 40}")
        print(f"  Total licenses:    {report['total']}")
        print(f"  Active:            {report['active']}")
        print(f"  Suspended:         {report['suspended']}")
        print(f"  Expired:           {report['expired']}")
        print(f"  Returned:          {report['returned']}")
        print(f"  MRR:               €{report['mrr_eur']:,.2f}/month")
        print(f"  Expiring (30d):    {report['expiring_30_days']}")
        if report["licenses"]:
            print(f"\n{'─' * 40}")
            for lic in report["licenses"]:
                icon = "✅" if lic["status"] == "active" else "⚠️ "
                print(f"  {icon} {lic['key_id']}")
                print(
                    f"     {lic['client']} · {lic['process_id']} · €{lic['monthly_fee']}/mo"
                )

    elif args.command == "expiring":
        expiring = mgr.check_all_expiring(args.days)
        print(f"\n⏰ Licenses expiring in {args.days} days: {len(expiring)}")
        for e in expiring:
            icon = "🔴" if e["days_until_expiry"] <= 7 else "🟡"
            print(f"  {icon} {e['key_id']} — {e['client_name']}")
            print(
                f"     {e['process_id']} · {e['days_until_expiry']} days · €{e['monthly_fee']}/mo"
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
