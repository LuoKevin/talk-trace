import type { MeetingSummary } from "../types";

type SummaryDisplayProps = {
  summary: MeetingSummary;
};

export function SummaryDisplay({ summary }: SummaryDisplayProps) {
  return (
    <section className="panel">
      <h2>Overall summary</h2>
      <p>{summary.overview}</p>
    </section>
  );
}
