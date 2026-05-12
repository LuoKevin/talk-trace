import { useState } from "react";

import { uploadAudio } from "./api/client";
import { ActionItemsDisplay } from "./components/ActionItemsDisplay";
import { ArtifactsPanel } from "./components/ArtifactsPanel";
import { JobStatusCard } from "./components/JobStatusCard";
import { SummaryDisplay } from "./components/SummaryDisplay";
import { TranscriptDisplay } from "./components/TranscriptDisplay";
import { UploadPanel } from "./components/UploadPanel";
import { useJobArtifacts } from "./hooks/useJobArtifacts";
import { useJobPolling } from "./hooks/useJobPolling";

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const { job, result, error: pollingError } = useJobPolling(jobId);
  const { artifacts, error: artifactsError } = useJobArtifacts(jobId, job);

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

      {uploadError ? <p className="error">{uploadError}</p> : null}
      {pollingError ? <p className="error">{pollingError}</p> : null}
      {artifactsError ? <p className="error">{artifactsError}</p> : null}

      {jobId ? <ArtifactsPanel artifacts={artifacts} /> : null}

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
