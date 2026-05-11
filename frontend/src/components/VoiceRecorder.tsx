import { useEffect, useRef, useState } from "react";

type VoiceRecorderProps = {
  disabled?: boolean;
  onRecordingReady: (file: File) => void;
};

const MIME_TYPE_CANDIDATES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/ogg;codecs=opus",
];

export function VoiceRecorder({ disabled = false, onRecordingReady }: VoiceRecorderProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<number | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      stopTimer();
      stopStream();
    };
  }, []);

  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("Voice recording is not supported in this browser.");
      return;
    }

    try {
      setError(null);
      chunksRef.current = [];
      setElapsedSeconds(0);

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = getSupportedMimeType();
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);

      streamRef.current = stream;
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        stopTimer();
        stopStream();
        setIsRecording(false);

        const recordingType = recorder.mimeType || mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: recordingType });
        if (blob.size === 0) {
          setError("Recording was empty.");
          return;
        }

        onRecordingReady(
          new File([blob], `talktrace-recording-${Date.now()}.${extensionFor(recordingType)}`, {
            type: recordingType,
          }),
        );
      };

      recorder.start();
      setIsRecording(true);
      timerRef.current = window.setInterval(() => {
        setElapsedSeconds((current) => current + 1);
      }, 1000);
    } catch (err) {
      stopTimer();
      stopStream();
      setIsRecording(false);
      setError(err instanceof Error ? err.message : "Could not start recording.");
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }

  function stopTimer() {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }

  function stopStream() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  return (
    <div className="voice-recorder">
      <div className="recorder-actions">
        <button
          type="button"
          className={isRecording ? "secondary-button" : undefined}
          disabled={disabled || isRecording}
          onClick={startRecording}
        >
          Record
        </button>
        <button
          type="button"
          className="secondary-button"
          disabled={disabled || !isRecording}
          onClick={stopRecording}
        >
          Stop
        </button>
        <span className="recording-timer">{formatDuration(elapsedSeconds)}</span>
      </div>
      {error ? <p className="inline-error">{error}</p> : null}
    </div>
  );
}

function getSupportedMimeType(): string | undefined {
  return MIME_TYPE_CANDIDATES.find((mimeType) => MediaRecorder.isTypeSupported(mimeType));
}

function extensionFor(mimeType: string): string {
  if (mimeType.includes("mp4")) return "m4a";
  if (mimeType.includes("ogg")) return "ogg";
  return "webm";
}

function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}
