# TalkTrace

TalkTrace is an AI meeting intelligence project. The goal is to learn how an AI pipeline works end to end: upload audio, create a background job, process the file through separate AI stages, and display structured meeting intelligence in a React UI.

This scaffold intentionally uses fake AI outputs. The important part for Phase 1 is the shape of the system: API routes, persistence, service boundaries, job status, and frontend polling.

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
- Real WhisperX, pyannote, or OpenAI calls
- Production background workers

## Architecture

```text
frontend/
  React + TypeScript + Vite UI

backend/
  FastAPI API
  SQLite persistence
  Service-layer pipeline placeholders

docs/
  Architecture notes and learning roadmap
```

The backend pipeline is deliberately split into small service modules:

- `audio_service.py`: audio normalization and format preparation
- `transcription_service.py`: speech-to-text placeholder
- `diarization_service.py`: speaker diarization placeholder
- `alignment_service.py`: speaker/transcript alignment placeholder
- `summarization_service.py`: structured summary placeholder
- `pipeline_service.py`: orchestrates the pipeline

This keeps the future WhisperX, pyannote, and LLM code from leaking into API routes.

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

- Understand the request flow from React to FastAPI.
- Confirm jobs are created, persisted, processed, and displayed.
- Add validation for file size and file type.
- Track coarse pipeline progress: preprocessing, transcription, diarization, alignment, summarization, completed.
- Keep tests fast by mocking external dataset access by default.

### Phase 2: Real Transcription

- Integrate a real transcription backend in `transcription_service.py`.
- Save raw transcript segments with timestamps.
- Add tests around transcript parsing and failure handling.

### Phase 3: Speaker Diarization

- Integrate pyannote or a similar diarization model in `diarization_service.py`.
- Store speaker turns independently from transcript text.
- Learn how model output changes based on audio quality.

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
