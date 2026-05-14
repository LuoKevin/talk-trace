export type JobStatus = "queued" | "processing" | "completed" | "failed";

export type PipelineStage =
  | "uploaded"
  | "preprocessing"
  | "transcription"
  | "diarization"
  | "alignment"
  | "summarization"
  | "completed"
  | "failed";

export type JobMetadata = {
  id: string;
  filename: string;
  status: JobStatus;
  stage: PipelineStage;
  progress_percent: number;
  created_at: string;
  updated_at: string;
  error: string | null;
};

export type TranscriptSegment = {
  speaker: string;
  start_seconds: number;
  end_seconds: number;
  text: string;
};

export type RawTranscriptSegment = {
  start_seconds: number;
  end_seconds: number;
  text: string;
};

export type RawTranscript = {
  segments: RawTranscriptSegment[];
};

export type SpeakerTurn = {
  speaker: string;
  start_seconds: number;
  end_seconds: number;
};

export type Diarization = {
  speaker_turns: SpeakerTurn[];
};

export type AlignedTranscript = {
  segments: AlignedTranscriptSegment[];
};

export type AlignedTranscriptSegment = TranscriptSegment & {
  overlap_seconds: number;
  overlap_ratio: number;
};

export type Summarization = {
  main_speaker: string;
  overview: string;
  action_items: string[];
  follow_up_topics: string[];
  supporter_suggestions: Record<string, string[]>;
};

export type JobResult = {
  job_id: string;
  transcript: AlignedTranscript;
  summary: Summarization;
};

export type UploadResponse = {
  job_id: string;
  status: JobStatus;
};

export type JobArtifacts = {
  raw_transcript: RawTranscript | null;
  raw_diarization: Diarization | null;
  aligned_transcript: AlignedTranscript | null;
  raw_summarization: Summarization | null;
  speaker_labels: Record<string, string>;
  result: JobResult | null;
};

export type SpeakerLabelsResponse = {
  speaker_labels: Record<string, string>;
};
