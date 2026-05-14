from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from app.db.database import UPLOAD_DIR
from app.jobs.job_runner import run_job
from app.models.alignment import AlignedTranscript
from app.models.summarization import Summarization
from app.schemas import (
    JobArtifacts,
    JobMetadata,
    JobResult,
    SpeakerLabelsResponse,
    SpeakerLabelsUpdate,
    UploadResponse,
)
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
    speaker_labels = job_repository.get_speaker_labels(job_id)
    result = job_repository.get_result(job_id)
    return JobArtifacts(
        raw_transcript=transcript,
        raw_diarization=diarization,
        aligned_transcript=aligned,
        raw_summarization=summarization,
        speaker_labels=speaker_labels,
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

    return _apply_speaker_labels_to_result(
        result,
        job_repository.get_speaker_labels(job_id),
    )


@router.put("/{job_id}/speaker-labels", response_model=SpeakerLabelsResponse)
def update_speaker_labels(
    job_id: str,
    payload: SpeakerLabelsUpdate,
) -> SpeakerLabelsResponse:
    job = job_repository.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    speaker_labels = _clean_speaker_labels(payload.speaker_labels)
    job_repository.save_speaker_labels(job_id, speaker_labels)
    return SpeakerLabelsResponse(speaker_labels=speaker_labels)


def _clean_speaker_labels(speaker_labels: dict[str, str]) -> dict[str, str]:
    cleaned = {
        original.strip(): label.strip()
        for original, label in speaker_labels.items()
        if original.strip() and label.strip()
    }
    return cleaned


def _apply_speaker_labels_to_result(
    result: JobResult,
    speaker_labels: dict[str, str],
) -> JobResult:
    if not speaker_labels:
        return result

    return result.model_copy(
        update={
            "transcript": _apply_speaker_labels_to_transcript(
                result.transcript,
                speaker_labels,
            ),
            "summary": _apply_speaker_labels_to_summary(
                result.summary,
                speaker_labels,
            ),
        },
        deep=True,
    )


def _apply_speaker_labels_to_transcript(
    transcript: AlignedTranscript,
    speaker_labels: dict[str, str],
) -> AlignedTranscript:
    return transcript.model_copy(
        update={
            "segments": [
                segment.model_copy(
                    update={"speaker": speaker_labels.get(segment.speaker, segment.speaker)}
                )
                for segment in transcript.segments
            ]
        },
        deep=True,
    )


def _apply_speaker_labels_to_summary(
    summary: Summarization,
    speaker_labels: dict[str, str],
) -> Summarization:
    return summary.model_copy(
        update={
            "main_speaker": speaker_labels.get(summary.main_speaker, summary.main_speaker),
            "supporter_suggestions": {
                speaker_labels.get(speaker, speaker): suggestions
                for speaker, suggestions in summary.supporter_suggestions.items()
            },
        },
        deep=True,
    )
