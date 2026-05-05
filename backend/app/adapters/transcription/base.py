from pathlib import Path

from app.models.transcription import RawTranscript


class TranscriptionAdapter:
    def __init__(self):
        self.model = self.load_model()

    def load_model(self):
        """Load the transcription model into memory."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def transcribe(self, audio_path: Path) -> RawTranscript:
        """Transcribe the given audio file and return a RawTranscript object."""
        raise NotImplementedError("This method should be implemented by subclasses.")
