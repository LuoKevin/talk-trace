from pathlib import Path

from pydantic import BaseModel


class SpeakerTurn(BaseModel):
    speaker: str
    start_seconds: float
    end_seconds: float


def diarize_audio(audio_path: Path) -> list[SpeakerTurn]:
    """Detect who spoke when.

    Diarization does not produce text. It produces speaker-labeled time ranges
    that later need to be aligned with transcript segments.
    """
    # TODO: Integrate pyannote or another diarization system here.
    # TODO: Learn how to handle overlapping speech and unknown speaker counts.
    return [
        SpeakerTurn(speaker="Speaker 1", start_seconds=0.0, end_seconds=7.2),
        SpeakerTurn(speaker="Speaker 2", start_seconds=7.3, end_seconds=14.4),
        SpeakerTurn(speaker="Speaker 1", start_seconds=14.5, end_seconds=22.0),
    ]
