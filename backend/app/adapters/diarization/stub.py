from app.models.diarization import Diarization, SpeakerTurn


class StubDiarizationAdapter:
    def load_model(self):
        """No model to load for the stub adapter."""
        pass

    def diarize(self, audio_path: str) -> Diarization:
        """Return a hardcoded list of speaker turns for testing purposes."""
        return Diarization(
            speaker_turns=[
                SpeakerTurn(speaker="Speaker 1", start_seconds=0.0, end_seconds=3600.0)
            ]
        )
