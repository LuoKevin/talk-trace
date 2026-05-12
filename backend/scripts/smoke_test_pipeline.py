from pathlib import Path
import json
import os
import sys
from uuid import uuid4


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.models.alignment import AlignedTranscript
from app.models.diarization import Diarization
from app.models.summarization import Summarization
from app.models.transcription import RawTranscript
from app.schemas import PipelineStage
from app.services.pipeline_service import process_meeting_audio


def main() -> None:
    load_dotenv(BACKEND_ROOT / ".env")

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/smoke_test_pipeline.py /path/to/audio.wav")

    audio_path = Path(sys.argv[1]).expanduser().resolve()
    if not audio_path.exists():
        raise SystemExit(f"Audio file not found: {audio_path}")

    artifacts: dict[str, object] = {
        "progress": [],
        "raw_transcript": None,
        "raw_diarization": None,
        "aligned_transcript": None,
        "raw_summarization": None,
    }

    result = process_meeting_audio(
        job_id=f"smoke-{uuid4()}",
        audio_path=audio_path,
        progress_callback=lambda stage, progress: artifacts["progress"].append(
            {"stage": stage.value if isinstance(stage, PipelineStage) else stage, "progress": progress}
        ),
        raw_transcript_callback=lambda transcript: _set_artifact(
            artifacts,
            "raw_transcript",
            transcript,
        ),
        raw_diarization_callback=lambda diarization: _set_artifact(
            artifacts,
            "raw_diarization",
            diarization,
        ),
        aligned_transcript_callback=lambda transcript: _set_artifact(
            artifacts,
            "aligned_transcript",
            transcript,
        ),
        summarization_callback=lambda summary: _set_artifact(
            artifacts,
            "raw_summarization",
            summary,
        ),
    )

    report = {
        **artifacts,
        "result": result,
    }
    print(json.dumps(_to_jsonable(report), indent=2))


def _set_artifact(artifacts: dict[str, object], key: str, value: object) -> None:
    artifacts[key] = value


def _to_jsonable(value: object) -> object:
    if isinstance(value, (RawTranscript, Diarization, AlignedTranscript, Summarization)):
        return value.model_dump()

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]

    return value


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
