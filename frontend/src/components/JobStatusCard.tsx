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
