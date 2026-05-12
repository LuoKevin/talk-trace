from app.models.summarization import Summarization
from app.models.alignment import AlignedTranscript
from app.config import get_settings


def summarize_meeting(transcript: AlignedTranscript) -> Summarization:
    """Generate a structured meeting summary.

    In the real implementation, this service should call an OpenAI-compatible
    API and validate the response against `Summarization`.
    """
    # TODO: Add retry and validation behavior for malformed model responses.
    # TODO: Decide whether summaries should include citations to transcript segments.
    settings = get_settings()
    if settings.summarization_adapter == "openai":
        from app.adapters.summarization.openai_summarization import (
            OpenAISummarizationAdapter,
        )

        adapter = OpenAISummarizationAdapter(settings.summarization_model)
    elif settings.summarization_adapter == "stub":
        from app.adapters.summarization.stub import StubSummarizationAdapter

        adapter = StubSummarizationAdapter()
    else:
        raise ValueError(
            f"Unrecognized summarization adapter: {settings.summarization_adapter}"
        )

    return adapter.summarize(transcript)
