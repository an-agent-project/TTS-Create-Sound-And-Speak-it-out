import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

TERMINAL_STATUSES = {"completed", "failed"}


@dataclass
class JobRecord:
    id: str
    kind: str
    owner_id: int | None = None
    status: str = "queued"
    progress: int = 0
    message: str = "任务已创建"
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: int = 0


_jobs: dict[str, JobRecord] = {}
_jobs_lock = asyncio.Lock()


def _clamp_progress(value: int) -> int:
    return max(0, min(100, int(value)))


async def create_job(kind: str, owner_id: int | None = None, message: str = "任务已创建") -> JobRecord:
    async with _jobs_lock:
        job = JobRecord(id=uuid4().hex, kind=kind, owner_id=owner_id, message=message)
        _jobs[job.id] = job
        return job


async def get_job(job_id: str) -> JobRecord | None:
    async with _jobs_lock:
        return _jobs.get(job_id)


async def update_job(
    job_id: str,
    *,
    status: str | None = None,
    progress: int | None = None,
    message: str | None = None,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> JobRecord | None:
    async with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return None
        if status is not None:
            job.status = status
        if progress is not None:
            job.progress = _clamp_progress(progress)
        if message is not None:
            job.message = message
        if result is not None:
            job.result = result
        if error is not None:
            job.error = error
        job.updated_at = datetime.now(timezone.utc).isoformat()
        job.version += 1
        return job


def job_to_dict(job: JobRecord) -> dict[str, Any]:
    return {
        "jobId": job.id,
        "kind": job.kind,
        "ownerId": job.owner_id,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "result": job.result,
        "error": job.error,
        "createdAt": job.created_at,
        "updatedAt": job.updated_at,
    }


def format_sse(job: JobRecord) -> str:
    return f"data: {json.dumps(job_to_dict(job), ensure_ascii=False)}\n\n"


async def job_event_stream(job_id: str, poll_interval: float = 0.35):
    last_version = -1
    while True:
        job = await get_job(job_id)
        if not job:
            payload = {"jobId": job_id, "status": "failed", "progress": 100, "message": "任务不存在", "error": "job not found"}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            return
        if job.version != last_version:
            last_version = job.version
            yield format_sse(job)
        if job.status in TERMINAL_STATUSES:
            return
        await asyncio.sleep(poll_interval)