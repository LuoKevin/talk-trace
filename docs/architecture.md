# TalkTrace Architecture

TalkTrace is built around a staged audio intelligence pipeline:

```text
audio upload
  -> preprocessing
  -> transcription
  -> diarization
  -> alignment
  -> summarization
  -> UI display
```

Each stage has a separate service module. That separation is the main learning goal of the scaffold.

## Pipeline Stages

### 1. Audio Upload

The frontend sends a file to `POST /api/jobs/upload`. The backend stores the file under `backend/data/uploads`, creates a job row in SQLite, and starts a background task.

TODOs to study:

- Add file size limits.
- Validate audio MIME types and extensions.
- Decide whether raw uploads should be retained forever.

### 2. Preprocessing

Preprocessing prepares audio for models. Real systems often convert files to WAV, resample audio, normalize volume, and convert stereo to mono.

The placeholder lives in `backend/app/services/audio_service.py`.

### 3. Transcription

Transcription turns speech into text with timestamps.

Example output:

```json
{
  "start_seconds": 7.3,
  "end_seconds": 14.4,
  "text": "I can finish the onboarding flow."
}
```

Transcription does not reliably answer who spoke. It answers what was said and when it was said.

### 4. Diarization

Diarization detects speaker turns.

Example output:

```json
{
  "speaker": "Speaker 2",
  "start_seconds": 7.0,
  "end_seconds": 15.0
}
```

Diarization does not produce transcript text. It answers who spoke and when they spoke.

### 5. Alignment

Alignment combines transcription and diarization. It takes timestamped transcript segments and speaker time ranges, then assigns speaker labels to words or segments.

This stage can get tricky because transcript boundaries and speaker boundaries rarely match perfectly. Later versions may need to split transcript segments when speakers change mid-segment.

### 6. Summarization

Summarization converts the speaker-aware transcript into structured meeting intelligence:

- Overall summary
- Action items
- Decisions
- Unanswered questions

The placeholder lives in `backend/app/services/summarization_service.py`. A real implementation should ask an LLM for schema-conforming JSON and validate it with Pydantic.

## Why Background Processing Matters

Audio processing can take seconds or minutes. The upload request should not stay open while models run. Instead, the API creates a job immediately and the frontend polls for status.

The MVP uses FastAPI `BackgroundTasks`, which is good enough for learning. It has important limitations:

- Jobs run in the same process as the API server.
- Jobs can be lost if the server restarts.
- It does not provide retries, queues, concurrency control, or distributed workers.

Later, `backend/app/jobs/job_runner.py` can become a Celery or RQ task body. The API route should still create a job, store metadata, and enqueue work.

## Storage Boundary

SQLite code is isolated in `backend/app/storage/job_repository.py`. API routes should not contain SQL. This keeps the code structured so a Postgres-backed repository can be added later without rewriting the rest of the app.

For a stronger version, split storage into:

- job metadata table
- uploaded file artifact records
- transcript segment table
- speaker turn table
- summary table
- evaluation run table

Do that only after the fake pipeline works.
