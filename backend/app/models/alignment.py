from pydantic import BaseModel


class AlignedTranscriptSegment(BaseModel):
    speaker: str
    start_seconds: float
    end_seconds: float
    text: str
    overlap_seconds: float = 0.0
    overlap_ratio: float = 0.0


class AlignedTranscript(BaseModel):
    segments: list[AlignedTranscriptSegment]
