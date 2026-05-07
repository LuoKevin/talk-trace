from pathlib import Path

import pytest

from app.adapters.diarization.pyannote import PyannoteDiarizationAdapter
from app.adapters.diarization import pyannote
from app.services.diarization_service import diarize_audio


def test_diarize_audio_uses_stub_adapter_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv("TALKTRACE_DIARIZATION_ADAPTER", raising=False)
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")

    diarization = diarize_audio(audio_path)

    assert len(diarization.speaker_turns) == 1
    assert diarization.speaker_turns[0].speaker == "Speaker 1"
    assert diarization.speaker_turns[0].start_seconds == 0.0
    assert diarization.speaker_turns[0].end_seconds == 3600.0


def test_unrecognized_diarization_adapter_raises_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("TALKTRACE_DIARIZATION_ADAPTER", "unknown_adapter")
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")

    with pytest.raises(
        ValueError,
        match="Unrecognized diarization adapter: unknown_adapter",
    ):
        diarize_audio(audio_path)

class FakeTurn:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end


class FakeAnnotation:
    def itertracks(self, yield_label: bool):
        return iter(
            [
                (FakeTurn(0.0, 2.5), "track-1", "SPEAKER_00"),
                (FakeTurn(2.5, 5.0), "track-2", "SPEAKER_01"),
            ]
        )


class FakePyannotePipeline:
    def __init__(self):
        self.device = None
        self.calls = []

    def to(self, device):
        self.device = device
        return self

    def __call__(self, audio_path: str, hook=None):
        self.calls.append((audio_path, hook))
        return FakeAnnotation()


class FakeTorch:
    @staticmethod
    def device(name: str):
        return name


class FakeProgressHook:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_pyannote_adapter_converts_output_to_diarization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    fake_pipeline = FakePyannotePipeline()
    captured = {}

    def fake_from_pretrained(model_name: str, token: str | None):
        captured["model_name"] = model_name
        captured["token"] = token
        return fake_pipeline

    monkeypatch.setenv("TALKTRACE_PYANNOTE_MODEL", "fake-pyannote-model")
    monkeypatch.setenv("HUGGINGFACE_TOKEN", "fake-token")
    monkeypatch.setattr(pyannote, "_get_torch", lambda: FakeTorch)
    monkeypatch.setattr(
        pyannote,
        "_get_pipeline_class",
        lambda: type(
            "FakePipelineClass",
            (),
            {"from_pretrained": staticmethod(fake_from_pretrained)},
        ),
    )
    monkeypatch.setattr(pyannote, "_get_progress_hook_class", lambda: FakeProgressHook)

    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")

    diarization = PyannoteDiarizationAdapter().diarize(audio_path)

    assert captured == {
        "model_name": "fake-pyannote-model",
        "token": "fake-token",
    }
    assert fake_pipeline.calls[0][0] == str(audio_path)
    assert len(diarization.speaker_turns) == 2
    assert diarization.speaker_turns[0].speaker == "SPEAKER_00"
    assert diarization.speaker_turns[0].start_seconds == 0.0
    assert diarization.speaker_turns[0].end_seconds == 2.5
    assert diarization.speaker_turns[1].speaker == "SPEAKER_01"
