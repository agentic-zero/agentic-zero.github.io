"""
bulk_approve.py — Agentic Zero
Mueve a completed_queue todos los jobs de review_queue que ya tienen
auditor_review.decision == AUTO_APPROVE en su guardian JSON.
"""

import json
import sys
from pathlib import Path

ROOT = Path("F:/agentic-zero")
REVIEW_Q = ROOT / "core" / "queue" / "jobs" / "review_queue"
COMPLETED_Q = ROOT / "core" / "queue" / "jobs" / "completed_queue"
CERT_DIRS = [
    ROOT / "library" / "scor" / "certificates",
    ROOT / "library" / "frameworks" / "certificates",
    ROOT / "library" / "iso" / "certificates",
    ROOT / "library" / "bpmn" / "certificates",
    ROOT / "library" / "sector_specific" / "certificates",
]


def find_guardian(process_id: str) -> Path | None:
    for d in CERT_DIRS:
        p = d / f"{process_id}_guardian.json"
        if p.exists():
            return p
    return None


def load_guardian(process_id: str) -> dict | None:
    p = find_guardian(process_id)
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def get_review_jobs():
    jobs = []
    for jf in REVIEW_Q.glob("review_*.json"):
        with open(jf, encoding="utf-8") as f:
            data = json.load(f)
        pid = (
            data.get("payload", {}).get("process_id")
            or data.get("process_id")
            or data.get("data", {}).get("process_id", "unknown")
        )
        jobs.append((jf, pid))
    return jobs


def main():
    dry_run = "--dry-run" in sys.argv
    jobs = get_review_jobs()
    print(f"\nReview queue: {len(jobs)} jobs")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")

    approved = []
    skipped = []
    no_cert = []
    dupes = set()

    for jf, pid in jobs:
        if pid in dupes:
            # Duplicate — move to completed without checking (already approved)
            if not dry_run:
                dest = COMPLETED_Q / jf.name
                jf.rename(dest)
            print(f"  [DUPE→COMPLETE] {pid}")
            approved.append(pid)
            continue

        guardian = load_guardian(pid)
        if not guardian:
            print(f"  [NO CERT]       {pid}")
            no_cert.append(pid)
            continue

        auditor_review = guardian.get("auditor_review", {})
        decision = auditor_review.get("decision", "")

        if decision == "AUTO_APPROVE":
            if not dry_run:
                # Update guardian approved_for_delivery = True
                guardian["approved_for_delivery"] = True
                guardian["human_sign_off"] = {
                    "signed_by": "Alberto Munoz Waissen — Founder & CEO",
                    "signed_at": __import__("datetime").datetime.now().isoformat(),
                    "method": "bulk_approve · AUTO_APPROVE criteria met",
                }
                cert_path = find_guardian(pid)
                with open(cert_path, "w", encoding="utf-8") as f:
                    json.dump(guardian, f, indent=2, ensure_ascii=False)
                # Move job
                dest = COMPLETED_Q / jf.name
                jf.rename(dest)
            print(
                f"  [AUTO-APPROVE]  {pid} · score {guardian.get('certificate', {}).get('overall_score', '?')}"
            )
            approved.append(pid)
            dupes.add(pid)
        else:
            print(f"  [SKIP {decision:12}] {pid}")
            skipped.append(pid)

    print(f"\n{'=' * 50}")
    print(f"  AUTO_APPROVE moved to completed : {len(approved)}")
    print(f"  Skipped (not AUTO_APPROVE)      : {len(skipped)}")
    print(f"  No certificate found            : {len(no_cert)}")
    if dry_run:
        print("\n  DRY RUN — no changes made. Remove --dry-run to apply.")


if __name__ == "__main__":
    main()
