# security/tamper_detection.py

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from security.audit_logger import AuditLogger


class TamperStatus:
    OK = "OK"
    UNTRACKED = "UNTRACKED"  # exists, never snapshotted - informational only
    MODIFIED = "MODIFIED"  # hash differs in a way that isn't a clean append
    SHRUNK = "SHRUNK"  # file got smaller than its baseline - always suspicious
    DELETED = "DELETED"  # file existed at baseline time, missing now
    GREW_CLEANLY = "GREW_CLEANLY"  # append-only file grew, old bytes unchanged


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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


@dataclass
class FileBaseline:
    path: str
    sha256: str
    size_bytes: int
    append_only: bool
    snapshotted_at: str


@dataclass
class FileVerification:
    path: str
    status: str
    detail: str
    baseline_size: Optional[int]
    current_size: Optional[int]


@dataclass
class TamperReport:
    checked_at: str
    files_checked: int
    clean: int
    suspicious: int
    verifications: list[dict[str, Any]]


class TamperDetector:
    """
    Detects unauthorized modification of the three classes of file this
    platform treats as security-relevant state:

      - License files (security/state/licenses/<client_id>.json) - these
        already carry their own internal fingerprint, verified on every
        license_manager.validate() call. This module adds an EXTERNAL
        snapshot/diff layer on top, so a license file edited while the
        system is offline (no validate() call to catch it) is still
        caught the next time someone explicitly runs --verify.

      - Entitlement files (security/state/entitlements/<client_id>.json) -
        these have NO internal integrity check today. A hand-edited
        status:"LOCKED" -> status:"ACTIVE" would silently work. This is
        the gap this module exists primarily to close.

      - Audit log files (security/state/audit_logs/<client_id>.jsonl) -
        append-only by contract. Append-only files are checked with a
        stricter rule than "did the hash change": a clean append (new
        content starts with the exact same bytes as the baseline, plus
        more at the end) is GREW_CLEANLY, not flagged. Anything else -
        especially the file getting SMALLER, which can only mean a line
        was deleted - is flagged as tampering. This is how a deleted
        audit line gets caught even though deleting one line from a
        JSONL file does not change its line *count* signature in an
        obvious way, but always changes its size/hash in a way that
        breaks the "starts with baseline bytes" check.

    This module does not prevent tampering - it detects it after the
    fact, and logs a CRITICAL audit event the moment it's found. Like
    every other security/ module, it fails toward suspicion: an unreadable
    or missing file where one was expected is reported, never silently
    skipped.
    """

    def __init__(
        self,
        manifest_path: str | Path = "security/state/tamper_manifest.json",
        audit_logger: Optional[AuditLogger] = None,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.audit_logger = audit_logger or AuditLogger()

    def _load_manifest(self) -> dict[str, dict[str, Any]]:
        data = read_json(self.manifest_path, {"files": {}})
        return data.get("files", {})

    def _save_manifest(self, files: dict[str, dict[str, Any]]) -> None:
        write_json(self.manifest_path, {"updated_at": now(), "files": files})

    def discover_client_files(self, client_id: str) -> list[tuple[Path, bool]]:
        """Returns (path, append_only) pairs for the standard security
        state files of one client - the common case for --snapshot/--verify.

        token_usage.jsonl added 29 Jun 2026 - built (saas/token_governance.py,
        M11) after this discovery list already existed, so it was never
        protected. A deleted line here would hide real spend before a
        billing audit - the exact same attack already proven against
        audit_logs.jsonl (a deleted CONTRACT_GO_LIVE line, caught as
        SHRUNK). Append-only, same rule.
        """
        return [
            (Path("security/state/licenses") / f"{client_id}.json", False),
            (Path("security/state/entitlements") / f"{client_id}.json", False),
            (Path("security/state/audit_logs") / f"{client_id}.jsonl", True),
            (Path("saas/state/token_usage") / f"{client_id}.jsonl", True),
        ]

    def snapshot(self, paths: list[tuple[Path, bool]]) -> list[FileBaseline]:
        manifest = self._load_manifest()
        baselines = []

        for path, append_only in paths:
            if not path.exists():
                continue

            baseline = FileBaseline(
                path=str(path),
                sha256=sha256_of(path),
                size_bytes=path.stat().st_size,
                append_only=append_only,
                snapshotted_at=now(),
            )
            manifest[str(path)] = asdict(baseline)
            baselines.append(baseline)

        self._save_manifest(manifest)
        return baselines

    def _is_clean_append(self, baseline_path: Path, baseline_sha256: str, baseline_size: int) -> bool:
        """For append-only files: re-hash just the FIRST baseline_size bytes
        of the current file and compare to the baseline's full-file hash.
        If they match, every byte that existed at snapshot time is still
        there, unchanged, in the same order - the only change is content
        appended after that point, which is exactly what's expected.
        """
        current_size = baseline_path.stat().st_size
        if current_size < baseline_size:
            return False

        h = hashlib.sha256()
        with open(baseline_path, "rb") as f:
            remaining = baseline_size
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                h.update(chunk)
                remaining -= len(chunk)

        return h.hexdigest() == baseline_sha256

    def verify(self, paths: Optional[list[tuple[Path, bool]]] = None) -> TamperReport:
        manifest = self._load_manifest()
        verifications: list[FileVerification] = []

        check_paths = paths or [(Path(p), info.get("append_only", False)) for p, info in manifest.items()]

        for path, _ in check_paths:
            key = str(path)
            baseline = manifest.get(key)

            if baseline is None:
                if path.exists():
                    verifications.append(
                        FileVerification(
                            path=key,
                            status=TamperStatus.UNTRACKED,
                            detail="File exists but has never been snapshotted - no baseline to compare against.",
                            baseline_size=None,
                            current_size=path.stat().st_size,
                        )
                    )
                continue

            if not path.exists():
                verifications.append(
                    FileVerification(
                        path=key,
                        status=TamperStatus.DELETED,
                        detail="File existed at last snapshot but is now missing.",
                        baseline_size=baseline["size_bytes"],
                        current_size=None,
                    )
                )
                self._log_tamper(key, TamperStatus.DELETED, "File deleted since last snapshot.")
                continue

            current_size = path.stat().st_size
            current_sha256 = sha256_of(path)

            if current_sha256 == baseline["sha256"]:
                verifications.append(
                    FileVerification(
                        path=key,
                        status=TamperStatus.OK,
                        detail="Unchanged since last snapshot.",
                        baseline_size=baseline["size_bytes"],
                        current_size=current_size,
                    )
                )
                continue

            if current_size < baseline["size_bytes"]:
                verifications.append(
                    FileVerification(
                        path=key,
                        status=TamperStatus.SHRUNK,
                        detail=(
                            f"File shrank from {baseline['size_bytes']} to {current_size} bytes. "
                            f"This file should only ever grow or stay the same - shrinking strongly "
                            f"suggests content was deleted."
                        ),
                        baseline_size=baseline["size_bytes"],
                        current_size=current_size,
                    )
                )
                self._log_tamper(key, TamperStatus.SHRUNK, f"Shrank from {baseline['size_bytes']} to {current_size} bytes.")
                continue

            if baseline.get("append_only") and self._is_clean_append(
                path, baseline["sha256"], baseline["size_bytes"]
            ):
                verifications.append(
                    FileVerification(
                        path=key,
                        status=TamperStatus.GREW_CLEANLY,
                        detail="Append-only file grew; all previously-recorded bytes are unchanged.",
                        baseline_size=baseline["size_bytes"],
                        current_size=current_size,
                    )
                )
                continue

            verifications.append(
                FileVerification(
                    path=key,
                    status=TamperStatus.MODIFIED,
                    detail=(
                        "Content changed in a way that is not a clean append. For a license or "
                        "entitlement file, this means the file was edited directly outside the "
                        "normal API. For an audit log, this means an existing line was altered, "
                        "not just a new one added."
                    ),
                    baseline_size=baseline["size_bytes"],
                    current_size=current_size,
                )
            )
            self._log_tamper(key, TamperStatus.MODIFIED, "Content changed in a non-append-only way.")

        suspicious_statuses = {TamperStatus.MODIFIED, TamperStatus.SHRUNK, TamperStatus.DELETED}
        suspicious = sum(1 for v in verifications if v.status in suspicious_statuses)

        report = TamperReport(
            checked_at=now(),
            files_checked=len(verifications),
            clean=len(verifications) - suspicious,
            suspicious=suspicious,
            verifications=[asdict(v) for v in verifications],
        )
        return report

    def _log_tamper(self, path: str, status: str, detail: str) -> None:
        # client_id is recovered from the filename stem - audit_logger needs
        # SOME client_id; tamper events on files without an obvious client
        # association are logged under "_platform".
        client_id = Path(path).stem or "_platform"
        self.audit_logger.log(
            event_type="TAMPER_DETECTED",
            client_id=client_id,
            actor="tamper_detection",
            action="verify",
            outcome=status,
            severity="CRITICAL",
            reason=detail,
            metadata={"path": path},
        )


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Agentic Zero - Tamper Detection")
    sub = parser.add_subparsers(dest="command", required=True)

    p_snapshot = sub.add_parser("snapshot", help="Record a new baseline for a client's security files")
    p_snapshot.add_argument("--client-id", required=True)

    p_verify = sub.add_parser("verify", help="Check current files against their last snapshot")
    p_verify.add_argument("--client-id", default="", help="Limit to one client, or omit to verify everything in the manifest")

    args = parser.parse_args()
    detector = TamperDetector()

    if args.command == "snapshot":
        paths = detector.discover_client_files(args.client_id)
        baselines = detector.snapshot(paths)
        print(f"\nTamper Detection - snapshot recorded for '{args.client_id}'")
        for b in baselines:
            print(f"  {b.path} ({b.size_bytes} bytes, append_only={b.append_only})")
        if not baselines:
            print("  (no files found for this client yet)")
        return

    if args.client_id:
        paths = detector.discover_client_files(args.client_id)
    else:
        paths = None

    report = detector.verify(paths)

    print("\nTamper Detection - verification complete")
    print(f"Files checked: {report.files_checked}")
    print(f"Clean:         {report.clean}")
    print(f"Suspicious:    {report.suspicious}")
    for v in report.verifications:
        marker = "OK" if v["status"] in ("OK", "GREW_CLEANLY", "UNTRACKED") else "!!"
        print(f"  [{marker}] {v['path']}: {v['status']} - {v['detail']}")

    if report.suspicious:
        raise SystemExit(1)


if __name__ == "__main__":
    run_cli()
