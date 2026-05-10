# TalkTrace Learning Roadmap

Use this roadmap as a sequence of checkpoints. Do not rush to model integrations before you understand the data moving through the system.

## Phase 1: Upload + Fake Pipeline

Implementation tasks:

- Completed: add file type, empty-file, file size, and content-type validation in `backend/app/api/jobs.py`.
- Completed: add per-stage progress fields to job metadata.
- Completed: add frontend states for queued, processing, completed, and failed.
- Completed: write backend tests for repository, upload flow, pipeline, and adapter selection.
- Remaining optional task: write a manual QA checklist for upload and polling.

Questions you should be able to answer:

- What happens after the browser sends the file?
- Where is job state stored?
- Why does the upload endpoint return before processing finishes?
- What breaks if the API server restarts during processing?

## Phase 2: Real Transcription

Implementation tasks:

- Completed: add transcription adapters under `backend/app/adapters/transcription`.
- Completed: keep stub transcription as the default adapter.
- Completed: add faster-whisper adapter and mocked conversion tests.
- Completed: save raw transcript output before alignment.
- Add sample audio files for local testing.
- Add error handling for unsupported audio or model failures.
- Manual signoff: run with `TALKTRACE_TRANSCRIPTION_ADAPTER=faster_whisper` and upload a real short audio file.

Questions you should be able to answer:

- What timestamps does your transcription model return?
- Does the model return words, segments, or both?
- How does audio length affect runtime?
- What model output should be persisted for debugging?

Notes:

- faster-whisper returns text and timestamps, not speaker identities.
- Speaker labels are still produced by the diarization stage.
- During Phase 2, the diarization stub should stay single-speaker so transcription testing is not confused by fake extra speakers.

## Phase 3: Speaker Diarization

Implementation tasks:

- Started: add diarization adapters under `backend/app/adapters/diarization`.
- Started: add pyannote adapter skeleton and mocked output conversion tests.
- Replace fake speaker turns in `diarization_service.py` with real pyannote output.
- Persist speaker turns separately from transcript text.
- Add a way to configure expected speaker count when known.
- Test the pipeline on overlapping speech and poor audio.

Questions you should be able to answer:

- What is the difference between diarization and speaker identification?
- Why can diarization be wrong even when transcription is right?
- How do speaker turns line up with transcript segments?
- What should happen when speaker count is unknown?

Manual pyannote setup:

```bash
cd backend
source .venv/bin/activate
HUGGINGFACE_TOKEN=your_token \
TALKTRACE_DIARIZATION_ADAPTER=pyannote \
TALKTRACE_PYANNOTE_MODEL=pyannote/speaker-diarization-3.1 \
uvicorn app.main:app --reload
```

Before running this, accept the selected pyannote model terms on Hugging Face.

## Phase 4: Speaker-Aware Summaries

Implementation tasks:

- Design a prompt that includes speaker labels and timestamps.
- Require structured JSON matching `MeetingSummary`.
- Validate LLM output with Pydantic.
- Add citations from summary points back to transcript segments.

Questions you should be able to answer:

- Why is speaker attribution useful for action items?
- What makes a summary verifiable?
- How do you recover from malformed LLM JSON?
- What data should not be sent to an external API?

## Phase 5: Evaluation Harness

Implementation tasks:

- Create a small dataset of sample meetings.
- Define expected transcript and summary outputs.
- Track word error rate or a simpler transcript quality metric.
- Score summary fields for completeness and hallucination risk.
- Add regression checks before changing prompts or models.

Questions you should be able to answer:

- How do you know the pipeline improved?
- Which errors matter most to users?
- How will you compare two transcription models?
- What summary failures are unacceptable?

## Personal Study Loop

For each phase:

1. Read the relevant service file.
2. Sketch the input and output data shape.
3. Implement the smallest useful change.
4. Run the full upload flow manually.
5. Write down what failed or surprised you.
6. Add one test or checklist item before moving on.
