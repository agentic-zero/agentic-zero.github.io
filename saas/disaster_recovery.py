# saas/disaster_recovery.py

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from saas.backup_manager import BackupManager, BackupRecord
from saas.tenant_manager import TenantManager


class RecoveryStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class RecoveryRecord:
    recovery_id: str
    client_id: str
    backup_id: str
    status: RecoveryStatus
    backup_path: str
    restored_paths: list[str]
    reason: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]


class DisasterRecovery:
    """
    SaaS disaster recovery manager for Agentic Zero.

    This module does NOT execute:
    - Agentic Shield
    - The Machine
    - Runtime actions

    Responsibilities:
    - plan recovery from latest backup
    - restore copied backup folders to a recovery sandbox
    - track recovery lifecycle
    - preserve recovery evidence
    """

    def __init__(
        self,
        *,
        tenant_manager: Optional[TenantManager] = None,
        backup_manager: Optional[BackupManager] = None,
        recovery_root: str | Path = "saas/recovery",
    ) -> None:
        self.tenant_manager = tenant_manager or TenantManager()
        self.backup_manager = backup_manager or BackupManager(
            tenant_manager=self.tenant_manager
        )
        self.recovery_root = Path(recovery_root)
        self.recovery_root.mkdir(parents=True, exist_ok=True)

    def plan_recovery(
        self,
        *,
        client_id: str,
        backup_id: Optional[str] = None,
        reason: str = "Disaster recovery plan",
        metadata: Optional[dict[str, Any]] = None,
    ) -> RecoveryRecord:
        backup = self._select_backup(client_id, backup_id)

        now = datetime.now(timezone.utc).isoformat()

        record = RecoveryRecord(
            recovery_id=f"recovery-{uuid.uuid4()}",
            client_id=client_id,
            backup_id=backup.backup_id,
            status=RecoveryStatus.PLANNED,
            backup_path=backup.backup_path,
            restored_paths=[],
            reason=reason,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        self._write_record(record)
        return record

    def execute_recovery(self, client_id: str, recovery_id: str) -> RecoveryRecord:
        record = self._require_recovery(client_id, recovery_id)

        record.status = RecoveryStatus.IN_PROGRESS
        record.updated_at = datetime.now(timezone.utc).isoformat()
        self._write_record(record)

        try:
            backup_path = Path(record.backup_path)

            if not backup_path.exists():
                raise FileNotFoundError(f"Backup path not found: {backup_path}")

            recovery_dir = self._recovery_dir(client_id, recovery_id)
            recovery_dir.mkdir(parents=True, exist_ok=True)

            restored_paths: list[str] = []

            for item in backup_path.iterdir():
                if item.name == "backup_record.json":
                    continue

                target = recovery_dir / item.name

                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)

                restored_paths.append(str(target))

            record.restored_paths = restored_paths
            record.status = RecoveryStatus.COMPLETED
            record.updated_at = datetime.now(timezone.utc).isoformat()
            record.metadata["completed_at"] = record.updated_at

            self.backup_manager.mark_restored(
                client_id=client_id,
                backup_id=record.backup_id,
                reason=record.reason,
            )

            self._write_record(record)
            return record

        except Exception as exc:
            record.status = RecoveryStatus.FAILED
            record.updated_at = datetime.now(timezone.utc).isoformat()
            record.metadata["error"] = str(exc)
            self._write_record(record)
            raise

    def get_recovery(
        self, client_id: str, recovery_id: str
    ) -> Optional[RecoveryRecord]:
        path = self._record_path(client_id, recovery_id)

        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            try:
                status = RecoveryStatus(data["status"])
            except ValueError:
                status = RecoveryStatus.FAILED

            return RecoveryRecord(
                recovery_id=data["recovery_id"],
                client_id=data["client_id"],
                backup_id=data["backup_id"],
                status=status,
                backup_path=data["backup_path"],
                restored_paths=data.get("restored_paths", []),
                reason=data["reason"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError):
            return None

    def list_recoveries(self, client_id: str) -> list[RecoveryRecord]:
        root = self.recovery_root / client_id

        if not root.exists():
            return []

        records: list[RecoveryRecord] = []

        for file in sorted(root.glob("recovery-*/recovery_record.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                try:
                    status = RecoveryStatus(data["status"])
                except ValueError:
                    status = RecoveryStatus.FAILED

                records.append(
                    RecoveryRecord(
                        recovery_id=data["recovery_id"],
                        client_id=data["client_id"],
                        backup_id=data["backup_id"],
                        status=status,
                        backup_path=data["backup_path"],
                        restored_paths=data.get("restored_paths", []),
                        reason=data["reason"],
                        created_at=data["created_at"],
                        updated_at=data["updated_at"],
                        metadata=data.get("metadata", {}),
                    )
                )
            except (json.JSONDecodeError, OSError, UnicodeDecodeError, KeyError):
                continue

        return records

    def _select_backup(self, client_id: str, backup_id: Optional[str]) -> BackupRecord:
        if backup_id:
            for backup in self.backup_manager.list_backups(client_id):
                if backup.backup_id == backup_id:
                    return backup

            raise FileNotFoundError(
                f"Backup '{backup_id}' not found for client_id='{client_id}'"
            )

        latest = self.backup_manager.get_latest_backup(client_id)

        if latest is None:
            raise FileNotFoundError(f"No backups found for client_id='{client_id}'")

        return latest

    def _require_recovery(self, client_id: str, recovery_id: str) -> RecoveryRecord:
        record = self.get_recovery(client_id, recovery_id)

        if record is None:
            raise FileNotFoundError(
                f"Recovery '{recovery_id}' not found for client_id='{client_id}'"
            )

        return record

    def _write_record(self, record: RecoveryRecord) -> None:
        path = self._record_path(record.client_id, record.recovery_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = asdict(record)
        data["status"] = record.status.value

        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _record_path(self, client_id: str, recovery_id: str) -> Path:
        return self.recovery_root / client_id / recovery_id / "recovery_record.json"

    def _recovery_dir(self, client_id: str, recovery_id: str) -> Path:
        return self.recovery_root / client_id / recovery_id / "restored"


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

    backup_manager = BackupManager(tenant_manager=tenant_manager)

    if backup_manager.get_latest_backup("dis_solar") is None:
        backup_manager.create_backup(
            client_id="dis_solar",
            include_client_package=True,
            metadata={
                "source": "disaster_recovery_test",
            },
        )

    recovery = DisasterRecovery(
        tenant_manager=tenant_manager,
        backup_manager=backup_manager,
    )

    record = recovery.plan_recovery(
        client_id="dis_solar",
        reason="Disaster recovery smoke test",
        metadata={
            "source": "disaster_recovery_test",
        },
    )

    record = recovery.execute_recovery(
        client_id="dis_solar",
        recovery_id=record.recovery_id,
    )

    print("")
    print("Disaster Recovery")
    print("-----------------")
    print(json.dumps(asdict(record), indent=2))
    print("")


if __name__ == "__main__":
    main()
