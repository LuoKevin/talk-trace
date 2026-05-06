

from pathlib import Path

from app.models.diarization import Diarization


class DiarizationAdapter:    
    def load_model(self):
        """Load the diarization model into memory."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def diarize(self, audio_path: Path) -> Diarization:
        """Diarize the given audio file and return a list of diarization segments."""
        raise NotImplementedError("This method should be implemented by subclasses.")