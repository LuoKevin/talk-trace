from pydantic import BaseModel


class RawTranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str


class RawTranscript(BaseModel):
    segments: list[RawTranscriptSegment]
