import logging
from pathlib import Path

from app.config import get_settings
from app.models.transcription import RawTranscript


logger = logging.getLogger(__name__)


def transcribe_audio(audio_path: Path) -> RawTranscript:
    """Transcribe speech into timestamped text segments.

    This placeholder returns fake segments so the app can be used before a
    WhisperX integration exists.
    """
    # TODO: Integrate WhisperX or another transcription engine here.
    # TODO: Decide what metadata you need to keep from the model output.

    adapter_type = get_settings().transcription_adapter
    logger.info("transcription_adapter_selected adapter=%s audio_path=%s", adapter_type, audio_path)
    if adapter_type == "faster_whisper":
        from app.adapters.transcription.faster_whisper import FasterWhisperAdapter
        adapter = FasterWhisperAdapter()
    elif adapter_type == "stub":
        from app.adapters.transcription.stub import StubTranscriptionAdapter
        adapter = StubTranscriptionAdapter()
    else:
        raise ValueError(f"Unrecognized transcription adapter: {adapter_type}")

    return adapter.transcribe(audio_path)  
