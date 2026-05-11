from datetime import datetime, timezone
import json
import sqlite3

from app.db.database import get_connection
from app.models.alignment import AlignedTranscript
from app.models.diarization import Diarization
from app.models.transcription import RawTranscript
from app.schemas import JobMetadata, JobResult, JobStatus, PipelineStage


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_metadata(row: sqlite3.Row) -> JobMetadata:
    return JobMetadata(
        id=row["id"],
        filename=row["filename"],
        status=row["status"],
        stage=row["stage"],
        progress_percent=row["progress_percent"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        error=row["error"],
    )


def create_job(job_id: str, filename: str, audio_path: str) -> JobMetadata:
    now = _now_iso()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO jobs (
                id, filename, audio_path, status, stage, progress_percent,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                filename,
                audio_path,
                JobStatus.QUEUED.value,
                PipelineStage.UPLOADED.value,
                0,
                now,
                now,
            ),
        )
    job = get_job(job_id)
    if job is None:
        raise RuntimeError("Job was not created")
    return job


def get_job(job_id: str) -> JobMetadata | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
    return _row_to_metadata(row) if row else None


def get_audio_path(job_id: str) -> str | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT audio_path FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
    return row["audio_path"] if row else None


def update_status(
    job_id: str,
    status: JobStatus,
    stage: PipelineStage | None = None,
    progress_percent: int | None = None,
    error: str | None = None,
) -> None:
    current = get_job(job_id)
    next_stage = stage or (current.stage if current else PipelineStage.UPLOADED)
    next_progress = (
        progress_percent
        if progress_percent is not None
        else current.progress_percent
        if current
        else 0
    )

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET status = ?, stage = ?, progress_percent = ?, error = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                status.value,
                next_stage.value,
                next_progress,
                error,
                _now_iso(),
                job_id,
            ),
        )


def save_result(job_id: str, result: JobResult) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET status = ?, stage = ?, progress_percent = ?, result_json = ?,
                updated_at = ?, error = NULL
            WHERE id = ?
            """,
            (
                JobStatus.COMPLETED.value,
                PipelineStage.COMPLETED.value,
                100,
                result.model_dump_json(),
                _now_iso(),
                job_id,
            ),
        )


def save_raw_transcript(job_id: str, transcript: RawTranscript) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET raw_transcript_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (transcript.model_dump_json(), _now_iso(), job_id),
        )


def save_raw_diarization(job_id: str, diarization: Diarization) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET raw_diarization_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (diarization.model_dump_json(), _now_iso(), job_id),
        )


def save_aligned_transcript(job_id: str, transcript: AlignedTranscript) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET aligned_transcript_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (transcript.model_dump_json(), _now_iso(), job_id),
        )


def get_raw_transcript(job_id: str) -> RawTranscript | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT raw_transcript_json FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
    if row is None or row["raw_transcript_json"] is None:
        return None
    return RawTranscript.model_validate(json.loads(row["raw_transcript_json"]))


def get_raw_diarization(job_id: str) -> Diarization | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT raw_diarization_json FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()

    if row is None or row["raw_diarization_json"] is None:
        return None

    return Diarization.model_validate(json.loads(row["raw_diarization_json"]))


def get_aligned_transcript(job_id: str) -> AlignedTranscript | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT aligned_transcript_json FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()

    if row is None or row["aligned_transcript_json"] is None:
        return None

    return AlignedTranscript.model_validate(json.loads(row["aligned_transcript_json"]))


def get_result(job_id: str) -> JobResult | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT result_json FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()

    if row is None or row["result_json"] is None:
        return None

    return JobResult.model_validate(json.loads(row["result_json"]))
