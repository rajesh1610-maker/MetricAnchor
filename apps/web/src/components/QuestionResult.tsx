"use client";

import { useState } from "react";
import {
  submitFeedback,
  type QuestionResponse,
  type SemanticMappingItem,
} from "@/lib/api";
import SqlDisplay from "@/components/SqlDisplay";

interface QuestionResultProps {
  result: QuestionResponse;
}

const CONFIDENCE_STYLES: Record<string, string> = {
  high: "bg-green-900/30 border-green-700 text-green-300",
  medium: "bg-yellow-900/20 border-yellow-700 text-yellow-300",
  low: "bg-red-900/20 border-red-700 text-red-300",
  clarification_needed: "bg-purple-900/20 border-purple-700 text-purple-300",
};

const CONFIDENCE_LABELS: Record<string, string> = {
  high: "High confidence",
  medium: "Medium confidence",
  low: "Low confidence",
  clarification_needed: "Clarification needed",
};

export default function QuestionResult({ result }: QuestionResultProps) {
  const [feedbackSent, setFeedbackSent] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"result" | "sql" | "trust">("result");

  async function handleFeedback(type: "correct" | "partial" | "wrong") {
    try {
      await submitFeedback(result.id, type);
      setFeedbackSent(type);
    } catch {
      // ignore
    }
  }

  const confidence = result.confidence ?? "low";
  const confidenceStyle = CONFIDENCE_STYLES[confidence] ?? CONFIDENCE_STYLES.low;
  const confidenceLabel = CONFIDENCE_LABELS[confidence] ?? confidence;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 overflow-hidden">
      {/* Question header */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/60">
        <p className="text-xs text-gray-500 mb-1">Question</p>
        <p className="text-sm text-gray-200 font-medium">{result.question}</p>
      </div>

      {/* Error state */}
      {result.error && (
        <div className="px-6 py-4 border-b border-gray-800">
          <div className="rounded-lg border border-red-700 bg-red-900/20 p-4 text-sm text-red-300">
            <span className="font-semibold">Could not answer: </span>
            {result.error}
          </div>
        </div>
      )}

      {/* Clarification needed */}
      {!result.error && result.clarifying_question && (
        <div className="px-6 py-4 border-b border-gray-800">
          <div className="rounded-lg border border-purple-700 bg-purple-900/20 p-4 text-sm text-purple-200">
            <p className="font-semibold mb-1">I need a bit more info:</p>
            <p>{result.clarifying_question}</p>
          </div>
        </div>
      )}

      {/* Main answer */}
      {result.answer && !result.error && (
        <div className="px-6 py-5 border-b border-gray-800">
          <p className="text-gray-100 text-base leading-relaxed">{result.answer}</p>

          {/* Confidence badge */}
          <div className={`mt-3 inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs ${confidenceStyle}`}>
            <span>{confidenceLabel}</span>
            {result.confidence_note && (
              <span className="text-opacity-70">— {result.confidence_note}</span>
            )}
          </div>
        </div>
      )}

      {/* Result table (when rows returned) */}
      {result.rows.length > 0 && result.chart_type !== "metric" && (
        <div className="px-6 py-4 border-b border-gray-800 overflow-x-auto">
          <p className="text-xs text-gray-500 mb-2">
            {result.row_count} row{result.row_count !== 1 ? "s" : ""}
          </p>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                {result.columns.map((col) => (
                  <th
                    key={col}
                    className="py-1.5 pr-6 text-left text-xs font-medium text-gray-400 uppercase tracking-wide"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.rows.slice(0, 20).map((row, i) => (
                <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                  {row.map((cell, j) => (
                    <td key={j} className="py-1.5 pr-6 text-gray-200 font-mono text-xs">
                      {cell == null ? <span className="text-gray-600">null</span> : String(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {result.row_count > 20 && (
            <p className="mt-2 text-xs text-gray-600">
              Showing 20 of {result.row_count} rows
            </p>
          )}
        </div>
      )}

      {/* Single metric KPI */}
      {result.chart_type === "metric" && result.rows.length > 0 && (
        <div className="px-6 py-6 border-b border-gray-800">
          <p className="text-4xl font-bold text-anchor-400 font-mono">
            {_fmtCell(result.rows[0][0])}
          </p>
          <p className="text-xs text-gray-500 mt-1">{result.columns[0]}</p>
        </div>
      )}

      {/* Tab bar */}
      {(result.sql || result.semantic_mappings.length > 0) && (
        <>
          <div className="flex border-b border-gray-800">
            {(["result", "sql", "trust"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2.5 text-xs font-medium capitalize transition-colors border-b-2 ${
                  activeTab === tab
                    ? "border-anchor-500 text-anchor-400"
                    : "border-transparent text-gray-500 hover:text-gray-300"
                }`}
              >
                {tab === "trust"
                  ? "Trust & Provenance"
                  : tab === "sql"
                  ? "SQL"
                  : "Summary"}
              </button>
            ))}
          </div>

          <div className="p-6">
            {activeTab === "sql" && result.sql && (
              <SqlDisplay sql={result.sql} executionMs={result.execution_ms} />
            )}

            {activeTab === "trust" && (
              <TrustPanel result={result} />
            )}

            {activeTab === "result" && (
              <SummaryPanel result={result} />
            )}
          </div>
        </>
      )}

      {/* Feedback */}
      <div className="px-6 py-3 border-t border-gray-800 flex items-center justify-between">
        <p className="text-xs text-gray-600">Was this answer helpful?</p>
        {feedbackSent ? (
          <p className="text-xs text-gray-500">Thanks for the feedback.</p>
        ) : (
          <div className="flex items-center gap-2">
            <FeedbackButton onClick={() => handleFeedback("correct")} label="Yes" />
            <FeedbackButton onClick={() => handleFeedback("partial")} label="Partial" />
            <FeedbackButton onClick={() => handleFeedback("wrong")} label="Wrong" />
          </div>
        )}
      </div>
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function SummaryPanel({ result }: { result: QuestionResponse }) {
  return (
    <div className="space-y-4">
      {result.assumptions.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Assumptions
          </p>
          <ul className="space-y-1">
            {result.assumptions.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
                <span className="text-gray-600 mt-0.5">•</span>
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.caveats.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-yellow-600 uppercase tracking-wide mb-2">
            Caveats
          </p>
          <ul className="space-y-1">
            {result.caveats.map((c, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-yellow-400">
                <span className="mt-0.5">!</span>
                {c}
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.assumptions.length === 0 && result.caveats.length === 0 && (
        <p className="text-xs text-gray-600">No additional context for this answer.</p>
      )}
    </div>
  );
}

function TrustPanel({ result }: { result: QuestionResponse }) {
  // Extract provenance steps with a proper type guard — avoids `unknown` in JSX
  const provenanceSteps: Array<{ step: string }> = (() => {
    const raw = result.provenance?.["steps"];
    return Array.isArray(raw) ? (raw as Array<{ step: string }>) : [];
  })();

  return (
    <div className="space-y-5">
      {/* Semantic mappings */}
      {result.semantic_mappings.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Business Terms Resolved
          </p>
          <div className="flex flex-wrap gap-2">
            {result.semantic_mappings.map((m, i) => (
              <MappingChip key={i} mapping={m} />
            ))}
          </div>
        </div>
      )}

      {/* Assumptions */}
      {result.assumptions.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Assumptions Made
          </p>
          <ul className="space-y-1">
            {result.assumptions.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
                <span className="text-gray-600 mt-0.5">•</span>
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Caveats */}
      {result.caveats.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-yellow-600 uppercase tracking-wide mb-2">
            Model Caveats
          </p>
          <ul className="space-y-1">
            {result.caveats.map((c, i) => (
              <li key={i} className="text-xs text-yellow-400 flex items-start gap-2">
                <span>!</span>
                {c}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Provenance steps */}
      {provenanceSteps.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Pipeline Steps
          </p>
          <div className="space-y-1">
            {provenanceSteps.map((s, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-gray-400">
                <span className="text-green-500 font-mono">✓</span>
                <span className="font-mono">{s.step}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MappingChip({ mapping }: { mapping: SemanticMappingItem }) {
  const typeColor =
    mapping.type === "metric"
      ? "border-anchor-700 bg-anchor-900/30 text-anchor-300"
      : "border-blue-700 bg-blue-900/20 text-blue-300";

  return (
    <div className={`rounded-full border px-2.5 py-1 text-xs flex items-center gap-1.5 ${typeColor}`}>
      <span>&quot;{mapping.phrase}&quot;</span>
      <span className="text-gray-600">→</span>
      <span className="font-mono">{mapping.resolved_to}</span>
      {mapping.via !== "exact" && (
        <span className="text-gray-500 text-xs">({mapping.via})</span>
      )}
    </div>
  );
}

function FeedbackButton({
  onClick,
  label,
}: {
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className="rounded px-2.5 py-1 text-xs text-gray-500 border border-gray-700 hover:border-gray-500 hover:text-gray-200 transition-colors"
    >
      {label}
    </button>
  );
}

function _fmtCell(v: string | number | null): string {
  if (v == null) return "—";
  if (typeof v === "number") {
    return Number.isInteger(v) ? v.toLocaleString() : v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return String(v);
}
