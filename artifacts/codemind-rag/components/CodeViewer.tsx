"use client";

// Phase 8 implementation: Monaco Editor code viewer with syntax highlighting
// Scaffold only — implementation coming in Phase 8

export interface CodeViewerProps {
  filePath?: string;
  code?: string;
  language?: string;
  startLine?: number;
  endLine?: number;
}

export default function CodeViewer({
  filePath,
  code,
  language,
  startLine,
  endLine,
}: CodeViewerProps) {
  return (
    <div style={{ padding: "1rem" }}>
      {filePath && (
        <div
          style={{
            fontSize: "0.75rem",
            color: "#64748b",
            fontFamily: "monospace",
            marginBottom: "0.5rem",
          }}
        >
          {filePath}
          {startLine && endLine && ` (lines ${startLine}-${endLine})`}
        </div>
      )}
      <p style={{ color: "#64748b", fontSize: "0.875rem" }}>
        Code viewer — Phase 8 implementation
      </p>
    </div>
  );
}
