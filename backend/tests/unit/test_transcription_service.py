import pytest

from app.services.transcription_service import transcribe_audio
from app.adapters.transcription.faster_whisper import FasterWhisperAdapter
from app.adapters.transcription import faster_whisper


def test_transcribe_audio_with_stub_adapter_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("TALKTRACE_TRANSCRIPTION_ADAPTER", raising=False)
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")

    transcript = transcribe_audio(audio_path)

    assert len(transcript.segments) == 2
    assert transcript.segments[0].start_seconds == 0.0
    assert transcript.segments[0].end_seconds == 5.0
    assert transcript.segments[0].text == "Hello, this is a test transcript."


class FakeSegment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


class FakeWhisperModel:
    def __init__(self, model_size, device, compute_type):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio_path):
        return (
            [
                FakeSegment(0.0, 2.5, "Hello world."),
                FakeSegment(2.5, 5.0, "This is a test."),
            ],
            None,
        )


def test_faster_whisper_adapter_converts_segments(monkeypatch, tmp_path):
    monkeypatch.setattr(faster_whisper, "WhisperModel", FakeWhisperModel)

    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")

    adapter = FasterWhisperAdapter()
    transcript = adapter.transcribe(audio_path)

    assert len(transcript.segments) == 2
    assert transcript.segments[0].start_seconds == 0.0
    assert transcript.segments[0].end_seconds == 2.5
    assert transcript.segments[0].text == "Hello world."
    assert transcript.segments[1].start_seconds == 2.5
    assert transcript.segments[1].end_seconds == 5.0
    assert transcript.segments[1].text == "This is a test."


def test_unrecognized_adapter_raises_error(monkeypatch, tmp_path):
    monkeypatch.setenv("TALKTRACE_TRANSCRIPTION_ADAPTER", "unknown_adapter")
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")

    with pytest.raises(
        ValueError, match="Unrecognized transcription adapter: unknown_adapter"
    ):
        transcribe_audio(audio_path)
