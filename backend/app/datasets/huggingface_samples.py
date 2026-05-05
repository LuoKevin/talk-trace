from typing import Any

from pydantic import BaseModel


AMI_DATASET_REPO = "edinburghcstr/ami"
AMI_DATASET_CONFIG = "ihm"


class AmiAudioSample(BaseModel):
    """Small normalized view of one AMI Hugging Face sample.

    The original row is intentionally kept so you can inspect fields as you
    learn the dataset instead of hiding them behind a perfect abstraction.
    """

    text: str
    speaker_id: str | None
    start_seconds: float | None
    end_seconds: float | None
    audio: Any
    raw_row: dict[str, Any]


def load_ami_audio_samples(
    limit: int = 3,
    split: str = "train",
    streaming: bool = True,
) -> list[AmiAudioSample]:
    """Load a few audio samples from the AMI meeting corpus on Hugging Face.

    This helper is for exploration and test fixtures, not production pipeline
    code. Keep real user uploads and public sample datasets as separate inputs.
    """
    # TODO: Add a small CLI script that saves selected samples to local fixtures.
    # TODO: Decide which AMI microphone configuration is best for your pipeline.
    dataset = _load_dataset(
        AMI_DATASET_REPO,
        AMI_DATASET_CONFIG,
        split=split,
        streaming=streaming,
    )

    samples: list[AmiAudioSample] = []
    for row in dataset:
        samples.append(_normalize_ami_row(dict(row)))
        if len(samples) >= limit:
            break

    return samples


def _load_dataset(
    repo: str,
    config: str,
    split: str,
    streaming: bool,
) -> Any:
    from datasets import load_dataset

    return load_dataset(repo, config, split=split, streaming=streaming)


def _normalize_ami_row(row: dict[str, Any]) -> AmiAudioSample:
    return AmiAudioSample(
        text=str(_first_present(row, ["text", "transcript", "sentence"]) or ""),
        speaker_id=_optional_string(
            _first_present(row, ["speaker_id", "speaker", "speaker_label"])
        ),
        start_seconds=_optional_float(
            _first_present(row, ["begin_time", "start_time", "start_seconds", "start"])
        ),
        end_seconds=_optional_float(
            _first_present(row, ["end_time", "end_seconds", "end"])
        ),
        audio=row.get("audio"),
        raw_row=row,
    )


def _first_present(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in row:
            return row[key]
    return None


def _optional_string(value: Any) -> str | None:
    return None if value is None else str(value)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)
