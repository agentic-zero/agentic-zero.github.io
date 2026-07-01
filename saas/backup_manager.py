# saas/backup_manager.py

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from saas.tenant_manager import TenantManager


class BackupStatus(str, Enum):
    CREATED = "CREATED"
    FAILED = "FAILED"
    RESTORED = "RESTORED"


@dataclass
class BackupRecord:
    backup_id: str
    client_id: str
    status: BackupStatus
    source_paths: list[str]
    backup_path: str
    created_at: str
    metadata: dict[str, Any]


class BackupManager:
    """
    SaaS backup manager for Agentic Zero.

    This module does NOT execute Shield, The Machine or runtime actions.

    Responsibilities:
    - create tenant backups
    - backup SaaS state
    - backup security state
    - backup client package snapshot
    - list backups
    - restore backup metadata
    """

    # Subdirectory -> filename pattern for every state file that belongs
    # to ONE specific client. Previously this module copied the entire
    # "saas/state" and "security/state" directory trees wholesale - which
    # meant a backup for "dis_solar" silently contained every OTHER
    # tenant's billing/tenant/license/audit data too (confirmed in
    # testing: dis_solar's backup contained typo_test's billing.json).
    # That is a real data-isolation problem before this ever exports a
    # backup to a client for support/compliance/GDPR purposes. Each entry
    # below is scoped to exactly one client_id's file.
    CLIENT_SCOPED_FILES = [
        ("saas/state/tenants", "{client_id}.json"),
        ("saas/state/billing", "{client_id}.json"),
        ("saas/state/usage", "{client_id}.jsonl"),
        ("saas/state/monitoring", "{client_id}.json"),
        ("saas/state/deployments", "{client_id}.json"),
        ("security/state/licenses", "{client_id}.json"),
        ("security/state/entitlements", "{client_id}.json"),
        ("security/state/audit_logs", "{client_id}.jsonl"),
        # Added 29 Jun 2026 - both built AFTER this scoping was first
        # written, so neither was originally included. token_usage.py
        # (M11) writes one JSONL file per client; evidence_shield.py
        # (M12) writes a FOLDER per client (multiple package files
        # inside, one per decision) - _client_scoped_paths() below
        # resolves either shape correctly since create_backup()'s copy
        # loop already branches on src.is_dir() vs is_file().
        ("saas/state/token_usage", "{client_id}.jsonl"),
        ("agentic_shield/evidence", "{client_id}"),
    ]

    def __init__(
        self,
        *,
        tenant_manager: Optional[TenantManager] = None,
        backup_root: str | Path = "saas/backups",
    ) -> None:
        self.tenant_manager = tenant_manager or TenantManager()
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        *,
        client_id: str,
        include_client_package: bool = True,
        metadata: Optional[dict[str, Any]] = None,
    ) -> BackupRecord:
        tenant = self.tenant_manager.get_tenant(client_id)

        if tenant is None:
            raise FileNotFoundError(f"Tenant not found for client_id='{client_id}'")

        backup_id = f"backup-{uuid.uuid4()}"
        created_at = datetime.now(timezone.utc).isoformat()

        backup_dir = self.backup_root / client_id / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        source_paths = self._client_scoped_paths(client_id)

        if include_client_package:
            source_paths.append(Path(tenant.package_path))

        copied_sources: list[str] = []

        try:
            for src in source_paths:
                if not src.exists():
                    continue

                target = backup_dir / self._safe_target_name(src)

                if src.is_dir():
                    shutil.copytree(src, target, dirs_exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)

                copied_sources.append(str(src))

            record = BackupRecord(
                backup_id=backup_id,
                client_id=client_id,
                status=BackupStatus.CREATED,
                source_paths=copied_sources,
                backup_path=str(backup_dir),
                created_at=created_at,
                metadata=metadata or {},
            )

            self._write_record(record)
            return record

        except Exception as exc:
            record = BackupRecord(
                backup_id=backup_id,
                client_id=client_id,
                status=BackupStatus.FAILED,
                source_paths=copied_sources,
                backup_path=str(backup_dir),
                created_at=created_at,
                metadata={
                    **(metadata or {}),
                    "error": str(exc),
                },
            )
            self._write_record(record)
            raise

    def list_backups(self, client_id: str) -> list[BackupRecord]:
        root = self.backup_root / client_id

        if not root.exists():
            return []

        records: list[BackupRecord] = []

        for file in sorted(root.glob("*/backup_record.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                try:
                    status = BackupStatus(data["status"])
                except ValueError:
                    status = BackupStatus.FAILED

                records.append(
                    BackupRecord(
                        backup_id=data["backup_id"],
                        client_id=data["client_id"],
                        status=status,
                        source_paths=data.get("source_paths", []),
                        backup_path=data["backup_path"],
                        created_at=data["created_at"],
                        metadata=data.get("metadata", {}),
                    )
                )
            except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError):
                # Corrupted backup_record.json - skip it rather than crash
                # the whole list_backups() call for every other valid
                # backup this client has.
                continue

        return records

    def get_latest_backup(self, client_id: str) -> Optional[BackupRecord]:
        backups = self.list_backups(client_id)

        if not backups:
            return None

        return sorted(backups, key=lambda b: b.created_at)[-1]

    def mark_restored(
        self,
        *,
        client_id: str,
        backup_id: str,
        reason: str,
    ) -> BackupRecord:
        record = self._require_backup(client_id, backup_id)
        record.status = BackupStatus.RESTORED
        record.metadata["restore_reason"] = reason
        record.metadata["restored_at"] = datetime.now(timezone.utc).isoformat()

        self._write_record(record)
        return record

    def _require_backup(self, client_id: str, backup_id: str) -> BackupRecord:
        for backup in self.list_backups(client_id):
            if backup.backup_id == backup_id:
                return backup

        raise FileNotFoundError(
            f"Backup '{backup_id}' not found for client_id='{client_id}'"
        )

    def _write_record(self, record: BackupRecord) -> None:
        path = Path(record.backup_path) / "backup_record.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        data = asdict(record)
        data["status"] = record.status.value

        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _client_scoped_paths(self, client_id: str) -> list[Path]:
        return [
            Path(directory) / filename_pattern.format(client_id=client_id)
            for directory, filename_pattern in self.CLIENT_SCOPED_FILES
        ]

    def _safe_target_name(self, path: Path) -> str:
        return str(path).replace(":", "").replace("\\", "__").replace("/", "__")


def main() -> None:
    tenant_manager = TenantManager()

    if not tenant_manager.tenant_exists("dis_solar"):
        tenant_manager.create_tenant(
            client_id="dis_solar",
            company_name="DIS Solar Europe",
            product="AGENTIC_ONE",
            plan="ENTERPRISE",
            package_path="clients/dis_solar/agentic_one/essential_package",
            environment="production",
        )

    manager = BackupManager(tenant_manager=tenant_manager)

    record = manager.create_backup(
        client_id="dis_solar",
        include_client_package=True,
        metadata={
            "source": "backup_manager_test",
        },
    )

    print("")
    print("Backup Manager")
    print("--------------")
    print(json.dumps(asdict(record), indent=2))
    print("")


if __name__ == "__main__":
    main()
