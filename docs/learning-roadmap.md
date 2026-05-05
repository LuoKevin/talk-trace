# TalkTrace Learning Roadmap

Use this roadmap as a sequence of checkpoints. Do not rush to model integrations before you understand the data moving through the system.

## Phase 1: Upload + Fake Pipeline

Implementation tasks:

- Add file type and file size validation in `backend/app/api/jobs.py`.
- Add per-stage progress fields to job metadata.
- Add a frontend loading state that distinguishes queued, processing, completed, and failed.
- Write one backend test for creating a job.
- Write one frontend test or manual checklist for upload and polling.

Questions you should be able to answer:

- What happens after the browser sends the file?
- Where is job state stored?
- Why does the upload endpoint return before processing finishes?
- What breaks if the API server restarts during processing?

## Phase 2: Real Transcription

Implementation tasks:

- Replace the fake output in `transcription_service.py` with a real transcription adapter.
- Save raw transcript output before alignment.
- Add sample audio files for local testing.
- Add error handling for unsupported audio or model failures.

Questions you should be able to answer:

- What timestamps does your transcription model return?
- Does the model return words, segments, or both?
- How does audio length affect runtime?
- What model output should be persisted for debugging?

## Phase 3: Speaker Diarization

Implementation tasks:

- Replace fake speaker turns in `diarization_service.py`.
- Persist speaker turns separately from transcript text.
- Add a way to configure expected speaker count when known.
- Test the pipeline on overlapping speech and poor audio.

Questions you should be able to answer:

- What is the difference between diarization and speaker identification?
- Why can diarization be wrong even when transcription is right?
- How do speaker turns line up with transcript segments?
- What should happen when speaker count is unknown?

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
