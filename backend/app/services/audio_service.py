from pathlib import Path


def normalize_audio(input_path: Path) -> Path:
    """Prepare an uploaded audio file for transcription and diarization.

    Future implementation ideas:
    - Convert all inputs to WAV.
    - Resample to the rate required by the transcription/diarization models.
    - Convert stereo to mono if the model expects mono.
    - Store normalized files separately from raw uploads.
    """
    # TODO: Use ffmpeg or a Python audio library to create a normalized copy.
    return input_path
