import { useEffect, useState } from "react";

import { fetchJobArtifacts } from "../api/client";
import type { JobArtifacts, JobMetadata } from "../types";

type ArtifactState = {
  artifacts: JobArtifacts | null;
  error: string | null;
};

export function useJobArtifacts(
  jobId: string | null,
  job: JobMetadata | null,
  refreshKey = 0,
): ArtifactState {
  const [artifacts, setArtifacts] = useState<JobArtifacts | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setArtifacts(null);
      setError(null);
      return;
    }

    let isActive = true;
    const activeJobId = jobId;

    async function loadArtifacts() {
      try {
        const latestArtifacts = await fetchJobArtifacts(activeJobId);
        if (!isActive) return;

        setArtifacts(latestArtifacts);
        setError(null);
      } catch (err) {
        if (isActive) {
          setError(err instanceof Error ? err.message : "Could not load artifacts");
        }
      }
    }

    void loadArtifacts();

    if (job?.status === "completed" || job?.status === "failed") {
      return () => {
        isActive = false;
      };
    }

    const intervalId = window.setInterval(loadArtifacts, 1500);

    return () => {
      isActive = false;
      window.clearInterval(intervalId);
    };
  }, [jobId, job?.status, refreshKey]);

  return { artifacts, error };
}
