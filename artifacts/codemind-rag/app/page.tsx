"use client";

import { useEffect, useState } from "react";

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<
    "checking" | "online" | "offline"
  >("checking");

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const url =
          process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
        const res = await fetch(`${url}/api/health`, {
          signal: AbortSignal.timeout(3000),
        });
        setBackendStatus(res.ok ? "online" : "offline");
      } catch {
        setBackendStatus("offline");
      }
    };
    checkBackend();
  }, []);

  const statusColor = {
    checking: "#f59e0b",
    online: "#10b981",
    offline: "#64748b",
  }[backendStatus];

  const statusLabel = {
    checking: "Checking backend...",
    online: "Backend Online",
    offline: "Backend Offline (Phase 2+)",
  }[backendStatus];

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#0f1117",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
        gap: "2rem",
      }}
    >
      <div style={{ textAlign: "center", maxWidth: "640px" }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            background: "#1e2130",
            border: "1px solid #2d3448",
            borderRadius: "999px",
            padding: "0.25rem 1rem",
            fontSize: "0.75rem",
            color: "#6366f1",
            marginBottom: "1.5rem",
            fontWeight: 600,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
          }}
        >
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              background: "#10b981",
              display: "inline-block",
            }}
          />
          Phase 1 Complete
        </div>

        <h1
          style={{
            fontSize: "clamp(2rem, 5vw, 3.5rem)",
            fontWeight: 800,
            color: "#e2e8f0",
            lineHeight: 1.1,
            marginBottom: "1rem",
          }}
        >
          CodeMind{" "}
          <span
            style={{
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            RAG
          </span>
        </h1>

        <p
          style={{
            fontSize: "1.125rem",
            color: "#64748b",
            lineHeight: 1.6,
            marginBottom: "2rem",
          }}
        >
          Intelligent Codebase Search Engine — Ask natural language questions
          about any GitHub repository and get instant, cited answers.
        </p>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "0.5rem",
            padding: "0.75rem 1.5rem",
            background: "#1e2130",
            border: "1px solid #2d3448",
            borderRadius: "0.75rem",
            fontSize: "0.875rem",
            color: "#e2e8f0",
          }}
        >
          <span
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              background: statusColor,
              display: "inline-block",
              transition: "background 0.3s",
            }}
          />
          {statusLabel}
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          width: "100%",
          maxWidth: "640px",
        }}
      >
        {[
          {
            phase: "Phase 1",
            label: "Environment & Scaffolding",
            status: "complete",
          },
          {
            phase: "Phase 2",
            label: "Repo Cloning & Ingestion",
            status: "pending",
          },
          {
            phase: "Phase 3",
            label: "Code Chunking Engine",
            status: "pending",
          },
          {
            phase: "Phase 4",
            label: "Embedding & Vector DB",
            status: "pending",
          },
        ].map((item) => (
          <div
            key={item.phase}
            style={{
              background: "#1e2130",
              border: `1px solid ${item.status === "complete" ? "#6366f1" : "#2d3448"}`,
              borderRadius: "0.75rem",
              padding: "1rem",
            }}
          >
            <div
              style={{
                fontSize: "0.7rem",
                color:
                  item.status === "complete" ? "#6366f1" : "#64748b",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                marginBottom: "0.25rem",
              }}
            >
              {item.phase}
            </div>
            <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
              {item.label}
            </div>
            <div
              style={{
                marginTop: "0.5rem",
                fontSize: "0.7rem",
                color:
                  item.status === "complete" ? "#10b981" : "#475569",
                fontWeight: 600,
              }}
            >
              {item.status === "complete" ? "✓ Complete" : "Pending"}
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "0.75rem",
          width: "100%",
          maxWidth: "640px",
        }}
      >
        {[
          { label: "Next.js 14", value: "App Router ✓" },
          { label: "TypeScript", value: "Strict Mode ✓" },
          { label: "Tailwind CSS", value: "v4 Configured ✓" },
          { label: "Monaco Editor", value: "Installed ✓" },
        ].map((item) => (
          <div
            key={item.label}
            style={{
              background: "#1e2130",
              border: "1px solid #2d3448",
              borderRadius: "0.5rem",
              padding: "0.75rem",
              textAlign: "center",
            }}
          >
            <div
              style={{
                fontSize: "0.7rem",
                color: "#64748b",
                marginBottom: "0.25rem",
              }}
            >
              {item.label}
            </div>
            <div
              style={{ fontSize: "0.8rem", color: "#10b981", fontWeight: 600 }}
            >
              {item.value}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
