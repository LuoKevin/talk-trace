import { useState } from "react";

import { updateSpeakerLabels, uploadAudio } from "./api/client";
import { ActionItemsDisplay } from "./components/ActionItemsDisplay";
import { AudioPreviewPanel } from "./components/AudioPreviewPanel";
import { ArtifactsPanel } from "./components/ArtifactsPanel";
import { JobStatusCard } from "./components/JobStatusCard";
import { SpeakerLabelsPanel } from "./components/SpeakerLabelsPanel";
import { SummaryDisplay } from "./components/SummaryDisplay";
import { TranscriptDisplay } from "./components/TranscriptDisplay";
import { UploadPanel } from "./components/UploadPanel";
import { useJobArtifacts } from "./hooks/useJobArtifacts";
import { useJobPolling } from "./hooks/useJobPolling";

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isSavingSpeakerLabels, setIsSavingSpeakerLabels] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [speakerLabelError, setSpeakerLabelError] = useState<string | null>(null);
  const { job, result, error: pollingError } = useJobPolling(jobId, refreshKey);
  const { artifacts, error: artifactsError } = useJobArtifacts(jobId, job, refreshKey);

  async function handleUpload() {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadError(null);
    setJobId(null);

    try {
      const response = await uploadAudio(selectedFile);
      setJobId(response.job_id);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleSaveSpeakerLabels(speakerLabels: Record<string, string>) {
    if (!jobId) return;

    setIsSavingSpeakerLabels(true);
    setSpeakerLabelError(null);

    try {
      await updateSpeakerLabels(jobId, speakerLabels);
      setRefreshKey((current) => current + 1);
    } catch (err) {
      setSpeakerLabelError(
        err instanceof Error ? err.message : "Could not save speaker names",
      );
    } finally {
      setIsSavingSpeakerLabels(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">AI meeting intelligence</p>
          <h1>TalkTrace</h1>
        </div>
        <p>
          Upload audio, track processing, and review the structured output from a
          staged meeting intelligence pipeline.
        </p>
      </header>

      <div className="grid">
        <UploadPanel
          selectedFile={selectedFile}
          isUploading={isUploading}
          onFileChange={setSelectedFile}
          onUpload={handleUpload}
        />
        <JobStatusCard job={job} />
      </div>

      <AudioPreviewPanel file={selectedFile} />

      {uploadError ? <p className="error">{uploadError}</p> : null}
      {pollingError ? <p className="error">{pollingError}</p> : null}
      {artifactsError ? <p className="error">{artifactsError}</p> : null}
      {speakerLabelError ? <p className="error">{speakerLabelError}</p> : null}

      {jobId ? <ArtifactsPanel artifacts={artifacts} /> : null}
      {jobId ? (
        <SpeakerLabelsPanel
          transcript={artifacts?.aligned_transcript ?? null}
          speakerLabels={artifacts?.speaker_labels ?? {}}
          isSaving={isSavingSpeakerLabels}
          onSave={handleSaveSpeakerLabels}
        />
      ) : null}

      {result ? (
        <div className="results">
          <SummaryDisplay summary={result.summary} />
          <div className="grid three-column">
            <ActionItemsDisplay title="Action items" items={result.summary.action_items} />
            <ActionItemsDisplay
              title="Follow-up topics"
              items={result.summary.follow_up_topics}
            />
            <ActionItemsDisplay
              title="Support suggestions"
              items={Object.entries(result.summary.supporter_suggestions).flatMap(
                ([speaker, suggestions]) =>
                  suggestions.map((suggestion) => `${speaker}: ${suggestion}`),
              )}
            />
          </div>
          <TranscriptDisplay transcript={result.transcript} />
        </div>
      ) : job?.status === "failed" ? (
        <section className="failed-state">
          <p>
            {"Processing failed. No result was generated."}
            {job.error ? ` Error details: ${job.error}` : null}
          </p>
        </section>
      ) : (
        <section className="empty-state">
          <p>
            {job
              ? `Results will appear after ${job.stage} finishes.`
              : "Results will appear after the fake pipeline completes."}
          </p>
        </section>
      )}
    </main>
  );
}
