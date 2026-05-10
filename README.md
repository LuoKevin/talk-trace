# TalkTrace

TalkTrace is an AI meeting intelligence project. The goal is to learn how an AI pipeline works end to end: upload audio, create a background job, process the file through separate AI stages, and display structured meeting intelligence in a React UI.

The project started with fake AI outputs, but now has adapter boundaries for real transcription and diarization. Stub adapters remain the default so local development and tests stay fast.

## MVP Scope

The MVP supports this flow:

1. Upload an audio file from the frontend.
2. Create a transcription job in the backend.
3. Store job metadata in SQLite.
4. Run a placeholder processing pipeline.
5. Poll job status from the frontend.
6. Display a speaker-separated transcript, summary, action items, decisions, and unanswered questions.

Not included yet:

- Docker
- Auth
- Real-time streaming
- Production background workers
- Production-grade diarization and summarization

## Architecture

```text
frontend/
  React + TypeScript + Vite UI

backend/
  FastAPI API
  SQLite persistence
  Service-layer AI pipeline
  Adapter layer for transcription and diarization

docs/
  Architecture notes and learning roadmap
```

The backend pipeline is deliberately split into small service modules and adapter packages:

- `audio_service.py`: audio normalization and format preparation
- `transcription_service.py`: chooses a transcription adapter
- `diarization_service.py`: chooses a diarization adapter
- `alignment_service.py`: speaker/transcript alignment placeholder
- `summarization_service.py`: structured summary placeholder
- `pipeline_service.py`: orchestrates the pipeline
- `adapters/transcription/`: stub and faster-whisper adapters
- `adapters/diarization/`: stub and pyannote adapters

This keeps model-specific code from leaking into API routes or pipeline orchestration.

## Run The Backend

From the repo root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will run at `http://localhost:8000`.

Useful endpoints:

- `GET /health`
- `POST /api/jobs/upload`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/result`

## Adapter Configuration

Runtime settings are centralized in `backend/app/config.py`.

Stub adapters are the defaults. They make the full upload flow work without downloading models.

```bash
TALKTRACE_TRANSCRIPTION_ADAPTER=stub
TALKTRACE_DIARIZATION_ADAPTER=stub
```

To use faster-whisper for real transcription:

```bash
TALKTRACE_TRANSCRIPTION_ADAPTER=faster_whisper uvicorn app.main:app --reload
```

The faster-whisper adapter currently defaults to:

```bash
TALKTRACE_TRANSCRIPTION_MODEL=base
TALKTRACE_TRANSCRIPTION_DEVICE=cpu
TALKTRACE_TRANSCRIPTION_COMPUTE_TYPE=int8
```

To use pyannote for diarization:

```bash
HUGGINGFACE_TOKEN=your_token \
TALKTRACE_DIARIZATION_ADAPTER=pyannote \
TALKTRACE_PYANNOTE_MODEL=pyannote/speaker-diarization-3.1 \
TALKTRACE_PYANNOTE_DEVICE=cpu \
uvicorn app.main:app --reload
```

You may need to accept the model terms on Hugging Face before pyannote can download the model.

## Stored Artifacts

SQLite stores:

- job metadata and progress
- uploaded audio path
- raw transcript JSON before alignment
- final result JSON after alignment and summarization

This is intentionally simple for the MVP. Later phases can split transcript segments, speaker turns, summaries, and evaluation results into separate tables.

## Run Backend Tests

From the repo root:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

The default suite mocks Hugging Face dataset loading so unit tests do not
depend on network access. To run the optional AMI dataset integration test:

```bash
RUN_HF_TESTS=1 pytest -m integration
```

## Run The Frontend

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

The app will run at `http://localhost:5173`.

If your backend runs somewhere else, set:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Roadmap

### Phase 1: Upload + Fake Pipeline

- Complete: upload, validation, job metadata, progress tracking, fake pipeline, polling UI, failed-state UI, and backend tests.

### Phase 2: Real Transcription

- Mostly complete: faster-whisper adapter, stub default, adapter selection, mocked tests, and raw transcript persistence.
- Manual signoff: upload a short audio file with `TALKTRACE_TRANSCRIPTION_ADAPTER=faster_whisper` and inspect `raw_transcript_json`.

### Phase 3: Speaker Diarization

- In progress: pyannote adapter skeleton and mocked conversion test exist.
- Next: manually run pyannote on a short multi-speaker clip and then persist raw diarization output.

### Phase 4: Speaker-Aware Summaries

- Build prompts around speaker-attributed transcript segments.
- Return structured JSON from an OpenAI-compatible API.
- Add schema validation for summary output.

### Phase 5: Evaluation Harness

- Create sample meetings and expected outputs.
- Score transcription quality, speaker attribution, and summary usefulness.
- Track regressions as you change models and prompts.

## Where To Start

Study these files first:

- `backend/app/api/jobs.py`: HTTP endpoints and request flow
- `backend/app/services/pipeline_service.py`: AI pipeline orchestration
- `backend/app/storage/job_repository.py`: SQLite persistence boundary
- `frontend/src/App.tsx`: user flow in the UI
- `frontend/src/hooks/useJobPolling.ts`: polling job status until completion

The TODO comments are intentionally left for you. Treat them as your implementation map.
