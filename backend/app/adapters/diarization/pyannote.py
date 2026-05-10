from pathlib import Path

from app.adapters.diarization.base import DiarizationAdapter
from app.config import get_settings
from app.models.diarization import Diarization, SpeakerTurn


class PyannoteDiarizationAdapter(DiarizationAdapter):
    def load_model(self):
        settings = get_settings()
        torch = _get_torch()
        pipeline_cls = _get_pipeline_class()

        pipeline = pipeline_cls.from_pretrained(
            settings.pyannote_model,
            token=settings.huggingface_token,
        )
        pipeline.to(torch.device(settings.pyannote_device))
        return pipeline

    def diarize(self, audio_path: Path) -> Diarization:
        progress_hook_cls = _get_progress_hook_class()
        audio = _load_audio_for_pyannote(audio_path)

        with progress_hook_cls() as hook:
            output = self.model(audio, hook=hook)

        annotation = _get_annotation_from_output(output)
        speaker_turns = [
            SpeakerTurn(
                speaker=speaker,
                start_seconds=turn.start,
                end_seconds=turn.end,
            )
            for turn, _, speaker in annotation.itertracks(yield_label=True)
        ]

        return Diarization(speaker_turns=speaker_turns)


def _get_annotation_from_output(output):
    """Return a pyannote Annotation from old or new diarization outputs."""
    if hasattr(output, "exclusive_speaker_diarization"):
        return output.exclusive_speaker_diarization

    if hasattr(output, "speaker_diarization"):
        return output.speaker_diarization

    return output


def _load_audio_for_pyannote(audio_path: Path) -> dict:
    # Preload audio to avoid relying on pyannote's TorchCodec-backed file decoder.
    soundfile = _get_soundfile()
    torch = _get_torch()
    samples, sample_rate = soundfile.read(audio_path)

    waveform = torch.tensor(samples, dtype=torch.float32)
    if waveform.ndim == 1:
        waveform = waveform.unsqueeze(0)
    else:
        waveform = waveform.transpose(0, 1)

    return {
        "waveform": waveform,
        "sample_rate": sample_rate,
    }


def _get_soundfile():
    import soundfile

    return soundfile


def _get_torch():
    import torch

    return torch


def _get_pipeline_class():
    from pyannote.audio import Pipeline

    return Pipeline


def _get_progress_hook_class():
    from pyannote.audio.pipelines.utils.hook import ProgressHook

    return ProgressHook
