from enum import Enum

from pydantic import BaseModel, Field

from app.models.alignment import AlignedTranscript
from app.models.diarization import Diarization
from app.models.transcription import RawTranscript


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStage(str, Enum):
    UPLOADED = "uploaded"
    PREPROCESSING = "preprocessing"
    TRANSCRIPTION = "transcription"
    DIARIZATION = "diarization"
    ALIGNMENT = "alignment"
    SUMMARIZATION = "summarization"
    COMPLETED = "completed"
    FAILED = "failed"


class JobMetadata(BaseModel):
    id: str
    filename: str
    status: JobStatus
    stage: PipelineStage
    progress_percent: int
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

class JobArtifacts(BaseModel):
    raw_transcript: RawTranscript | None
    raw_diarization: Diarization | None
    aligned_transcript: AlignedTranscript | None
    result: JobResult | None
