# security/entitlement_guard.py

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class EntitlementStatus(str, Enum):
    ACTIVE = "ACTIVE"
    GRACE_PERIOD = "GRACE_PERIOD"
    READ_ONLY = "READ_ONLY"
    LOCKED = "LOCKED"
    DECOMMISSIONED = "DECOMMISSIONED"


@dataclass
class EntitlementDecision:
    client_id: str
    status: EntitlementStatus
    execution_allowed: bool
    write_allowed: bool
    read_allowed: bool
    reason: str
    plan: str
    expires_at: Optional[str]
    checked_at: str


class EntitlementGuard:
    """
    Controls whether a client can use Agentic Zero runtime.

    Protects:
    - monthly subscription access
    - runtime execution
    - autonomous agents
    - swarm execution
    - connector actions
    - dashboard/write operations
    """

    def __init__(
        self, entitlement_root: str | Path = "security/state/entitlements"
    ) -> None:
        self.entitlement_root = Path(entitlement_root)
        self.entitlement_root.mkdir(parents=True, exist_ok=True)

    def check(self, client_id: str) -> EntitlementDecision:
        entitlement = self._load_entitlement(client_id)
        now = datetime.now(timezone.utc)

        try:
            status = EntitlementStatus(entitlement.get("status", "LOCKED"))
        except ValueError:
            # Unknown/corrupted status value in the entitlement file (e.g.
            # hand-edited typo, partial write, tampering). Fail CLOSED.
            status = EntitlementStatus.LOCKED

        plan = entitlement.get("plan", "UNKNOWN")
        expires_at = entitlement.get("expires_at")

        if status == EntitlementStatus.ACTIVE:
            if expires_at and self._is_expired(expires_at, now):
                status = EntitlementStatus.GRACE_PERIOD

        if status == EntitlementStatus.ACTIVE:
            return self._decision(
                client_id,
                status,
                True,
                True,
                True,
                "Subscription active",
                plan,
                expires_at,
            )

        if status == EntitlementStatus.GRACE_PERIOD:
            return self._decision(
                client_id,
                status,
                True,
                True,
                True,
                "Subscription expired but grace period active",
                plan,
                expires_at,
            )

        if status == EntitlementStatus.READ_ONLY:
            return self._decision(
                client_id,
                status,
                False,
                False,
                True,
                "Client is in read-only mode",
                plan,
                expires_at,
            )

        if status == EntitlementStatus.LOCKED:
            return self._decision(
                client_id,
                status,
                False,
                False,
                False,
                "Client subscription locked",
                plan,
                expires_at,
            )

        if status == EntitlementStatus.DECOMMISSIONED:
            return self._decision(
                client_id,
                status,
                False,
                False,
                False,
                "Client environment decommissioned",
                plan,
                expires_at,
            )

        return self._decision(
            client_id,
            EntitlementStatus.LOCKED,
            False,
            False,
            False,
            "Unknown entitlement status",
            plan,
            expires_at,
        )

    def _load_entitlement(self, client_id: str) -> dict[str, Any]:
        file_path = self.entitlement_root / f"{client_id}.json"

        fallback = {
            "client_id": client_id,
            "status": "LOCKED",
            "plan": "UNKNOWN",
            "expires_at": None,
        }

        if not file_path.exists():
            return fallback

        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            # Corrupted or unreadable entitlement file. Fail CLOSED rather
            # than raising - this is an access-control layer, an unparseable
            # state file must never crash the caller, it must deny.
            return fallback

    def _is_expired(self, expires_at: str, now: datetime) -> bool:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return now > expiry

    def _decision(
        self,
        client_id: str,
        status: EntitlementStatus,
        execution_allowed: bool,
        write_allowed: bool,
        read_allowed: bool,
        reason: str,
        plan: str,
        expires_at: Optional[str],
    ) -> EntitlementDecision:
        return EntitlementDecision(
            client_id=client_id,
            status=status,
            execution_allowed=execution_allowed,
            write_allowed=write_allowed,
            read_allowed=read_allowed,
            reason=reason,
            plan=plan,
            expires_at=expires_at,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )

    def create_demo_entitlement(self, client_id: str = "dis_solar") -> Path:
        file_path = self.entitlement_root / f"{client_id}.json"

        data = {
            "client_id": client_id,
            "status": "ACTIVE",
            "plan": "ENTERPRISE",
            "product": "AGENTIC_ONE",
            "expires_at": "2099-12-31T23:59:59Z",
            "monthly_subscription_required": True,
            "runtime_execution_enabled": True,
            "connectors_enabled": True,
            "swarm_enabled": True,
        }

        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return file_path

    def provision(
        self,
        *,
        client_id: str,
        product: str,
        plan: str,
        expires_at: Optional[str],
        monthly_subscription_required: bool = True,
        connectors_enabled: bool = True,
        swarm_enabled: bool = True,
    ) -> Path:
        """Create a real (non-demo) entitlement record in READ_ONLY status.

        This is the correct state for a client between contract signature
        and go-live: they exist in the system, the dashboard can show build
        progress, but execution_allowed stays False because there is
        nothing real to execute yet. Use set_status() to flip to ACTIVE
        once deploy completes - that is a separate, explicit human action.
        """
        file_path = self.entitlement_root / f"{client_id}.json"

        data = {
            "client_id": client_id,
            "status": EntitlementStatus.READ_ONLY.value,
            "plan": plan,
            "product": product,
            "expires_at": expires_at,
            "monthly_subscription_required": monthly_subscription_required,
            "runtime_execution_enabled": False,
            "connectors_enabled": connectors_enabled,
            "swarm_enabled": swarm_enabled,
        }

        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return file_path

    def set_status(self, client_id: str, status: EntitlementStatus) -> Path:
        """Explicitly transition an existing entitlement to a new status
        (e.g. READ_ONLY -> ACTIVE at go-live, ACTIVE -> LOCKED on non-payment).
        Preserves plan/product/expires_at already on file. Raises if the
        client has no entitlement file yet - provision() must run first.
        """
        file_path = self.entitlement_root / f"{client_id}.json"

        if not file_path.exists():
            raise FileNotFoundError(
                f"No entitlement file found for client '{client_id}'. "
                f"Call provision() before set_status()."
            )

        data = self._load_entitlement(client_id)
        data["status"] = status.value
        if status == EntitlementStatus.ACTIVE:
            data["runtime_execution_enabled"] = True
        if status in (EntitlementStatus.LOCKED, EntitlementStatus.DECOMMISSIONED):
            # check() already denies everything unconditionally for these
            # two statuses regardless of these flags, so this isn't closing
            # a security hole - but leaving the stored record claiming
            # "connectors_enabled": true on a fully blocked client is
            # misleading data hygiene, and secure_client_offboarding.py's
            # whole job is to make these flags reflect reality.
            data["runtime_execution_enabled"] = False
            data["connectors_enabled"] = False
            data["swarm_enabled"] = False

        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return file_path


def main() -> None:
    guard = EntitlementGuard()

    entitlement_file = guard.create_demo_entitlement("dis_solar")
    decision = guard.check("dis_solar")

    print("")
    print("Entitlement Guard")
    print("-----------------")
    print(f"Entitlement file : {entitlement_file}")
    print(json.dumps(asdict(decision), indent=2))
    print("")


if __name__ == "__main__":
    main()
