import logging
from pathlib import Path
from typing import Callable

from app.models.alignment import AlignedTranscript
from app.models.diarization import Diarization
from app.models.transcription import RawTranscript
from app.schemas import JobResult, PipelineStage, TranscriptSegment
from app.services.alignment_service import align_transcript_to_speakers
from app.services.audio_service import normalize_audio
from app.services.diarization_service import diarize_audio
from app.services.summarization_service import summarize_meeting
from app.services.transcription_service import transcribe_audio


ProgressCallback = Callable[[PipelineStage, int], None]
RawTranscriptCallback = Callable[[RawTranscript], None]
RawDiarizationCallback = Callable[[Diarization], None]
AlignedTranscriptCallback = Callable[[AlignedTranscript], None]

logger = logging.getLogger(__name__)


def process_meeting_audio(
    job_id: str,
    audio_path: Path,
    progress_callback: ProgressCallback | None = None,
    raw_transcript_callback: RawTranscriptCallback | None = None,
    raw_diarization_callback: RawDiarizationCallback | None = None,
    aligned_transcript_callback: AlignedTranscriptCallback | None = None,
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
    logger.info("pipeline_started job_id=%s audio_path=%s", job_id, audio_path)

    logger.info("pipeline_stage_started job_id=%s stage=%s", job_id, PipelineStage.PREPROCESSING)
    _report_progress(progress_callback, PipelineStage.PREPROCESSING, 15)
    normalized_audio_path = normalize_audio(audio_path)
    logger.info("pipeline_stage_completed job_id=%s stage=%s", job_id, PipelineStage.PREPROCESSING)

    logger.info("pipeline_stage_started job_id=%s stage=%s", job_id, PipelineStage.TRANSCRIPTION)
    _report_progress(progress_callback, PipelineStage.TRANSCRIPTION, 35)
    raw_transcript = transcribe_audio(normalized_audio_path)
    if raw_transcript_callback is not None:
        raw_transcript_callback(raw_transcript)
    logger.info(
        "pipeline_stage_completed job_id=%s stage=%s segment_count=%s",
        job_id,
        PipelineStage.TRANSCRIPTION,
        len(raw_transcript.segments),
    )

    logger.info("pipeline_stage_started job_id=%s stage=%s", job_id, PipelineStage.DIARIZATION)
    _report_progress(progress_callback, PipelineStage.DIARIZATION, 55)
    diarization = diarize_audio(normalized_audio_path)
    if raw_diarization_callback is not None:
        raw_diarization_callback(diarization)
    logger.info(
        "pipeline_stage_completed job_id=%s stage=%s speaker_turn_count=%s",
        job_id,
        PipelineStage.DIARIZATION,
        len(diarization.speaker_turns),
    )

    logger.info("pipeline_stage_started job_id=%s stage=%s", job_id, PipelineStage.ALIGNMENT)
    _report_progress(progress_callback, PipelineStage.ALIGNMENT, 75)
    aligned_transcript = align_transcript_to_speakers(
        transcript=raw_transcript,
        diarization=diarization,
    )
    if aligned_transcript_callback is not None:
        aligned_transcript_callback(aligned_transcript)
    speaker_transcript = [
        TranscriptSegment(**segment.model_dump())
        for segment in aligned_transcript.segments
    ]
    logger.info(
        "pipeline_stage_completed job_id=%s stage=%s aligned_segment_count=%s",
        job_id,
        PipelineStage.ALIGNMENT,
        len(aligned_transcript.segments),
    )

    logger.info("pipeline_stage_started job_id=%s stage=%s", job_id, PipelineStage.SUMMARIZATION)
    _report_progress(progress_callback, PipelineStage.SUMMARIZATION, 90)
    summary = summarize_meeting(speaker_transcript)
    logger.info("pipeline_stage_completed job_id=%s stage=%s", job_id, PipelineStage.SUMMARIZATION)
    logger.info("pipeline_completed job_id=%s", job_id)

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
