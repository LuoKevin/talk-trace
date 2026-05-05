import type { JobMetadata } from "../types";

type JobStatusCardProps = {
  job: JobMetadata | null;
};

export function JobStatusCard({ job }: JobStatusCardProps) {
  return (
    <section className="panel">
      <h2>Job status</h2>
      {job ? (
        <dl className="status-grid">
          <dt>Job ID</dt>
          <dd>{job.id}</dd>
          <dt>File</dt>
          <dd>{job.filename}</dd>
          <dt>Status</dt>
          <dd>
            <span className={`status-pill status-${job.status}`}>{job.status}</span>
          </dd>
          <dt>Stage</dt>
          <dd>{formatStage(job.stage)}</dd>
          <dt>Progress</dt>
          <dd>
            <div className="progress-track" aria-label="Job progress">
              <div
                className="progress-fill"
                style={{ width: `${job.progress_percent}%` }}
              />
            </div>
            <span className="progress-label">{job.progress_percent}%</span>
          </dd>
          {job.error ? (
            <>
              <dt>Error</dt>
              <dd>{job.error}</dd>
            </>
          ) : null}
        </dl>
      ) : (
        <p className="muted">No job has been created yet.</p>
      )}
    </section>
  );
}

function formatStage(stage: string): string {
  return stage
    .split("_")
    .join(" ")
    .replace(/^\w/, (letter) => letter.toUpperCase());
}
