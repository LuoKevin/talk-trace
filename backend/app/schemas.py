from enum import Enum

from pydantic import BaseModel

from app.models.alignment import AlignedTranscript
from app.models.diarization import Diarization
from app.models.transcription import RawTranscript
from app.models.summarization import Summarization


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

class JobResult(BaseModel):
    job_id: str
    transcript: AlignedTranscript
    summary: Summarization


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus


class SpeakerLabelsUpdate(BaseModel):
    speaker_labels: dict[str, str]


class SpeakerLabelsResponse(BaseModel):
    speaker_labels: dict[str, str]


class JobArtifacts(BaseModel):
    raw_transcript: RawTranscript | None
    raw_diarization: Diarization | None
    aligned_transcript: AlignedTranscript | None
    raw_summarization: Summarization | None
    speaker_labels: dict[str, str]
    result: JobResult | None
