from __future__ import annotations

from typing import Any

import requests
import streamlit as st


DEFAULT_API_BASE_URL = "http://localhost:8000"


def main() -> None:
    st.set_page_config(page_title="TalkTrace Backend Tester", layout="wide")
    st.title("TalkTrace Backend Tester")

    api_base_url = st.sidebar.text_input("FastAPI base URL", DEFAULT_API_BASE_URL).rstrip("/")
    st.sidebar.caption("Start FastAPI separately with `uvicorn app.main:app --reload`.")

    if "job_id" not in st.session_state:
        st.session_state.job_id = ""

    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a", "mp4", "flac", "ogg", "webm"],
    )

    if uploaded_file is not None:
        st.audio(uploaded_file.getvalue(), format=uploaded_file.type or "audio/wav")

        if st.button("Upload and create job", type="primary"):
            with st.spinner("Uploading audio..."):
                response = upload_audio(api_base_url, uploaded_file)
            st.session_state.job_id = response["job_id"]
            st.success(f"Created job {st.session_state.job_id}")

    st.divider()

    job_id = st.text_input("Job ID", value=st.session_state.job_id)
    st.session_state.job_id = job_id

    if not job_id:
        st.info("Upload an audio file or paste an existing job ID.")
        return

    col_a, col_b, col_c = st.columns([1, 1, 2])
    with col_a:
        refresh = st.button("Refresh job")
    with col_b:
        auto_refresh = st.checkbox("Auto-refresh", value=False)
    with col_c:
        st.caption("Auto-refresh checks the backend every 3 seconds while this page is open.")

    if auto_refresh:
        st.markdown(
            "<meta http-equiv='refresh' content='3'>",
            unsafe_allow_html=True,
        )

    try:
        job = fetch_json(api_base_url, f"/api/jobs/{job_id}")
    except requests.HTTPError as exc:
        st.error(f"Could not load job: {format_http_error(exc)}")
        return

    render_job_status(job)

    artifacts = safe_fetch_json(api_base_url, f"/api/jobs/{job_id}/artifacts")
    result = safe_fetch_json(api_base_url, f"/api/jobs/{job_id}/result")

    if artifacts is not None:
        render_speaker_labels_editor(api_base_url, job_id, artifacts)
        render_artifact_summary(artifacts)

    if result is not None:
        render_result(result)
    elif job.get("status") == "failed":
        st.error(job.get("error") or "Job failed")
    else:
        st.info("Result is not ready yet.")

    with st.expander("Raw artifacts JSON"):
        st.json(artifacts)

    if refresh:
        st.rerun()


def upload_audio(api_base_url: str, uploaded_file) -> dict[str, Any]:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }
    response = requests.post(f"{api_base_url}/api/jobs/upload", files=files, timeout=120)
    response.raise_for_status()
    return response.json()


def fetch_json(api_base_url: str, path: str) -> dict[str, Any]:
    response = requests.get(f"{api_base_url}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def safe_fetch_json(api_base_url: str, path: str) -> dict[str, Any] | None:
    try:
        return fetch_json(api_base_url, path)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in {404, 409}:
            return None
        raise


def render_job_status(job: dict[str, Any]) -> None:
    st.subheader("Job status")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Status", job["status"])
    col_b.metric("Stage", job["stage"])
    col_c.metric("Progress", f'{job["progress_percent"]}%')
    st.progress(job["progress_percent"] / 100)


def render_speaker_labels_editor(
    api_base_url: str,
    job_id: str,
    artifacts: dict[str, Any],
) -> None:
    aligned = artifacts.get("aligned_transcript") or {}
    segments = aligned.get("segments") or []
    speakers = sorted({segment["speaker"] for segment in segments})
    if not speakers:
        return

    st.subheader("Speaker names")
    current_labels = artifacts.get("speaker_labels") or {}

    with st.form("speaker-labels-form"):
        labels = {
            speaker: st.text_input(
                speaker,
                value=current_labels.get(speaker, ""),
                placeholder="Display name",
            )
            for speaker in speakers
        }
        submitted = st.form_submit_button("Save speaker names")

    if submitted:
        response = requests.put(
            f"{api_base_url}/api/jobs/{job_id}/speaker-labels",
            json={"speaker_labels": labels},
            timeout=30,
        )
        response.raise_for_status()
        st.success("Speaker names saved.")
        st.rerun()


def render_artifact_summary(artifacts: dict[str, Any]) -> None:
    st.subheader("Pipeline artifacts")
    raw_transcript = artifacts.get("raw_transcript") or {}
    raw_diarization = artifacts.get("raw_diarization") or {}
    aligned = artifacts.get("aligned_transcript") or {}

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Transcript segments", len(raw_transcript.get("segments") or []))
    col_b.metric("Speaker turns", len(raw_diarization.get("speaker_turns") or []))
    col_c.metric("Aligned segments", len(aligned.get("segments") or []))
    col_d.metric(
        "Summarization",
        "Ready" if artifacts.get("raw_summarization") else "Pending",
    )


def render_result(result: dict[str, Any]) -> None:
    st.subheader("Result")
    summary = result["summary"]
    st.markdown(f"**Main speaker:** {summary['main_speaker']}")
    st.write(summary["overview"])

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**Action items**")
        render_list(summary["action_items"])
    with col_b:
        st.markdown("**Follow-up topics**")
        render_list(summary["follow_up_topics"])
    with col_c:
        st.markdown("**Support suggestions**")
        suggestions = [
            f"{speaker}: {suggestion}"
            for speaker, speaker_suggestions in summary["supporter_suggestions"].items()
            for suggestion in speaker_suggestions
        ]
        render_list(suggestions)

    st.subheader("Transcript")
    for segment in result["transcript"]["segments"]:
        st.markdown(
            f"**{segment['speaker']}** "
            f"`{format_time(segment['start_seconds'])}-{format_time(segment['end_seconds'])}`"
        )
        st.write(segment["text"])


def render_list(items: list[str]) -> None:
    if not items:
        st.caption("None found.")
        return

    for item in items:
        st.markdown(f"- {item}")


def format_time(seconds: float) -> str:
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


def format_http_error(exc: requests.HTTPError) -> str:
    if exc.response is None:
        return str(exc)
    return f"{exc.response.status_code}: {exc.response.text}"


if __name__ == "__main__":
    main()
