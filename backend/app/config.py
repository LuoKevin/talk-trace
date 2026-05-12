from dataclasses import dataclass
import os


@dataclass(frozen=True)
class TalkTraceSettings:
    transcription_adapter: str = "stub"
    transcription_model: str = "base"
    transcription_device: str = "cpu"
    transcription_compute_type: str = "int8"
    diarization_adapter: str = "stub"
    pyannote_model: str = "pyannote/speaker-diarization-3.1"
    pyannote_device: str = "cpu"
    summarization_adapter: str = "stub"
    summarization_model: str = "gpt-4.1-mini"
    huggingface_token: str | None = None
    openai_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "TalkTraceSettings":
        return cls(
            transcription_adapter=os.getenv(
                "TALKTRACE_TRANSCRIPTION_ADAPTER",
                cls.transcription_adapter,
            ),
            transcription_model=os.getenv(
                "TALKTRACE_TRANSCRIPTION_MODEL",
                cls.transcription_model,
            ),
            transcription_device=os.getenv(
                "TALKTRACE_TRANSCRIPTION_DEVICE",
                cls.transcription_device,
            ),
            transcription_compute_type=os.getenv(
                "TALKTRACE_TRANSCRIPTION_COMPUTE_TYPE",
                cls.transcription_compute_type,
            ),
            diarization_adapter=os.getenv(
                "TALKTRACE_DIARIZATION_ADAPTER",
                cls.diarization_adapter,
            ),
            pyannote_model=os.getenv("TALKTRACE_PYANNOTE_MODEL", cls.pyannote_model),
            pyannote_device=os.getenv("TALKTRACE_PYANNOTE_DEVICE", cls.pyannote_device),
            summarization_adapter=os.getenv(
                "TALKTRACE_SUMMARIZATION_ADAPTER",
                cls.summarization_adapter,
            ),
            summarization_model=os.getenv(
                "TALKTRACE_SUMMARIZATION_MODEL",
                cls.summarization_model,
            ),
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )


def get_settings() -> TalkTraceSettings:
    return TalkTraceSettings.from_env()
