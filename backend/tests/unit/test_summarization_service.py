import json

import pytest

from app.adapters.summarization.openai_summarization import (
    SummarizationAdapterError,
    format_aligned_transcript_for_prompt,
)
from app.models.alignment import AlignedTranscript, AlignedTranscriptSegment
from app.services.summarization_service import summarize_meeting


DEFAULT_RESPONSE = object()


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
    assert (
        "[00:00-00:02] Speaker 1: I could use a check-in next week."
        in fake_client.messages[1]["content"]
    )
    assert summary.main_speaker == "Speaker 1"
    assert summary.supporter_suggestions == {
        "Speaker 1": ["Check in next week."],
    }


def test_openai_summarization_adapter_requires_api_key(monkeypatch):
    monkeypatch.setenv("TALKTRACE_SUMMARIZATION_ADAPTER", "openai")
    monkeypatch.setenv("TALKTRACE_SUMMARIZATION_MODEL", "test-summary-model")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        summarize_meeting(_aligned_transcript())


def test_openai_summarization_adapter_rejects_empty_response(monkeypatch):
    _configure_openai_adapter(monkeypatch, FakeOpenAIClient(response_content=None))

    with pytest.raises(
        SummarizationAdapterError,
        match="OpenAI summarization response had no content",
    ):
        summarize_meeting(_aligned_transcript())


def test_openai_summarization_adapter_rejects_invalid_json(monkeypatch):
    _configure_openai_adapter(monkeypatch, FakeOpenAIClient(response_content="not json"))

    with pytest.raises(
        SummarizationAdapterError,
        match="OpenAI summarization response was not valid JSON",
    ):
        summarize_meeting(_aligned_transcript())


def test_openai_summarization_adapter_rejects_missing_required_fields(monkeypatch):
    _configure_openai_adapter(
        monkeypatch,
        FakeOpenAIClient(response_content={"overview": "Too little structure."}),
    )

    with pytest.raises(
        SummarizationAdapterError,
        match="OpenAI summarization response did not match",
    ):
        summarize_meeting(_aligned_transcript())


def test_openai_summarization_adapter_wraps_client_errors(monkeypatch):
    _configure_openai_adapter(
        monkeypatch,
        FakeOpenAIClient(request_error=RuntimeError("network failed")),
    )

    with pytest.raises(
        SummarizationAdapterError,
        match="OpenAI summarization request failed",
    ):
        summarize_meeting(_aligned_transcript())


def test_format_aligned_transcript_for_prompt_includes_timestamps_and_speakers():
    formatted = format_aligned_transcript_for_prompt(_aligned_transcript())

    assert formatted == "[00:00-00:02] Speaker 1: I could use a check-in next week."


def _configure_openai_adapter(monkeypatch, fake_client):
    from app.adapters.summarization import openai_summarization

    monkeypatch.setattr(openai_summarization, "OpenAI", lambda api_key: fake_client)
    monkeypatch.setenv("TALKTRACE_SUMMARIZATION_ADAPTER", "openai")
    monkeypatch.setenv("TALKTRACE_SUMMARIZATION_MODEL", "test-summary-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


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
    def __init__(self, response_content=DEFAULT_RESPONSE, request_error=None):
        self.chat = FakeChat(self)
        self.model = ""
        self.messages = []
        self.response_content = response_content
        self.request_error = request_error


class FakeChat:
    def __init__(self, client: FakeOpenAIClient):
        self.completions = FakeCompletions(client)


class FakeCompletions:
    def __init__(self, client: FakeOpenAIClient):
        self.client = client

    def create(self, model, messages, temperature):
        if self.client.request_error is not None:
            raise self.client.request_error

        self.client.model = model
        self.client.messages = messages
        response_content = self.client.response_content
        if response_content is DEFAULT_RESPONSE:
            return FakeResponse(_valid_summary())
        if response_content is None:
            return FakeResponse(None)

        return FakeResponse(response_content)


def _valid_summary() -> dict:
    return {
        "main_speaker": "Speaker 1",
        "overview": "Speaker 1 asked for support next week.",
        "action_items": ["Check in with Speaker 1 next week."],
        "follow_up_topics": ["How Speaker 1 is doing next week."],
        "supporter_suggestions": {
            "Speaker 1": ["Check in next week."],
        },
    }


class FakeResponse:
    def __init__(self, response_content):
        self.choices = [FakeChoice(response_content)]


class FakeChoice:
    def __init__(self, response_content):
        self.message = FakeMessage(response_content)


class FakeMessage:
    def __init__(self, response_content):
        if response_content is None:
            self.content = None
        elif isinstance(response_content, dict):
            self.content = json.dumps(response_content)
        else:
            self.content = response_content
