from pathlib import Path

from app.schemas import PipelineStage
from app.services.pipeline_service import process_meeting_audio


def test_process_meeting_audio_returns_fake_structured_result(tmp_path: Path):
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")

    result = process_meeting_audio(job_id="job-123", audio_path=audio_path)

    assert result.job_id == "job-123"
    assert len(result.transcript) == 2
    assert result.transcript[0].speaker == "Speaker 1"
    assert result.summary.overview
    assert result.summary.action_items
    assert result.summary.decisions
    assert result.summary.unanswered_questions


def test_process_meeting_audio_reports_stage_progress(tmp_path: Path):
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")
    progress_events = []

    process_meeting_audio(
        job_id="job-123",
        audio_path=audio_path,
        progress_callback=lambda stage, progress: progress_events.append(
            (stage, progress)
        ),
    )

    assert progress_events == [
        (PipelineStage.PREPROCESSING, 15),
        (PipelineStage.TRANSCRIPTION, 35),
        (PipelineStage.DIARIZATION, 55),
        (PipelineStage.ALIGNMENT, 75),
        (PipelineStage.SUMMARIZATION, 90),
    ]


def test_process_meeting_audio_reports_raw_transcript(tmp_path: Path):
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"fake audio")
    raw_transcripts = []

    process_meeting_audio(
        job_id="job-123",
        audio_path=audio_path,
        raw_transcript_callback=raw_transcripts.append,
    )

    assert len(raw_transcripts) == 1
    assert raw_transcripts[0].segments
