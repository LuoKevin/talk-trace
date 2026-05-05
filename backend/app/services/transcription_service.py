from pathlib import Path

from pydantic import BaseModel


class RawTranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str


def transcribe_audio(audio_path: Path) -> list[RawTranscriptSegment]:
    """Transcribe speech into timestamped text segments.

    This placeholder returns fake segments so the app can be used before a
    WhisperX integration exists.
    """
    # TODO: Integrate WhisperX or another transcription engine here.
    # TODO: Decide what metadata you need to keep from the model output.
    return [
        RawTranscriptSegment(
            start_seconds=0.0,
            end_seconds=7.2,
            text="Let's review the launch plan and confirm who owns each next step.",
        ),
        RawTranscriptSegment(
            start_seconds=7.3,
            end_seconds=14.4,
            text="I can finish the onboarding flow, but I need the final copy by Friday.",
        ),
        RawTranscriptSegment(
            start_seconds=14.5,
            end_seconds=22.0,
            text="We decided to keep the MVP focused on uploads, processing status, and summaries.",
        ),
    ]
