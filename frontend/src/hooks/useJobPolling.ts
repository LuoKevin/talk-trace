import { useEffect, useState } from "react";

import { fetchJob, fetchJobResult } from "../api/client";
import type { JobMetadata, JobResult } from "../types";

type PollingState = {
  job: JobMetadata | null;
  result: JobResult | null;
  error: string | null;
};

export function useJobPolling(jobId: string | null, refreshKey = 0): PollingState {
  const [job, setJob] = useState<JobMetadata | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setJob(null);
      setResult(null);
      setError(null);
      return;
    }

    let isActive = true;
    const activeJobId = jobId;

    async function poll() {
      try {
        const latestJob = await fetchJob(activeJobId);
        if (!isActive) return;

        setJob(latestJob);
        setError(null);

        if (latestJob.status === "completed") {
          const latestResult = await fetchJobResult(activeJobId);
          if (isActive) setResult(latestResult);
        }
      } catch (err) {
        if (isActive) {
          setError(err instanceof Error ? err.message : "Unknown polling error");
        }
      }
    }

    void poll();
    const intervalId = window.setInterval(poll, 1500);

    return () => {
      isActive = false;
      window.clearInterval(intervalId);
    };
  }, [jobId, refreshKey]);

  return { job, result, error };
}
