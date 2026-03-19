"use client";

import { useState } from "react";
import type { QuestionResponse } from "@/lib/api";

interface DevPanelProps {
  result: QuestionResponse;
}

interface Step {
  step: string;
  output?: Record<string, unknown>;
}

export default function DevPanel({ result }: DevPanelProps) {
  const [section, setSection] = useState<"pipeline" | "json">("pipeline");

  const steps: Step[] = Array.isArray(result.provenance?.["steps"])
    ? (result.provenance!["steps"] as Step[])
    : [];

  return (
    <div className="rounded-xl border border-anchor-800/60 bg-gray-900/80 overflow-hidden">
      {/* Dev panel header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-anchor-950/50 border-b border-anchor-800/40">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-anchor-400 animate-pulse" />
          <span className="text-xs font-mono font-medium text-anchor-300">Developer Mode</span>
        </div>
        <div className="flex items-center gap-1 rounded border border-anchor-800/40 overflow-hidden">
          {(["pipeline", "json"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSection(s)}
              className={`px-2.5 py-1 text-xs font-mono transition-colors ${
                section === s
                  ? "bg-anchor-700/50 text-anchor-200"
                  : "text-anchor-500 hover:text-anchor-300"
              }`}
            >
              {s === "pipeline" ? "Pipeline" : "Raw JSON"}
            </button>
          ))}
        </div>
      </div>

      <div className="p-4">
        {section === "pipeline" && (
          <PipelineView steps={steps} executionMs={result.execution_ms} />
        )}
        {section === "json" && (
          <JsonView result={result} />
        )}
      </div>
    </div>
  );
}

function PipelineView({ steps, executionMs }: { steps: Step[]; executionMs: number | null | undefined }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (steps.length === 0) {
    return <p className="text-xs text-gray-600">No pipeline trace available.</p>;
  }

  return (
    <div className="space-y-1.5">
      {executionMs != null && (
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs text-gray-500 font-mono">Total execution</span>
          <span className="text-xs font-mono text-anchor-400">{executionMs}ms</span>
        </div>
      )}
      {steps.map((s, i) => {
        const isOpen = expanded === s.step;
        const outputSize = s.output ? JSON.stringify(s.output).length : 0;

        return (
          <div key={i} className="rounded-md border border-gray-800 overflow-hidden">
            <button
              onClick={() => setExpanded(isOpen ? null : s.step)}
              className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-gray-800/40 transition-colors"
              aria-expanded={isOpen}
            >
              <div className="flex items-center gap-2">
                <span className="text-green-500 text-xs font-mono">✓</span>
                <span className="text-xs font-mono text-gray-300">{s.step}</span>
              </div>
              <div className="flex items-center gap-2">
                {outputSize > 0 && (
                  <span className="text-xs text-gray-600 font-mono">{outputSize}B</span>
                )}
                <svg
                  className={`h-3 w-3 text-gray-600 transition-transform ${isOpen ? "rotate-180" : ""}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {isOpen && s.output && (
              <div className="border-t border-gray-800 bg-gray-950/60 px-3 py-2 overflow-x-auto">
                <pre className="text-xs font-mono text-gray-400 whitespace-pre-wrap leading-relaxed">
                  {JSON.stringify(s.output, null, 2)}
                </pre>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function JsonView({ result }: { result: QuestionResponse }) {
  // Redact large row arrays in the JSON view for readability
  const display = {
    ...result,
    rows: result.rows.length > 5
      ? [...result.rows.slice(0, 5), `... ${result.rows.length - 5} more rows`]
      : result.rows,
  };

  return (
    <div className="overflow-x-auto">
      <pre className="text-xs font-mono text-gray-400 leading-relaxed whitespace-pre-wrap">
        {JSON.stringify(display, null, 2)}
      </pre>
    </div>
  );
}
