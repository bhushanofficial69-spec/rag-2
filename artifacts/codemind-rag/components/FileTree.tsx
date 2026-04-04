"use client";

// Phase 8 implementation: File tree navigation panel
// Scaffold only — implementation coming in Phase 8

export interface FileTreeProps {
  files?: string[];
  onSelectFile?: (path: string) => void;
}

export default function FileTree({ files, onSelectFile }: FileTreeProps) {
  return (
    <div style={{ padding: "1rem" }}>
      <p style={{ color: "#64748b", fontSize: "0.875rem" }}>
        File tree — Phase 8 implementation
      </p>
    </div>
  );
}
