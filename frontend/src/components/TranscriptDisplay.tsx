import type { TranscriptSegment } from "../types";

type TranscriptDisplayProps = {
  transcript: TranscriptSegment[];
};

export function TranscriptDisplay({ transcript }: TranscriptDisplayProps) {
  return (
    <section className="panel">
      <h2>Speaker transcript</h2>
      <div className="transcript-list">
        {transcript.map((segment, index) => (
          <article className="transcript-segment" key={`${segment.start_seconds}-${index}`}>
            <div className="segment-meta">
              <strong>{segment.speaker}</strong>
              <span>
                {formatTime(segment.start_seconds)} - {formatTime(segment.end_seconds)}
              </span>
            </div>
            <p>{segment.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}
