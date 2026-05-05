from app.schemas import (
    JobResult,
    JobStatus,
    MeetingSummary,
    PipelineStage,
    TranscriptSegment,
)
from app.storage import job_repository


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
