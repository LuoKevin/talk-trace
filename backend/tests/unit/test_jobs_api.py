from fastapi.testclient import TestClient

from app.main import app
from app.storage import job_repository


def test_upload_status_and_result_endpoints(isolated_storage):
    client = TestClient(app)

    upload_response = client.post(
        "/api/jobs/upload",
        files={"file": ("meeting.wav", b"fake audio", "audio/wav")},
    )

    assert upload_response.status_code == 200
    job_id = upload_response.json()["job_id"]

    status_response = client.get(f"/api/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert status_response.json()["stage"] == "completed"
    assert status_response.json()["progress_percent"] == 100

    result_response = client.get(f"/api/jobs/{job_id}/result")
    assert result_response.status_code == 200
    assert result_response.json()["transcript"]["segments"][0]["speaker"] == "Speaker 1"
    assert result_response.json()["summary"]["main_speaker"] == "Speaker 1"

    raw_transcript = job_repository.get_raw_transcript(job_id)
    assert raw_transcript is not None
    assert raw_transcript.segments

    raw_diarization = job_repository.get_raw_diarization(job_id)
    assert raw_diarization is not None
    assert raw_diarization.speaker_turns

    aligned_transcript = job_repository.get_aligned_transcript(job_id)
    assert aligned_transcript is not None
    assert aligned_transcript.segments

    raw_summarization = job_repository.get_raw_summarization(job_id)
    assert raw_summarization is not None
    assert raw_summarization.supporter_suggestions


def test_job_artifacts_endpoint_returns_intermediate_outputs(isolated_storage):
    client = TestClient(app)

    upload_response = client.post(
        "/api/jobs/upload",
        files={"file": ("meeting.wav", b"fake audio", "audio/wav")},
    )

    assert upload_response.status_code == 200
    job_id = upload_response.json()["job_id"]

    artifacts_response = client.get(f"/api/jobs/{job_id}/artifacts")

    assert artifacts_response.status_code == 200
    artifacts = artifacts_response.json()
    assert artifacts["raw_transcript"]["segments"]
    assert artifacts["raw_diarization"]["speaker_turns"]
    assert artifacts["aligned_transcript"]["segments"]
    assert artifacts["raw_summarization"]["supporter_suggestions"]
    assert artifacts["result"]["job_id"] == job_id
    assert artifacts["result"]["summary"]["supporter_suggestions"]


def test_speaker_labels_endpoint_updates_result_display_names(isolated_storage):
    client = TestClient(app)

    upload_response = client.post(
        "/api/jobs/upload",
        files={"file": ("meeting.wav", b"fake audio", "audio/wav")},
    )

    assert upload_response.status_code == 200
    job_id = upload_response.json()["job_id"]

    label_response = client.put(
        f"/api/jobs/{job_id}/speaker-labels",
        json={"speaker_labels": {"Speaker 1": "Kevin", " ": "Ignored"}},
    )

    assert label_response.status_code == 200
    assert label_response.json()["speaker_labels"] == {"Speaker 1": "Kevin"}

    result_response = client.get(f"/api/jobs/{job_id}/result")
    assert result_response.status_code == 200
    result = result_response.json()
    assert result["transcript"]["segments"][0]["speaker"] == "Kevin"
    assert result["summary"]["main_speaker"] == "Kevin"
    assert "Kevin" in result["summary"]["supporter_suggestions"]

    artifacts_response = client.get(f"/api/jobs/{job_id}/artifacts")
    assert artifacts_response.status_code == 200
    artifacts = artifacts_response.json()
    assert artifacts["speaker_labels"] == {"Speaker 1": "Kevin"}
    assert artifacts["aligned_transcript"]["segments"][0]["speaker"] == "Speaker 1"


def test_speaker_labels_endpoint_returns_404_for_missing_job(isolated_storage):
    client = TestClient(app)

    response = client.put(
        "/api/jobs/not-a-real-job/speaker-labels",
        json={"speaker_labels": {"Speaker 1": "Kevin"}},
    )

    assert response.status_code == 404


def test_missing_job_returns_404(isolated_storage):
    client = TestClient(app)

    response = client.get("/api/jobs/not-a-real-job")

    assert response.status_code == 404


def test_upload_rejects_non_audio_extension(isolated_storage):
    client = TestClient(app)

    response = client.post(
        "/api/jobs/upload",
        files={"file": ("notes.txt", b"not audio", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported audio file extension" in response.json()["detail"]


def test_upload_rejects_non_audio_content_type(isolated_storage):
    client = TestClient(app)

    response = client.post(
        "/api/jobs/upload",
        files={"file": ("meeting.wav", b"not audio", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported upload content type. Please upload an audio file."


def test_upload_rejects_files_over_mvp_size_limit(isolated_storage, monkeypatch):
    from app.api import jobs

    monkeypatch.setattr(jobs, "MAX_UPLOAD_BYTES", 4)
    client = TestClient(app)

    response = client.post(
        "/api/jobs/upload",
        files={"file": ("meeting.wav", b"too large", "audio/wav")},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Audio file is too large for the MVP upload limit"

def test_upload_rejects_empty_files(isolated_storage, monkeypatch):
    from app.api import jobs

    monkeypatch.setattr(jobs, "MAX_UPLOAD_BYTES", 10)
    client = TestClient(app)

    response = client.post(
        "/api/jobs/upload",
        files={"file": ("meeting.wav", b"", "audio/wav")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded audio file is empty"
