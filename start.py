"""
AGENTIC ZERO — Start Script
Arranca el sistema completo y muestra el estado
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           AGENTIC ZERO — Autonomous Operations              ║
║         Regulated Supply Chains · Built for Complexity       ║
╚══════════════════════════════════════════════════════════════╝
""")


def check_env():
    print("► Checking environment...")
    from dotenv import load_dotenv

    load_dotenv()

    checks = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "LIBRARY_PATH": os.getenv("LIBRARY_PATH"),
        "GROQ_MODEL": os.getenv("GROQ_MODEL"),
    }

    all_ok = True
    for key, val in checks.items():
        if val and not val.startswith("your_"):
            print(f"  ✅ {key}: configured")
        else:
            print(f"  ⚠️  {key}: not configured")
            if key == "GROQ_API_KEY":
                all_ok = False

    return all_ok


def check_library():
    print("\n► Library status...")
    library_path = Path(os.getenv("LIBRARY_PATH", str(ROOT / "library")))

    stats = {
        "processes": 0,
        "variants": 0,
        "agents": 0,
        "packages": 0,
        "certificates": 0,
    }

    for folder in ["scor", "iso", "bpmn", "sector_specific"]:
        base = library_path / folder
        if (base / "processes").exists():
            stats["processes"] += len(list((base / "processes").glob("*.json")))
        if (base / "variants").exists():
            stats["variants"] += len(list((base / "variants").glob("*.json")))
        if (base / "agents").exists():
            stats["agents"] += len(list((base / "agents").glob("*_builder.json")))
        if (base / "packages").exists():
            stats["packages"] += len(list((base / "packages").glob("*.json")))
        if (base / "certificates").exists():
            stats["certificates"] += len(
                list((base / "certificates").glob("*_guardian.json"))
            )

    print(f"  📚 Processes:    {stats['processes']}")
    print(f"  ⬡  Variants:     {stats['variants']}")
    print(f"  🤖 Agents built: {stats['agents']}")
    print(f"  📦 Packaged:     {stats['packages']}")
    print(f"  🛡️  Certified:    {stats['certificates']}")

    return stats


def check_queue():
    print("\n► Queue status...")
    queue_path = ROOT / "core" / "queue" / "jobs"
    queues = [
        "scout_queue",
        "architect_queue",
        "builder_queue",
        "packager_queue",
        "guardian_queue",
        "completed_queue",
        "failed_queue",
        "review_queue",
    ]

    has_pending = False
    for q in queues:
        count = (
            len(list((queue_path / q).glob("*.json")))
            if (queue_path / q).exists()
            else 0
        )
        if count > 0:
            icon = "❌" if "failed" in q else "⚠️ " if "review" in q else "📥"
            print(f"  {icon} {q:<25} {count} jobs")
            has_pending = True

    if not has_pending:
        print("  ✅ All queues empty")

    return has_pending


def check_licenses():
    print("\n► License status...")
    licenses_file = ROOT / "core" / "license" / "licenses.json"

    if not licenses_file.exists():
        print("  No licenses issued yet")
        return

    with open(licenses_file) as f:
        licenses = json.load(f)

    active = [l for l in licenses if l["status"] == "active"]
    mrr = sum(l["monthly_fee_eur"] for l in active)

    print(f"  Active licenses: {len(active)}")
    print(f"  MRR:             €{mrr:,.2f}/month")

    for lic in active:
        print(
            f"  ✅ {lic['key_id']} — {lic['client_name']} · €{lic['monthly_fee_eur']}/mo"
        )


def start_api(port=8000):
    print(f"\n► Starting API Gateway on port {port}...")
    print(f"  Docs: http://localhost:{port}/docs")
    print(f"  Health: http://localhost:{port}/api/v1/health")
    print(f"\n  Press Ctrl+C to stop\n")
    print("─" * 60)

    os.chdir(ROOT / "core" / "api")
    sys.path.insert(0, str(ROOT / "core" / "api"))

    import uvicorn

    os.environ["API_PORT"] = str(port)
    uvicorn.run(
        "api_gateway:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[str(ROOT / "core" / "api")],
        log_level="warning",
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agentic Zero Start Script")
    parser.add_argument(
        "--no-api", action="store_true", help="Show status only, don't start API"
    )
    parser.add_argument("--port", type=int, default=8000, help="API port")
    args = parser.parse_args()

    banner()
    print(f"{'─' * 60}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — System check")
    print(f"{'─' * 60}")

    env_ok = check_env()
    lib_stats = check_library()
    queue_pending = check_queue()
    check_licenses()

    print(f"\n{'─' * 60}")
    print(f"  SUMMARY")
    print(f"{'─' * 60}")
    print(f"  Environment:  {'✅ Ready' if env_ok else '⚠️  Check .env'}")
    print(
        f"  Library:      {lib_stats['processes']} processes · {lib_stats['agents']} agents"
    )
    print(f"  Queue:        {'⚠️  Jobs pending' if queue_pending else '✅ Clean'}")
    print(f"{'─' * 60}")

    if args.no_api:
        print("\n  Status check complete. API not started (--no-api)")
        return

    if not env_ok:
        print(
            "\n  ⚠️  GROQ_API_KEY not configured. API will start but agents won't run."
        )
        print("  Configure F:\\agentic-zero\\.env before running agents.")

    start_api(args.port)


if __name__ == "__main__":
    main()
