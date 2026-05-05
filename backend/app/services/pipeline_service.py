from pathlib import Path
from typing import Callable

from app.schemas import JobResult, PipelineStage
from app.services.alignment_service import align_transcript_to_speakers
from app.services.audio_service import normalize_audio
from app.services.diarization_service import diarize_audio
from app.services.summarization_service import summarize_meeting
from app.services.transcription_service import transcribe_audio


ProgressCallback = Callable[[PipelineStage, int], None]


def process_meeting_audio(
    job_id: str,
    audio_path: Path,
    progress_callback: ProgressCallback | None = None,
) -> JobResult:
    """Run the TalkTrace pipeline for one uploaded meeting.

    Pipeline:
    1. Normalize audio.
    2. Transcribe speech.
    3. Diarize speakers.
    4. Align transcript segments to speakers.
    5. Generate a structured summary.
    """
    # TODO: Persist intermediate artifacts for debugging and evaluation.
    # TODO: Make this function resilient to long-running model calls.
    _report_progress(progress_callback, PipelineStage.PREPROCESSING, 15)
    normalized_audio_path = normalize_audio(audio_path)

    _report_progress(progress_callback, PipelineStage.TRANSCRIPTION, 35)
    raw_transcript = transcribe_audio(normalized_audio_path)

    _report_progress(progress_callback, PipelineStage.DIARIZATION, 55)
    speaker_turns = diarize_audio(normalized_audio_path)

    _report_progress(progress_callback, PipelineStage.ALIGNMENT, 75)
    speaker_transcript = align_transcript_to_speakers(
        transcript=raw_transcript,
        speaker_turns=speaker_turns,
    )

    _report_progress(progress_callback, PipelineStage.SUMMARIZATION, 90)
    summary = summarize_meeting(speaker_transcript)

    return JobResult(
        job_id=job_id,
        transcript=speaker_transcript,
        summary=summary,
    )


def _report_progress(
    progress_callback: ProgressCallback | None,
    stage: PipelineStage,
    progress_percent: int,
) -> None:
    if progress_callback is not None:
        progress_callback(stage, progress_percent)
