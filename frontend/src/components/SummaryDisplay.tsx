import type { Summarization } from "../types";

type SummaryDisplayProps = {
  summary: Summarization;
};

export function SummaryDisplay({ summary }: SummaryDisplayProps) {
  return (
    <section className="panel">
      <h2>Overall summary</h2>
      <p className="muted">Main speaker: {summary.main_speaker}</p>
      <p>{summary.overview}</p>
    </section>
  );
}
