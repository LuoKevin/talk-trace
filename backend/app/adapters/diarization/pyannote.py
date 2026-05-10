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

        with progress_hook_cls() as hook:
            output = self.model(str(audio_path), hook=hook)

        speaker_turns = [
            SpeakerTurn(
                speaker=speaker,
                start_seconds=turn.start,
                end_seconds=turn.end,
            )
            for turn, _, speaker in output.itertracks(yield_label=True)
        ]

        return Diarization(speaker_turns=speaker_turns)


def _get_torch():
    import torch

    return torch


def _get_pipeline_class():
    from pyannote.audio import Pipeline

    return Pipeline


def _get_progress_hook_class():
    from pyannote.audio.pipelines.utils.hook import ProgressHook

    return ProgressHook
