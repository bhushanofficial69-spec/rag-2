"use client";

// Phase 8 implementation: GitHub URL input form with progress tracking
// Scaffold only — implementation coming in Phase 8

export interface RepoInputProps {
  onIngestionComplete?: (repoName: string) => void;
}

export default function RepoInput({ onIngestionComplete }: RepoInputProps) {
  return (
    <div style={{ padding: "1rem" }}>
      <p style={{ color: "#64748b", fontSize: "0.875rem" }}>
        Repo input — Phase 8 implementation
      </p>
    </div>
  );
}
