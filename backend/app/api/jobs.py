from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from app.db.database import UPLOAD_DIR
from app.jobs.job_runner import run_job
from app.schemas import JobArtifacts, JobMetadata, JobResult, UploadResponse
from app.storage import job_repository


router = APIRouter()

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4", ".flac", ".ogg", ".webm"}


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> UploadResponse:
    original_name = _validate_upload_filename(file.filename)
    _validate_upload_content_type(file.content_type)

    job_id = str(uuid4())
    stored_path = UPLOAD_DIR / f"{job_id}-{original_name}"

    contents = await file.read()
    content_length = len(contents)
    if content_length > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Audio file is too large for the MVP upload limit",
        )
    elif content_length == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty",
        )

    stored_path.write_bytes(contents)

    job = job_repository.create_job(
        job_id=job_id,
        filename=original_name,
        audio_path=str(stored_path),
    )
    background_tasks.add_task(run_job, job_id)

    return UploadResponse(job_id=job.id, status=job.status)


@router.get("/{job_id}/artifacts", response_model=JobArtifacts)
def get_job_artifacts(job_id: str) -> JobArtifacts:
    job = job_repository.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    transcript = job_repository.get_raw_transcript(job_id)
    diarization = job_repository.get_raw_diarization(job_id)
    aligned = job_repository.get_aligned_transcript(job_id)
    summarization = job_repository.get_raw_summarization(job_id)
    result = job_repository.get_result(job_id)
    return JobArtifacts(
        raw_transcript=transcript,
        raw_diarization=diarization,
        aligned_transcript=aligned,
        raw_summarization=summarization,
        result=result,
    )


def _validate_upload_filename(filename: str | None) -> str:
    original_name = Path(filename or "").name
    if not original_name:
        raise HTTPException(status_code=400, detail="Audio file must have a filename")

    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio file extension. "
                f"Allowed extensions: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
            ),
        )

    return original_name


def _validate_upload_content_type(content_type: str | None) -> None:
    if content_type is None:
        return

    allowed_exact_types = {"application/octet-stream", "video/mp4"}
    if content_type.startswith("audio/") or content_type in allowed_exact_types:
        return

    raise HTTPException(
        status_code=400,
        detail="Unsupported upload content type. Please upload an audio file.",
    )


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
