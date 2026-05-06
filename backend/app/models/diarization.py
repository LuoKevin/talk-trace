
from pydantic import BaseModel


class SpeakerTurn(BaseModel):
    speaker: str
    start_seconds: float
    end_seconds: float

class Diarization(BaseModel):
    speaker_turns: list[SpeakerTurn]