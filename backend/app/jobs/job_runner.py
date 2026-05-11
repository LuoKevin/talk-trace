import logging
from pathlib import Path

from app.schemas import JobStatus, PipelineStage
from app.services.pipeline_service import process_meeting_audio
from app.storage import job_repository


logger = logging.getLogger(__name__)


def run_job(job_id: str) -> None:
    """Run a single TalkTrace job in-process.

    This is intentionally simple for the MVP. Later, this function can become
    the body of a Celery/RQ task without changing the API routes much.
    """
    audio_path = job_repository.get_audio_path(job_id)
    if audio_path is None:
        logger.error("job_failed_missing_audio_path job_id=%s", job_id)
        job_repository.update_status(
            job_id,
            JobStatus.FAILED,
            stage=PipelineStage.FAILED,
            progress_percent=0,
            error="Audio path was not found for job",
        )
        return

    try:
        logger.info("job_started job_id=%s audio_path=%s", job_id, audio_path)
        job_repository.update_status(
            job_id,
            JobStatus.PROCESSING,
            stage=PipelineStage.UPLOADED,
            progress_percent=5,
        )
        result = process_meeting_audio(
            job_id=job_id,
            audio_path=Path(audio_path),
            progress_callback=lambda stage, progress: job_repository.update_status(
                job_id,
                JobStatus.PROCESSING,
                stage=stage,
                progress_percent=progress,
            ),
            raw_transcript_callback=lambda transcript: job_repository.save_raw_transcript(
                job_id,
                transcript,
            ),
            raw_diarization_callback=lambda diarization: job_repository.save_raw_diarization(
                job_id,
                diarization,
            ),
            aligned_transcript_callback=lambda transcript: job_repository.save_aligned_transcript(
                job_id,
                transcript,
            ),
        )
        job_repository.save_result(job_id, result)
        logger.info("job_completed job_id=%s", job_id)
    except Exception as exc:
        # TODO: Replace broad exception handling with typed errors as the
        # pipeline becomes real and each stage has known failure modes.
        logger.exception("job_failed job_id=%s error=%s", job_id, exc)
        job_repository.update_status(
            job_id,
            JobStatus.FAILED,
            stage=PipelineStage.FAILED,
            error=str(exc),
        )
