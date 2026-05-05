from pathlib import Path

from app.adapters.transcription.base import TranscriptionAdapter
from app.models.transcription import RawTranscript, RawTranscriptSegment


class StubTranscriptionAdapter(TranscriptionAdapter):
    """A stub transcription adapter that returns a hardcoded transcript for testing purposes."""

    def load_model(self) -> None:
        """The stub adapter does not need a model."""
        return None

    def transcribe(self, audio_path: Path) -> RawTranscript:
        """Return a hardcoded RawTranscript object."""
        return RawTranscript(
            segments=[
                RawTranscriptSegment(
                    start_seconds=0.0,
                    end_seconds=5.0,
                    text="Hello, this is a test transcript.",
                ),
                RawTranscriptSegment(
                    start_seconds=5.0,
                    end_seconds=10.0,
                    text="This is the second segment of the transcript.",
                ),
            ]
        )
