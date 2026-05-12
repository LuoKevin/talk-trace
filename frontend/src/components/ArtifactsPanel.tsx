import type { JobArtifacts } from "../types";

type ArtifactsPanelProps = {
  artifacts: JobArtifacts | null;
};

export function ArtifactsPanel({ artifacts }: ArtifactsPanelProps) {
  return (
    <section className="panel artifacts-panel">
      <div>
        <h2>Pipeline artifacts</h2>
        <p className="muted">Intermediate outputs saved by the backend.</p>
      </div>

      <div className="artifact-metrics">
        <ArtifactMetric
          label="Raw transcript"
          value={countLabel(artifacts?.raw_transcript?.segments.length, "segment")}
        />
        <ArtifactMetric
          label="Diarization"
          value={countLabel(artifacts?.raw_diarization?.speaker_turns.length, "turn")}
        />
        <ArtifactMetric
          label="Aligned transcript"
          value={countLabel(artifacts?.aligned_transcript?.segments.length, "segment")}
        />
        <ArtifactMetric label="Result" value={artifacts?.result ? "Ready" : "Pending"} />
      </div>

      <div className="artifact-details">
        <JsonArtifact title="Raw transcript" value={artifacts?.raw_transcript} />
        <JsonArtifact title="Raw diarization" value={artifacts?.raw_diarization} />
        <JsonArtifact title="Aligned transcript" value={artifacts?.aligned_transcript} />
      </div>
    </section>
  );
}

function ArtifactMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="artifact-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function JsonArtifact({ title, value }: { title: string; value: unknown }) {
  return (
    <details className="artifact-json">
      <summary>{title}</summary>
      <pre>{JSON.stringify(value ?? null, null, 2)}</pre>
    </details>
  );
}

function countLabel(count: number | undefined, noun: string): string {
  if (count === undefined) return "Pending";
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}
