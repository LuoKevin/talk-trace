from pathlib import Path

from app.schemas import JobResult
from app.services.alignment_service import align_transcript_to_speakers
from app.services.audio_service import normalize_audio
from app.services.diarization_service import diarize_audio
from app.services.summarization_service import summarize_meeting
from app.services.transcription_service import transcribe_audio


def process_meeting_audio(job_id: str, audio_path: Path) -> JobResult:
    """Run the TalkTrace pipeline for one uploaded meeting.

    Pipeline:
    1. Normalize audio.
    2. Transcribe speech.
    3. Diarize speakers.
    4. Align transcript segments to speakers.
    5. Generate a structured summary.
    """
    # TODO: Add per-stage status updates so the UI can show richer progress.
    # TODO: Persist intermediate artifacts for debugging and evaluation.
    # TODO: Make this function resilient to long-running model calls.
    normalized_audio_path = normalize_audio(audio_path)
    raw_transcript = transcribe_audio(normalized_audio_path)
    speaker_turns = diarize_audio(normalized_audio_path)
    speaker_transcript = align_transcript_to_speakers(
        transcript=raw_transcript,
        speaker_turns=speaker_turns,
    )
    summary = summarize_meeting(speaker_transcript)

    return JobResult(
        job_id=job_id,
        transcript=speaker_transcript,
        summary=summary,
    )
