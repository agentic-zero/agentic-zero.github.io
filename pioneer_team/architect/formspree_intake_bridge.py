"""
AGENTIC ZERO -- PIONEER TEAM
Formspree Intake Bridge v1.0

Role:
  Bridges the gap between what Formspree actually delivers (raw form-field
  payloads from two independently submitted HTML forms -- AUDIT ZERO and,
  optionally, ADVANCED AUDIT) and what customer_pipeline.py expects on disk
  (audit_zero.json + an optional fast_track.json).

  Without this bridge, the connected forms (audit_zero_connected.html,
  advanced_audit_connected.html) have nowhere correct to land -- Formspree
  emails/webhooks are not, by themselves, the clean JSON files the pipeline
  reads via --audit / --fast-track.

How the two submissions are matched:
  Both forms carry the same `audit_id` field (generated client-side in
  AUDIT ZERO, carried via querystring into ADVANCED AUDIT). This script
  reads both payloads and writes them into the same client folder, keyed
  by audit_id, so customer_pipeline.py can be pointed at the right files.

Input sources supported:
  1. Formspree webhook JSON (if you configure a webhook instead of/in addition
     to email notifications) -- this is the payload format this script expects
     by default: a flat dict of the form field names exactly as appended via
     FormData in the HTML forms.
  2. Manually exported Formspree submission JSON (downloaded from the
     Formspree dashboard) -- same flat-field shape, works unchanged.

Recommended path:
  pioneer_team/architect/formspree_intake_bridge.py

Usage:
  # After AUDIT ZERO submission lands (webhook payload saved to disk):
  python formspree_intake_bridge.py --submission raw_audit_zero_submission.json \\
      --output-dir clients/{slug}/{process}/essential_package/01_functional_analysis

  # After an Advanced Audit submission for the same audit_id lands:
  python formspree_intake_bridge.py --submission raw_advanced_audit_submission.json \\
      --output-dir clients/{slug}/{process}/essential_package/01_functional_analysis
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    value = (value or "lead").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "lead"


def read_json(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def is_advanced_audit_submission(submission: dict[str, Any]) -> bool:
    """
    ADVANCED AUDIT submissions carry a single 'fast_track_json' field (a
    JSON string built client-side in advanced_audit_connected.html).
    AUDIT ZERO submissions carry flat fields (company, sector, erp, ...)
    with no such field. This is how we tell them apart on intake.
    """
    return "fast_track_json" in submission and bool(submission.get("fast_track_json"))


def normalize_audit_zero_submission(submission: dict[str, Any]) -> dict[str, Any]:
    """
    Maps the raw Formspree field names sent by audit_zero_connected.html
    directly onto the AUDIT ZERO shape that
    pioneer_team/architect/functional_translator.py's normalize_audit_zero()
    already knows how to read. Field names already match 1:1 by design --
    this function exists mainly to drop Formspree's own bookkeeping fields
    (_subject, _replyto) and to keep this mapping in one explicit place
    instead of implicit duck-typing further downstream.
    """
    return {
        "audit_id": submission.get("audit_id", ""),
        "name": submission.get("name", ""),
        "email": submission.get("email", ""),
        "role": submission.get("role", ""),
        "company": submission.get("company", ""),
        "sector": submission.get("sector", ""),
        "erp": submission.get("erp", ""),
        "countries": submission.get("countries", ""),
        "volume": submission.get("volume", ""),
        "team_size": submission.get("team_size", ""),
        "areas": submission.get("areas", ""),
        "process_mapping": submission.get("process_mapping", ""),
        "systems_involved": submission.get("systems_involved", ""),
        "data_used": ", ".join(filter(None, [submission.get("inputs", ""), submission.get("outputs", "")])),
        "business_rules": submission.get("business_rules", ""),
        "critical_exceptions": submission.get("exceptions", ""),
        "notes": submission.get("notes") or submission.get("context", ""),
        "advanced_required": submission.get("advanced_required", "false") == "true",
        "received_at": _now(),
    }


def normalize_advanced_audit_submission(submission: dict[str, Any]) -> dict[str, Any]:
    """
    ADVANCED AUDIT's own payload is already a structured fast_track dict
    (built client-side in advanced_audit_connected.html and sent as a JSON
    string in the 'fast_track_json' field) -- just parse and pass through,
    adding the linking metadata.
    """
    fast_track = json.loads(submission.get("fast_track_json", "{}"))
    fast_track["audit_id"] = submission.get("audit_id", fast_track.get("audit_id", ""))
    fast_track["company"] = submission.get("company", "")
    fast_track["email"] = submission.get("email", "")
    fast_track["received_at"] = _now()
    return fast_track


def process_submission(submission_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    submission = read_json(submission_path)
    output_dir = Path(output_dir)

    if is_advanced_audit_submission(submission):
        fast_track = normalize_advanced_audit_submission(submission)
        company_slug = _slug(fast_track.get("company", "lead"))
        out_path = write_json(output_dir / f"fast_track_{company_slug}.json", fast_track)
        return {
            "kind": "advanced_audit",
            "audit_id": fast_track.get("audit_id", ""),
            "company": fast_track.get("company", ""),
            "output_path": str(out_path),
        }

    audit_zero = normalize_audit_zero_submission(submission)
    company_slug = _slug(audit_zero.get("company", "lead"))
    out_path = write_json(output_dir / f"audit_zero_{company_slug}.json", audit_zero)
    return {
        "kind": "audit_zero",
        "audit_id": audit_zero.get("audit_id", ""),
        "company": audit_zero.get("company", ""),
        "advanced_required": audit_zero.get("advanced_required", False),
        "output_path": str(out_path),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agentic Zero -- Formspree Intake Bridge (AUDIT ZERO / ADVANCED AUDIT -> pipeline-ready JSON)"
    )
    parser.add_argument("--submission", required=True, help="Path to the raw Formspree submission JSON")
    parser.add_argument("--output-dir", required=True, help="Directory to write the normalized JSON into")
    args = parser.parse_args()

    result = process_submission(args.submission, args.output_dir)

    print("\nFormspree Intake Bridge complete")
    print(f"  Kind:       {result['kind']}")
    print(f"  Audit ID:   {result['audit_id']}")
    print(f"  Company:    {result['company']}")
    print(f"  Output:     {result['output_path']}")
    if result["kind"] == "audit_zero" and result.get("advanced_required"):
        print("\n  This lead requires Advanced Audit -- wait for the matching")
        print("  submission with the same audit_id before running the full pipeline.")
    print("\nNext: customer_pipeline.py --audit <audit_zero file> [--fast-track <fast_track file>] --package-dir ...")
