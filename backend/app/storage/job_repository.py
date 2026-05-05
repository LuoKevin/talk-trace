from datetime import datetime, timezone
import json
import sqlite3

from app.db.database import get_connection
from app.schemas import JobMetadata, JobResult, JobStatus


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_metadata(row: sqlite3.Row) -> JobMetadata:
    return JobMetadata(
        id=row["id"],
        filename=row["filename"],
        status=row["status"],
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
                id, filename, audio_path, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (job_id, filename, audio_path, JobStatus.QUEUED.value, now, now),
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
    error: str | None = None,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET status = ?, error = ?, updated_at = ?
            WHERE id = ?
            """,
            (status.value, error, _now_iso(), job_id),
        )


def save_result(job_id: str, result: JobResult) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET status = ?, result_json = ?, updated_at = ?, error = NULL
            WHERE id = ?
            """,
            (
                JobStatus.COMPLETED.value,
                result.model_dump_json(),
                _now_iso(),
                job_id,
            ),
        )


def get_result(job_id: str) -> JobResult | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT result_json FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()

    if row is None or row["result_json"] is None:
        return None

    return JobResult.model_validate(json.loads(row["result_json"]))
