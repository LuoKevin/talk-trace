import { useEffect, useMemo, useState } from "react";

import type { AlignedTranscript } from "../types";

type SpeakerLabelsPanelProps = {
  transcript: AlignedTranscript | null;
  speakerLabels: Record<string, string>;
  isSaving: boolean;
  onSave: (speakerLabels: Record<string, string>) => void;
};

export function SpeakerLabelsPanel({
  transcript,
  speakerLabels,
  isSaving,
  onSave,
}: SpeakerLabelsPanelProps) {
  const speakers = useMemo(() => {
    return Array.from(new Set(transcript?.segments.map((segment) => segment.speaker) ?? []));
  }, [transcript]);
  const [draftLabels, setDraftLabels] = useState<Record<string, string>>({});

  useEffect(() => {
    setDraftLabels(
      Object.fromEntries(
        speakers.map((speaker) => [speaker, speakerLabels[speaker] ?? ""]),
      ),
    );
  }, [speakerLabels, speakers]);

  if (speakers.length === 0) {
    return null;
  }

  function updateDraftLabel(speaker: string, label: string) {
    setDraftLabels((current) => ({
      ...current,
      [speaker]: label,
    }));
  }

  return (
    <section className="panel speaker-labels-panel">
      <div>
        <h2>Speaker names</h2>
        <p className="muted">Rename detected speakers for this job.</p>
      </div>

      <div className="speaker-label-grid">
        {speakers.map((speaker) => (
          <label className="speaker-label-row" key={speaker}>
            <span>{speaker}</span>
            <input
              type="text"
              value={draftLabels[speaker] ?? ""}
              placeholder="Display name"
              onChange={(event) => updateDraftLabel(speaker, event.target.value)}
            />
          </label>
        ))}
      </div>

      <button type="button" disabled={isSaving} onClick={() => onSave(draftLabels)}>
        {isSaving ? "Saving..." : "Save speaker names"}
      </button>
    </section>
  );
}
