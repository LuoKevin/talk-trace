from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.db.database import UPLOAD_DIR
from app.jobs.job_runner import run_job
from app.schemas import JobMetadata, JobResult, UploadResponse
from app.storage import job_repository


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> UploadResponse:
    # TODO: Add file size limits before writing the file to disk.
    # TODO: Validate content type and extension against supported audio formats.
    job_id = str(uuid4())
    original_name = Path(file.filename or "meeting-audio").name
    stored_path = UPLOAD_DIR / f"{job_id}-{original_name}"

    contents = await file.read()
    stored_path.write_bytes(contents)

    job = job_repository.create_job(
        job_id=job_id,
        filename=original_name,
        audio_path=str(stored_path),
    )
    background_tasks.add_task(run_job, job_id)

    return UploadResponse(job_id=job.id, status=job.status)


@router.get("/{job_id}", response_model=JobMetadata)
def get_job_status(job_id: str) -> JobMetadata:
    job = job_repository.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/result", response_model=JobResult)
def get_job_result(job_id: str) -> JobResult:
    job = job_repository.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    result = job_repository.get_result(job_id)
    if result is None:
        raise HTTPException(status_code=409, detail="Job result is not ready")

    return result
