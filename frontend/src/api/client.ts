import type { JobArtifacts, JobMetadata, JobResult, UploadResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function uploadAudio(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/jobs/upload`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<UploadResponse>(response);
}

export async function fetchJob(jobId: string): Promise<JobMetadata> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`);
  return parseResponse<JobMetadata>(response);
}

export async function fetchJobResult(jobId: string): Promise<JobResult> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/result`);
  return parseResponse<JobResult>(response);
}

export async function fetchJobArtifacts(jobId: string): Promise<JobArtifacts> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/artifacts`);
  return parseResponse<JobArtifacts>(response);
}
