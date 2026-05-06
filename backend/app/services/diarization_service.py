import os
from pathlib import Path

from app.models.diarization import Diarization

def diarize_audio(audio_path: Path) -> Diarization:
    """Detect who spoke when.

    
    Diarization does not produce text. It produces speaker-labeled time ranges
    that later need to be aligned with transcript segments.
    """
    # TODO: Integrate pyannote or another diarization system here.
    # TODO: Learn how to handle overlapping speech and unknown speaker counts.
    adapter_type = os.getenv("TALKTRACE_DIARIZATION_ADAPTER", "stub")
    if adapter_type == "pyannote":
        from app.adapters.diarization.pyannote import PyannoteDiarizationAdapter
        adapter = PyannoteDiarizationAdapter()
    elif adapter_type == "stub":
        from app.adapters.diarization.stub import StubDiarizationAdapter
        adapter = StubDiarizationAdapter()
    else:
        raise ValueError(f"Unrecognized diarization adapter: {adapter_type}")

    return adapter.diarize(audio_path)
