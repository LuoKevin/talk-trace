import json

import pytest

from app.models.alignment import AlignedTranscript, AlignedTranscriptSegment
from app.services.summarization_service import summarize_meeting


def test_summarize_meeting_uses_stub_adapter_by_default(monkeypatch):
    monkeypatch.delenv("TALKTRACE_SUMMARIZATION_ADAPTER", raising=False)

    summary = summarize_meeting(_aligned_transcript())

    assert summary.main_speaker == "Speaker 1"
    assert summary.overview
    assert summary.action_items
    assert summary.follow_up_topics
    assert summary.supporter_suggestions


def test_summarize_meeting_with_unknown_adapter_raises_error(monkeypatch):
    monkeypatch.setenv("TALKTRACE_SUMMARIZATION_ADAPTER", "unknown_adapter")

    with pytest.raises(
        ValueError, match="Unrecognized summarization adapter: unknown_adapter"
    ):
        summarize_meeting(_aligned_transcript())


def test_summarize_meeting_with_openai_adapter_uses_configured_model(monkeypatch):
    from app.adapters.summarization import openai_summarization

    fake_client = FakeOpenAIClient()
    monkeypatch.setattr(openai_summarization, "OpenAI", lambda api_key: fake_client)
    monkeypatch.setenv("TALKTRACE_SUMMARIZATION_ADAPTER", "openai")
    monkeypatch.setenv("TALKTRACE_SUMMARIZATION_MODEL", "test-summary-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    summary = summarize_meeting(_aligned_transcript())

    assert fake_client.model == "test-summary-model"
    assert fake_client.messages[0]["role"] == "system"
    assert "[00:00-00:02] Speaker 1: I could use a check-in next week." in fake_client.messages[1]["content"]
    assert summary.main_speaker == "Speaker 1"
    assert summary.supporter_suggestions == {
        "Speaker 1": ["Check in next week."],
    }


def _aligned_transcript() -> AlignedTranscript:
    return AlignedTranscript(
        segments=[
            AlignedTranscriptSegment(
                speaker="Speaker 1",
                start_seconds=0.0,
                end_seconds=2.0,
                text="I could use a check-in next week.",
                overlap_seconds=2.0,
                overlap_ratio=1.0,
            )
        ]
    )


class FakeOpenAIClient:
    def __init__(self):
        self.chat = FakeChat(self)
        self.model = ""
        self.messages = []


class FakeChat:
    def __init__(self, client: FakeOpenAIClient):
        self.completions = FakeCompletions(client)


class FakeCompletions:
    def __init__(self, client: FakeOpenAIClient):
        self.client = client

    def create(self, model, messages, temperature):
        self.client.model = model
        self.client.messages = messages
        return FakeResponse(
            {
                "main_speaker": "Speaker 1",
                "overview": "Speaker 1 asked for support next week.",
                "action_items": ["Check in with Speaker 1 next week."],
                "follow_up_topics": ["How Speaker 1 is doing next week."],
                "supporter_suggestions": {
                    "Speaker 1": ["Check in next week."],
                },
            }
        )


class FakeResponse:
    def __init__(self, summary):
        self.choices = [FakeChoice(summary)]


class FakeChoice:
    def __init__(self, summary):
        self.message = FakeMessage(summary)


class FakeMessage:
    def __init__(self, summary):
        self.content = json.dumps(summary)
