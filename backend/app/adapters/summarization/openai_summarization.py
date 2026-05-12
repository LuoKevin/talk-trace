from app.adapters.summarization.base import BaseSummarizationAdapter
from app.models.alignment import AlignedTranscript
from app.models.summarization import Summarization
from app.config import get_settings
from app.adapters.summarization.prompts import SUMMARIZATION_SYSTEM_PROMPT
from openai import OpenAI
import json


class OpenAISummarizationAdapter(BaseSummarizationAdapter):
    def __init__(self, model_id: str):
        settings = get_settings()
        if settings.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is required for OpenAI summarization")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_id = model_id

    def summarize(self, transcript: AlignedTranscript) -> Summarization:
        # Implement OpenAI summarization logic here
        formatted_transcript = format_aligned_transcript_for_prompt(transcript)
        messages = [
            {"role": "system", "content": SUMMARIZATION_SYSTEM_PROMPT},
            {"role": "user", "content": formatted_transcript},
        ]
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=0.3,
        )
        summary_content = response.choices[0].message.content
        summary_dict = json.loads(summary_content)
        return Summarization(**summary_dict)


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
