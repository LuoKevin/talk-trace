from pathlib import Path
import json
import os
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.adapters.summarization.openai_summarization import OpenAISummarizationAdapter
from app.config import get_settings
from app.models.alignment import AlignedTranscript, AlignedTranscriptSegment


def main() -> None:
    load_dotenv(BACKEND_ROOT / ".env")

    settings = get_settings()
    adapter = OpenAISummarizationAdapter(model_id=settings.summarization_model)
    summary = adapter.summarize(build_sample_transcript())

    print(summary.model_dump_json(indent=2))


def build_sample_transcript() -> AlignedTranscript:
    return AlignedTranscript(
        segments=[
            AlignedTranscriptSegment(
                speaker="Speaker 1",
                start_seconds=0.0,
                end_seconds=5.0,
                text="I have been feeling stretched pretty thin between work and helping my parents.",
                overlap_seconds=5.0,
                overlap_ratio=1.0,
            ),
            AlignedTranscriptSegment(
                speaker="Speaker 2",
                start_seconds=5.0,
                end_seconds=9.0,
                text="That sounds like a lot. Would it help if I checked in later this week?",
                overlap_seconds=4.0,
                overlap_ratio=1.0,
            ),
            AlignedTranscriptSegment(
                speaker="Speaker 1",
                start_seconds=9.0,
                end_seconds=14.0,
                text="Yeah, a check-in on Friday would help. I also need to decide whether to take Monday off.",
                overlap_seconds=5.0,
                overlap_ratio=1.0,
            ),
        ]
    )


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), _clean_env_value(value.strip()))


def _clean_env_value(value: str) -> str:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


if __name__ == "__main__":
    main()
