export type JobStatus = "queued" | "processing" | "completed" | "failed";

export type JobMetadata = {
  id: string;
  filename: string;
  status: JobStatus;
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

export type MeetingSummary = {
  overview: string;
  action_items: string[];
  decisions: string[];
  unanswered_questions: string[];
};

export type JobResult = {
  job_id: string;
  transcript: TranscriptSegment[];
  summary: MeetingSummary;
};

export type UploadResponse = {
  job_id: string;
  status: JobStatus;
};
