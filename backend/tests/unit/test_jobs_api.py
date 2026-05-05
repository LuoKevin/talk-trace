from fastapi.testclient import TestClient

from app.main import app


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
    assert result_response.json()["transcript"][0]["speaker"] == "Speaker 1"


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