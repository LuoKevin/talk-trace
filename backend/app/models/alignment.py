from pydantic import BaseModel


class AlignedTranscriptSegment(BaseModel):
    speaker: str
    start_seconds: float
    end_seconds: float
    text: str


class AlignedTranscript(BaseModel):
    segments: list[AlignedTranscriptSegment]
