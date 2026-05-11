from app.schemas import (
    JobResult,
    JobStatus,
    MeetingSummary,
    PipelineStage,
    TranscriptSegment,
)
from app.storage import job_repository
from app.models.diarization import Diarization, SpeakerTurn
from app.models.transcription import RawTranscript, RawTranscriptSegment


def test_job_repository_persists_metadata_and_result(isolated_storage):
    created = job_repository.create_job(
        job_id="job-abc",
        filename="meeting.wav",
        audio_path=str(isolated_storage / "uploads" / "meeting.wav"),
    )

    assert created.status == JobStatus.QUEUED
    assert created.stage == PipelineStage.UPLOADED
    assert created.progress_percent == 0
    assert job_repository.get_audio_path("job-abc").endswith("meeting.wav")

    job_repository.update_status(
        "job-abc",
        JobStatus.PROCESSING,
        stage=PipelineStage.TRANSCRIPTION,
        progress_percent=35,
    )
    processing = job_repository.get_job("job-abc")
    assert processing is not None
    assert processing.status == JobStatus.PROCESSING
    assert processing.stage == PipelineStage.TRANSCRIPTION
    assert processing.progress_percent == 35

    raw_transcript = RawTranscript(
        segments=[
            RawTranscriptSegment(
                start_seconds=0.0,
                end_seconds=1.0,
                text="Hello",
            )
        ]
    )
    job_repository.save_raw_transcript("job-abc", raw_transcript)
    assert job_repository.get_raw_transcript("job-abc") == raw_transcript

    raw_diarization = Diarization(
        speaker_turns=[
            SpeakerTurn(
                speaker="Speaker 1",
                start_seconds=0.0,
                end_seconds=1.0,
            )
        ]
    )
    job_repository.save_raw_diarization("job-abc", raw_diarization)
    assert job_repository.get_raw_diarization("job-abc") == raw_diarization

    result = JobResult(
        job_id="job-abc",
        transcript=[
            TranscriptSegment(
                speaker="Speaker 1",
                start_seconds=0.0,
                end_seconds=1.0,
                text="Hello",
            )
        ],
        summary=MeetingSummary(
            overview="Short meeting",
            action_items=["Follow up"],
            decisions=[],
            unanswered_questions=[],
        ),
    )
    job_repository.save_result("job-abc", result)

    completed = job_repository.get_job("job-abc")
    loaded_result = job_repository.get_result("job-abc")

    assert completed is not None
    assert completed.status == JobStatus.COMPLETED
    assert completed.stage == PipelineStage.COMPLETED
    assert completed.progress_percent == 100
    assert loaded_result == result
