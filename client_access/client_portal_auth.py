# client_access/client_portal_auth.py

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from client_access.package_access_manager import PackageAccessManager
from security.audit_logger import AuditLogger


class PortalUserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    DISABLED = "DISABLED"


@dataclass
class PortalUser:
    user_id: str
    client_id: str
    email: str
    name: str
    role: str
    status: PortalUserStatus
    password_hash: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]


@dataclass
class PortalSession:
    session_id: str
    client_id: str
    user_id: str
    email: str
    role: str
    created_at: str
    expires_at: str
    metadata: dict[str, Any]


@dataclass
class LoginResult:
    success: bool
    reason: str
    session: Optional[PortalSession]


class ClientPortalAuth:
    """
    Minimal customer portal authentication.

    This does NOT grant access to internal engines.

    It only authenticates users for customer-facing resources:
    - downloads
    - reports
    - license summary
    - billing view
    - customer documentation

    Internal directories remain protected by AccessBoundary.
    """

    def __init__(
        self,
        *,
        users_root: str | Path = "client_access/state/users",
        sessions_root: str | Path = "client_access/state/sessions",
        audit_logger: Optional[AuditLogger] = None,
        package_access_manager: Optional[PackageAccessManager] = None,
    ) -> None:
        self.users_root = Path(users_root)
        self.sessions_root = Path(sessions_root)
        self.users_root.mkdir(parents=True, exist_ok=True)
        self.sessions_root.mkdir(parents=True, exist_ok=True)
        self.audit_logger = audit_logger or AuditLogger()
        self.package_access_manager = package_access_manager or PackageAccessManager()

    def create_user(
        self,
        *,
        client_id: str,
        email: str,
        name: str,
        role: str,
        password: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> PortalUser:
        now = datetime.now(timezone.utc).isoformat()

        user = PortalUser(
            user_id=f"portal-user-{uuid.uuid4()}",
            client_id=client_id,
            email=email.lower().strip(),
            name=name.strip(),
            role=role.strip(),
            status=PortalUserStatus.ACTIVE,
            password_hash=self._hash_password(password),
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        self._write_user(user)

        self.audit_logger.log(
            event_type="CLIENT_PORTAL_USER_CREATED",
            client_id=client_id,
            actor="system",
            action="create_portal_user",
            outcome="SUCCESS",
            severity="INFO",
            reason="Customer portal user created",
            metadata={
                "user_id": user.user_id,
                "email": user.email,
                "role": user.role,
            },
        )

        return user

    def login(
        self,
        *,
        client_id: str,
        email: str,
        password: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> LoginResult:
        user = self.get_user_by_email(client_id=client_id, email=email)

        if user is None:
            self._log_login(
                client_id=client_id,
                email=email,
                success=False,
                reason="User not found",
                metadata=metadata,
            )
            return LoginResult(False, "User not found", None)

        if user.status != PortalUserStatus.ACTIVE:
            self._log_login(
                client_id=client_id,
                email=email,
                success=False,
                reason=f"User status is {user.status.value}",
                metadata=metadata,
            )
            return LoginResult(False, f"User status is {user.status.value}", None)

        if not self._verify_password(password, user.password_hash):
            self._log_login(
                client_id=client_id,
                email=email,
                success=False,
                reason="Invalid credentials",
                metadata=metadata,
            )
            return LoginResult(False, "Invalid credentials", None)

        session = self._create_session(user=user, metadata=metadata or {})

        self._log_login(
            client_id=client_id,
            email=email,
            success=True,
            reason="Login successful",
            metadata={
                **(metadata or {}),
                "session_id": session.session_id,
            },
        )

        return LoginResult(True, "Login successful", session)

    def validate_session(self, session_id: str) -> Optional[PortalSession]:
        path = self.sessions_root / f"{session_id}.json"

        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))

        session = PortalSession(
            session_id=data["session_id"],
            client_id=data["client_id"],
            user_id=data["user_id"],
            email=data["email"],
            role=data["role"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            metadata=data.get("metadata", {}),
        )

        expires_at = datetime.fromisoformat(session.expires_at.replace("Z", "+00:00"))

        if datetime.now(timezone.utc) > expires_at:
            return None

        return session

    def authorize_session_resource(
        self,
        *,
        session_id: str,
        resource: str,
        action: str = "view",
    ) -> dict[str, Any]:
        session = self.validate_session(session_id)

        if session is None:
            return {
                "allowed": False,
                "reason": "Invalid or expired session",
                "resource": resource,
            }

        decision = self.package_access_manager.authorize_package_access(
            client_id=session.client_id,
            resource=resource,
            action=action,
            metadata={
                "portal_user": session.email,
                "portal_role": session.role,
                "session_id": session.session_id,
            },
        )

        return {
            "allowed": decision.allowed,
            "reason": decision.reason,
            "resource": resource,
            "client_id": session.client_id,
            "user": session.email,
            "mode": decision.mode.value,
        }

    def get_user_by_email(self, *, client_id: str, email: str) -> Optional[PortalUser]:
        normalized = email.lower().strip()

        for path in self._client_user_dir(client_id).glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))

            if data["email"].lower() == normalized:
                try:
                    portal_status = PortalUserStatus(data["status"])
                except ValueError:
                    portal_status = PortalUserStatus.LOCKED

                return PortalUser(
                    user_id=data["user_id"],
                    client_id=data["client_id"],
                    email=data["email"],
                    name=data["name"],
                    role=data["role"],
                    status=portal_status,
                    password_hash=data["password_hash"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    metadata=data.get("metadata", {}),
                )

        return None

    def disable_user(self, *, client_id: str, email: str, reason: str) -> PortalUser:
        user = self.get_user_by_email(client_id=client_id, email=email)

        if user is None:
            raise FileNotFoundError(f"Portal user not found: {email}")

        user.status = PortalUserStatus.DISABLED
        user.updated_at = datetime.now(timezone.utc).isoformat()
        user.metadata["disabled_reason"] = reason

        self._write_user(user)
        return user

    def _create_session(
        self,
        *,
        user: PortalUser,
        metadata: dict[str, Any],
    ) -> PortalSession:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=8)

        session = PortalSession(
            session_id=f"portal-session-{uuid.uuid4()}",
            client_id=user.client_id,
            user_id=user.user_id,
            email=user.email,
            role=user.role,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            metadata=metadata,
        )

        path = self.sessions_root / f"{session.session_id}.json"
        path.write_text(json.dumps(asdict(session), indent=2), encoding="utf-8")

        return session

    def _hash_password(self, password: str) -> str:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120_000,
        ).hex()
        return f"pbkdf2_sha256${salt}${digest}"

    def _verify_password(self, password: str, stored: str) -> bool:
        try:
            algorithm, salt, digest = stored.split("$", 2)
        except ValueError:
            return False

        if algorithm != "pbkdf2_sha256":
            return False

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120_000,
        ).hex()

        return hmac.compare_digest(candidate, digest)

    def _write_user(self, user: PortalUser) -> None:
        path = self._client_user_dir(user.client_id) / f"{user.user_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        data = asdict(user)
        data["status"] = user.status.value

        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _client_user_dir(self, client_id: str) -> Path:
        return self.users_root / client_id

    def _log_login(
        self,
        *,
        client_id: str,
        email: str,
        success: bool,
        reason: str,
        metadata: Optional[dict[str, Any]],
    ) -> None:
        self.audit_logger.log(
            event_type="CLIENT_PORTAL_LOGIN",
            client_id=client_id,
            actor=email,
            action="login",
            outcome="SUCCESS" if success else "FAILED",
            severity="INFO" if success else "WARNING",
            reason=reason,
            metadata=metadata or {},
        )


def main() -> None:
    auth = ClientPortalAuth()

    user = auth.get_user_by_email(
        client_id="dis_solar",
        email="elena.martin@dissolar.eu",
    )

    if user is None:
        user = auth.create_user(
            client_id="dis_solar",
            email="elena.martin@dissolar.eu",
            name="Elena Martin",
            role="Customer Admin",
            password="ChangeMe123!",
            metadata={"test": True},
        )

    login = auth.login(
        client_id="dis_solar",
        email="elena.martin@dissolar.eu",
        password="ChangeMe123!",
        metadata={"test": True},
    )

    if login.session:
        allowed = auth.authorize_session_resource(
            session_id=login.session.session_id,
            resource="customer_packages/dis_solar/package.zip",
            action="view",
        )

        denied = auth.authorize_session_resource(
            session_id=login.session.session_id,
            resource="the_machine/evolution_engine.py",
            action="view",
        )
    else:
        allowed = {}
        denied = {}

    output = Path("client_access/state/client_portal_auth_test_result.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "login_success": login.success,
                "session": asdict(login.session) if login.session else None,
                "allowed_resource": allowed,
                "denied_resource": denied,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("")
    print("Client Portal Auth")
    print("------------------")
    print(f"Login success    : {login.success}")
    print(f"Allowed resource : {allowed.get('allowed')}")
    print(f"Denied resource  : {denied.get('allowed')}")
    print(f"Output           : {output}")
    print("")


if __name__ == "__main__":
    main()
