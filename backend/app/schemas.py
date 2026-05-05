from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobMetadata(BaseModel):
    id: str
    filename: str
    status: JobStatus
    created_at: str
    updated_at: str
    error: str | None = None


class TranscriptSegment(BaseModel):
    speaker: str
    start_seconds: float
    end_seconds: float
    text: str


class MeetingSummary(BaseModel):
    overview: str
    action_items: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    unanswered_questions: list[str] = Field(default_factory=list)


class JobResult(BaseModel):
    job_id: str
    transcript: list[TranscriptSegment]
    summary: MeetingSummary


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus
