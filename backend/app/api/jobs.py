from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth import decode_access_token
from app.database import get_db
from app.job_queue import get_job, job_event_stream, job_to_dict
from app.models import User

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    job = await get_authorized_job(job_id, token, db)
    return job_to_dict(job)


@router.get("/{job_id}/events")
async def stream_job_events(
    job_id: str,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    await get_authorized_job(job_id, token, db)
    return StreamingResponse(
        job_event_stream(job_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def get_authorized_job(job_id: str, token: str | None, db: Session):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    if job.owner_id is None:
        return job
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="job token is required")
    user_id = decode_access_token(token)
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user or user.id != job.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="job access denied")
    return job