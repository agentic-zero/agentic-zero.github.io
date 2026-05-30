"""
AGENTIC ZERO — CORE
Module: Message Queue System (M8)
Role: Async pipeline orchestration for Pioneer Team

Architecture: Simple file-based queue (no Redis needed for Phase 1)
              Upgradeable to Redis/Celery when scaling

Queue types:
  - scout_queue:     frameworks to research
  - architect_queue: processes to validate
  - builder_queue:   processes to build
  - packager_queue:  processes to package
  - guardian_queue:  processes to certify
  - completed_queue: certified products ready for delivery
  - failed_queue:    failed jobs for retry or review

Usage:
  # Enqueue a job
  queue.push("builder_queue", {"process_id": "SCOR-P1.1"})

  # Process jobs automatically
  python queue_system.py --worker builder
  python queue_system.py --pipeline SCOR-P1.1
  python queue_system.py --status
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# ── Add project root to path ──────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── LOGGING ───────────────────────────────────────────────────────────────────
logger.add(
    ROOT / "logs" / "queue_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | QUEUE | {message}",
)

# ── QUEUE CONFIGURATION ───────────────────────────────────────────────────────
QUEUE_PATH = Path(__file__).parent / "jobs"
QUEUE_NAMES = [
    "scout_queue",
    "architect_queue",
    "builder_queue",
    "packager_queue",
    "guardian_queue",
    "completed_queue",
    "failed_queue",
    "review_queue",
]

PIPELINE_SEQUENCE = [
    "builder_queue",
    "packager_queue",
    "guardian_queue",
    "completed_queue",
]


# ── JOB MODEL ─────────────────────────────────────────────────────────────────
class Job:
    def __init__(
        self,
        job_type: str,
        payload: dict,
        job_id: str = None,
        priority: int = 5,
        retries: int = 0,
        max_retries: int = 3,
        created_at: str = None,
        status: str = "pending",
    ):
        self.job_id = (
            job_id or f"{job_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        )
        self.job_type = job_type
        self.payload = payload
        self.priority = priority
        self.retries = retries
        self.max_retries = max_retries
        self.created_at = created_at or datetime.now().isoformat()
        self.status = status
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.result = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "payload": self.payload,
            "priority": self.priority,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "created_at": self.created_at,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        job = cls(
            job_type=data["job_type"],
            payload=data["payload"],
            job_id=data["job_id"],
            priority=data.get("priority", 5),
            retries=data.get("retries", 0),
            max_retries=data.get("max_retries", 3),
            created_at=data.get("created_at"),
            status=data.get("status", "pending"),
        )
        job.started_at = data.get("started_at")
        job.completed_at = data.get("completed_at")
        job.error = data.get("error")
        job.result = data.get("result")
        return job


# ── QUEUE MANAGER ─────────────────────────────────────────────────────────────
class QueueManager:
    """
    File-based queue system.
    Each queue is a folder. Each job is a JSON file.
    Simple, zero-dependency, upgradeable to Redis later.
    """

    def __init__(self, queue_path: Path = QUEUE_PATH):
        self.queue_path = queue_path
        self._init_queues()

    def _init_queues(self):
        """Create queue folders if they don't exist"""
        for name in QUEUE_NAMES:
            (self.queue_path / name).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Queue system initialized at {self.queue_path}")

    def push(self, queue_name: str, payload: dict, priority: int = 5) -> Job:
        """Add a job to a queue"""
        job_type = queue_name.replace("_queue", "")
        job = Job(job_type=job_type, payload=payload, priority=priority)

        job_file = self.queue_path / queue_name / f"{job.job_id}.json"
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(job.to_dict(), f, indent=2)

        logger.info(f"Job pushed: {job.job_id} → {queue_name}")
        return job

    def pop(self, queue_name: str) -> Optional[Job]:
        """Get the next job from a queue (FIFO by creation time)"""
        queue_dir = self.queue_path / queue_name
        jobs = sorted(queue_dir.glob("*.json"))

        if not jobs:
            return None

        # Get oldest job
        job_file = jobs[0]
        with open(job_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        job = Job.from_dict(data)
        job.status = "processing"
        job.started_at = datetime.now().isoformat()

        # Move to processing state
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(job.to_dict(), f, indent=2)

        logger.info(f"Job popped: {job.job_id} from {queue_name}")
        return job

    def complete(self, job: Job, result: dict, next_queue: str = None):
        """Mark job as completed and optionally move to next queue"""
        job.status = "completed"
        job.completed_at = datetime.now().isoformat()
        job.result = result

        # Remove from current queue
        current_file = self.queue_path / f"{job.job_type}_queue" / f"{job.job_id}.json"
        if current_file.exists():
            current_file.unlink()

        # Move to next queue or completed
        target_queue = next_queue or "completed_queue"
        next_file = self.queue_path / target_queue / f"{job.job_id}.json"
        with open(next_file, "w", encoding="utf-8") as f:
            json.dump(job.to_dict(), f, indent=2)

        logger.success(f"Job completed: {job.job_id} → {target_queue}")

    def fail(self, job: Job, error: str):
        """Mark job as failed and handle retry logic"""
        job.retries += 1
        job.error = error

        current_file = self.queue_path / f"{job.job_type}_queue" / f"{job.job_id}.json"
        if current_file.exists():
            current_file.unlink()

        if job.retries < job.max_retries:
            # Requeue for retry
            job.status = "pending"
            retry_file = (
                self.queue_path / f"{job.job_type}_queue" / f"{job.job_id}.json"
            )
            with open(retry_file, "w", encoding="utf-8") as f:
                json.dump(job.to_dict(), f, indent=2)
            logger.warning(
                f"Job failed, retrying ({job.retries}/{job.max_retries}): {job.job_id}"
            )
        else:
            # Move to failed queue
            job.status = "failed"
            job.completed_at = datetime.now().isoformat()
            failed_file = self.queue_path / "failed_queue" / f"{job.job_id}.json"
            with open(failed_file, "w", encoding="utf-8") as f:
                json.dump(job.to_dict(), f, indent=2)
            logger.error(f"Job permanently failed: {job.job_id} — {error}")

    def size(self, queue_name: str) -> int:
        """Get number of jobs in a queue"""
        queue_dir = self.queue_path / queue_name
        return len(list(queue_dir.glob("*.json")))

    def status(self) -> dict:
        """Get status of all queues"""
        status = {}
        for name in QUEUE_NAMES:
            status[name] = self.size(name)
        return status

    def list_jobs(self, queue_name: str) -> list[dict]:
        """List all jobs in a queue"""
        queue_dir = self.queue_path / queue_name
        jobs = []
        for job_file in sorted(queue_dir.glob("*.json")):
            with open(job_file, "r", encoding="utf-8") as f:
                jobs.append(json.load(f))
        return jobs

    def clear(self, queue_name: str):
        """Clear all jobs from a queue"""
        queue_dir = self.queue_path / queue_name
        for job_file in queue_dir.glob("*.json"):
            job_file.unlink()
        logger.warning(f"Queue cleared: {queue_name}")


# ── WORKERS ───────────────────────────────────────────────────────────────────
def run_builder_worker(queue: QueueManager, max_jobs: int = 10):
    """Builder worker — processes builder_queue"""
    logger.info("Builder worker started")
    processed = 0

    while processed < max_jobs:
        job = queue.pop("builder_queue")
        if not job:
            logger.info("Builder queue empty")
            break

        process_id = job.payload.get("process_id")
        logger.info(f"Builder worker processing: {process_id}")

        try:
            from pioneer_team.builder.builder import build_agent

            result = build_agent(process_id)

            if result:
                queue.complete(
                    job,
                    {
                        "agent_name": result.agent_spec.agent_name,
                        "ready_for_packager": result.ready_for_packager,
                    },
                    next_queue="packager_queue",
                )
                # Push to packager queue
                queue.push("packager_queue", {"process_id": process_id})
            else:
                queue.fail(job, "Builder returned no result")

        except Exception as e:
            queue.fail(job, str(e))

        processed += 1

    logger.info(f"Builder worker done. Processed: {processed}")
    return processed


def run_packager_worker(queue: QueueManager, max_jobs: int = 10):
    """Packager worker — processes packager_queue"""
    logger.info("Packager worker started")
    processed = 0

    while processed < max_jobs:
        job = queue.pop("packager_queue")
        if not job:
            logger.info("Packager queue empty")
            break

        process_id = job.payload.get("process_id")
        logger.info(f"Packager worker processing: {process_id}")

        try:
            from pioneer_team.packager.packager import package_agent

            result = package_agent(process_id)

            if result:
                queue.complete(
                    job,
                    {
                        "agent_name": result.agent_name,
                        "price_eur": result.pricing.total_price_eur,
                        "ready_for_guardian": result.ready_for_guardian,
                    },
                    next_queue="guardian_queue",
                )
                queue.push("guardian_queue", {"process_id": process_id})
            else:
                queue.fail(job, "Packager returned no result")

        except Exception as e:
            queue.fail(job, str(e))

        processed += 1

    logger.info(f"Packager worker done. Processed: {processed}")
    return processed


def run_guardian_worker(queue: QueueManager, max_jobs: int = 10):
    """Guardian worker — processes guardian_queue"""
    logger.info("Guardian worker started")
    processed = 0

    while processed < max_jobs:
        job = queue.pop("guardian_queue")
        if not job:
            logger.info("Guardian queue empty")
            break

        process_id = job.payload.get("process_id")
        logger.info(f"Guardian worker processing: {process_id}")

        try:
            from pioneer_team.guardian.guardian import certify_agent

            result = certify_agent(process_id)

            if result:
                if result.requires_human_sign_off:
                    queue.complete(
                        job,
                        {
                            "certificate_id": result.certificate.certificate_id,
                            "status": result.certificate.overall_status,
                        },
                        next_queue="review_queue",
                    )
                    logger.warning(f"Process {process_id} requires human review")
                else:
                    queue.complete(
                        job,
                        {
                            "certificate_id": result.certificate.certificate_id,
                            "status": result.certificate.overall_status,
                            "approved_for_library": result.approved_for_library,
                        },
                        next_queue="completed_queue",
                    )
            else:
                queue.fail(job, "Guardian returned no result")

        except Exception as e:
            queue.fail(job, str(e))

        processed += 1

    logger.info(f"Guardian worker done. Processed: {processed}")
    return processed


# ── PIPELINE RUNNER ───────────────────────────────────────────────────────────
def run_pipeline(process_ids: list, queue: QueueManager):
    """
    Queue-based pipeline: enqueue processes and run all workers in sequence
    Builder → Packager → Guardian
    """
    logger.info(f"Pipeline starting for: {process_ids}")

    # Enqueue all processes for builder
    for pid in process_ids:
        queue.push("builder_queue", {"process_id": pid})
        logger.info(f"Enqueued for builder: {pid}")

    print(f"\n📥 Enqueued {len(process_ids)} processes")
    print(f"   Queue status: {queue.status()}")

    # Run workers in sequence
    print(f"\n🔧 Running Builder worker...")
    built = run_builder_worker(queue, max_jobs=len(process_ids))
    print(f"   Built: {built}")

    print(f"\n📦 Running Packager worker...")
    packed = run_packager_worker(queue, max_jobs=len(process_ids))
    print(f"   Packaged: {packed}")

    print(f"\n🛡️  Running Guardian worker...")
    certified = run_guardian_worker(queue, max_jobs=len(process_ids))
    print(f"   Certified: {certified}")

    # Final status
    final_status = queue.status()
    print(f"\n{'=' * 40}")
    print(f"Pipeline complete")
    print(f"  ✅ Completed:      {final_status.get('completed_queue', 0)}")
    print(f"  ⚠️  Review needed:  {final_status.get('review_queue', 0)}")
    print(f"  ❌ Failed:         {final_status.get('failed_queue', 0)}")

    return final_status


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Agentic Zero Queue System (M8)")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument(
        "--pipeline",
        nargs="+",
        metavar="PROCESS_ID",
        help="Run full pipeline for process IDs",
    )
    parser.add_argument(
        "--worker",
        choices=["builder", "packager", "guardian"],
        help="Run specific worker",
    )
    parser.add_argument(
        "--push", nargs=2, metavar=("QUEUE", "PROCESS_ID"), help="Push a job to a queue"
    )
    parser.add_argument("--list", metavar="QUEUE", help="List jobs in a queue")
    parser.add_argument("--clear", metavar="QUEUE", help="Clear a queue")
    args = parser.parse_args()

    queue = QueueManager()

    if args.status:
        status = queue.status()
        print("\n📊 Queue Status — Agentic Zero")
        print("=" * 35)
        for name, count in status.items():
            icon = "✅" if count == 0 else "📥"
            if "failed" in name and count > 0:
                icon = "❌"
            if "review" in name and count > 0:
                icon = "⚠️ "
            if "completed" in name and count > 0:
                icon = "🎉"
            print(f"  {icon} {name:<25} {count} jobs")

    elif args.pipeline:
        run_pipeline(args.pipeline, queue)

    elif args.worker:
        workers = {
            "builder": run_builder_worker,
            "packager": run_packager_worker,
            "guardian": run_guardian_worker,
        }
        workers[args.worker](queue)

    elif args.push:
        queue_name, process_id = args.push
        job = queue.push(queue_name, {"process_id": process_id})
        print(f"✅ Job pushed: {job.job_id} → {queue_name}")

    elif args.list:
        jobs = queue.list_jobs(args.list)
        print(f"\n📋 Jobs in {args.list}: {len(jobs)}")
        for job in jobs:
            print(f"  {job['job_id']} | {job['status']} | {job['payload']}")

    elif args.clear:
        queue.clear(args.clear)
        print(f"🗑️  Queue cleared: {args.clear}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
