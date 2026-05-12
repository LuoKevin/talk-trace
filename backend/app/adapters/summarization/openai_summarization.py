import json

from openai import OpenAI
from pydantic import ValidationError

from app.adapters.summarization.base import BaseSummarizationAdapter
from app.adapters.summarization.prompts import SUMMARIZATION_SYSTEM_PROMPT
from app.config import get_settings
from app.models.alignment import AlignedTranscript
from app.models.summarization import Summarization


class SummarizationAdapterError(Exception):
    """Raised when an LLM summarization response cannot be used safely."""


class OpenAISummarizationAdapter(BaseSummarizationAdapter):
    def __init__(self, model_id: str):
        settings = get_settings()
        if settings.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is required for OpenAI summarization")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_id = model_id

    def summarize(self, transcript: AlignedTranscript) -> Summarization:
        """Generate a structured summary from an aligned transcript."""
        formatted_transcript = format_aligned_transcript_for_prompt(transcript)
        messages = [
            {"role": "system", "content": SUMMARIZATION_SYSTEM_PROMPT},
            {"role": "user", "content": formatted_transcript},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.3,
            )
        except Exception as exc:
            raise SummarizationAdapterError("OpenAI summarization request failed") from exc

        summary_content = _extract_summary_content(response)
        summary_dict = _parse_summary_json(summary_content)
        return _validate_summary(summary_dict)


def _extract_summary_content(response) -> str:
    try:
        summary_content = response.choices[0].message.content
    except (AttributeError, IndexError) as exc:
        raise SummarizationAdapterError("OpenAI summarization response was empty") from exc

    if summary_content is None or not summary_content.strip():
        raise SummarizationAdapterError("OpenAI summarization response had no content")

    return summary_content


def _parse_summary_json(summary_content: str) -> dict:
    try:
        parsed = json.loads(summary_content)
    except json.JSONDecodeError as exc:
        raise SummarizationAdapterError(
            "OpenAI summarization response was not valid JSON"
        ) from exc

    if not isinstance(parsed, dict):
        raise SummarizationAdapterError(
            "OpenAI summarization response JSON must be an object"
        )

    return parsed


def _validate_summary(summary_dict: dict) -> Summarization:
    try:
        return Summarization.model_validate(summary_dict)
    except ValidationError as exc:
        raise SummarizationAdapterError(
            "OpenAI summarization response did not match the Summarization schema"
        ) from exc


def format_aligned_transcript_for_prompt(transcript: AlignedTranscript) -> str:
    """Convert the aligned transcript into a string format suitable for prompting."""
    lines: list[str] = []

    for segment in transcript.segments:
        start = _format_timestamp(segment.start_seconds)
        end = _format_timestamp(segment.end_seconds)

        lines.append(f"[{start}-{end}] {segment.speaker}: {segment.text}")

    return "\n".join(lines)


def _format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"
