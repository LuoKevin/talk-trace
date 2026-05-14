import { useEffect, useState } from "react";

type AudioPreviewPanelProps = {
  file: File | null;
};

export function AudioPreviewPanel({ file }: AudioPreviewPanelProps) {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!file) {
      setAudioUrl(null);
      return;
    }

    const nextAudioUrl = URL.createObjectURL(file);
    setAudioUrl(nextAudioUrl);

    return () => {
      URL.revokeObjectURL(nextAudioUrl);
    };
  }, [file]);

  if (!file || !audioUrl) {
    return null;
  }

  return (
    <section className="panel audio-preview-panel">
      <div>
        <h2>Audio preview</h2>
        <p className="muted">{file.name}</p>
      </div>
      <audio controls src={audioUrl}>
        Your browser does not support audio playback.
      </audio>
    </section>
  );
}
