from pathlib import Path

from app.adapters.transcription.base import TranscriptionAdapter
from app.models.transcription import RawTranscript, RawTranscriptSegment
from faster_whisper import WhisperModel

MODEL_SIZE = "base"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"


class FasterWhisperAdapter(TranscriptionAdapter):
    def __init__(self):
        self.model = self.load_model()

    def load_model(self):
        """Load the transcription model into memory."""
        return WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

    def transcribe(self, audio_path: Path) -> RawTranscript:
        """Transcribe the given audio file and return a RawTranscript object."""
        segments, _ = self.model.transcribe(str(audio_path))
        return RawTranscript(
            segments=[
                RawTranscriptSegment(
                    start_seconds=segment.start,
                    end_seconds=segment.end,
                    text=segment.text,
                )
                for segment in segments
            ]
        )
