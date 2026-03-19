"use client";

import { useState } from "react";
import { type QuestionResponse, type SemanticMappingItem } from "@/lib/api";
import SqlDisplay from "@/components/SqlDisplay";
import KpiCard from "@/components/charts/KpiCard";
import BarChart from "@/components/charts/BarChart";
import LineChart from "@/components/charts/LineChart";
import FeedbackModal from "@/components/FeedbackModal";
import DevPanel from "@/components/DevPanel";

type Tab = "answer" | "chart" | "table" | "sql" | "assumptions" | "provenance";

const TABS: { id: Tab; label: string }[] = [
  { id: "answer", label: "Answer" },
  { id: "chart", label: "Chart" },
  { id: "table", label: "Table" },
  { id: "sql", label: "SQL" },
  { id: "assumptions", label: "Assumptions" },
  { id: "provenance", label: "Provenance" },
];

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

interface QuestionResultProps {
  result: QuestionResponse;
  devMode?: boolean;
}

export default function QuestionResult({ result, devMode = false }: QuestionResultProps) {
  const [activeTab, setActiveTab] = useState<Tab>("answer");
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<"correct" | "partial" | "wrong" | null>(null);

  const confidence = result.confidence ?? "low";
  const confidenceStyle = CONFIDENCE_STYLES[confidence] ?? CONFIDENCE_STYLES.low;
  const confidenceLabel = CONFIDENCE_LABELS[confidence] ?? confidence;

  // Determine which tabs have content (show all but dim empty ones)
  const hasChart =
    result.chart_type != null &&
    result.chart_type !== "table" &&
    result.rows.length > 0;
  const hasTable = result.rows.length > 0;
  const hasSql = !!result.sql;
  const hasAssumptions = result.assumptions.length > 0 || result.caveats.length > 0;
  const hasProvenance =
    result.semantic_mappings.length > 0 ||
    Array.isArray((result.provenance as Record<string, unknown> | null)?.["steps"]);

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 overflow-hidden">
      {/* Question header */}
      <div className="px-5 py-3.5 border-b border-gray-800 bg-gray-900/60 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs text-gray-500 mb-0.5">Question</p>
          <p className="text-sm text-gray-200 font-medium">{result.question}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {result.execution_ms != null && (
            <span className="text-xs font-mono text-gray-600">{result.execution_ms}ms</span>
          )}
          {feedbackSent ? (
            <span className="text-xs text-gray-500">Feedback sent</span>
          ) : (
            <button
              onClick={() => setShowFeedback(true)}
              className="rounded-md border border-gray-700 px-2.5 py-1 text-xs text-gray-400 hover:border-gray-500 hover:text-gray-200 transition-colors"
            >
              Rate answer
            </button>
          )}
        </div>
      </div>

      {/* Error state */}
      {result.error && (
        <div className="px-5 py-4">
          <div className="rounded-lg border border-red-700 bg-red-900/20 p-4 text-sm text-red-300">
            <span className="font-semibold">Could not answer: </span>
            {result.error}
          </div>
        </div>
      )}

      {/* Clarification needed */}
      {!result.error && result.clarifying_question && (
        <div className="px-5 py-4">
          <div className="rounded-lg border border-purple-700 bg-purple-900/20 p-4 text-sm text-purple-200">
            <p className="font-semibold mb-1">I need a bit more info:</p>
            <p>{result.clarifying_question}</p>
          </div>
        </div>
      )}

      {/* Tab bar */}
      {!result.error && (
        <div className="flex border-b border-gray-800 overflow-x-auto">
          {TABS.map(({ id, label }) => {
            const isEmpty =
              (id === "chart" && !hasChart) ||
              (id === "table" && !hasTable) ||
              (id === "sql" && !hasSql) ||
              (id === "assumptions" && !hasAssumptions) ||
              (id === "provenance" && !hasProvenance);
            return (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`shrink-0 px-4 py-2.5 text-xs font-medium transition-colors border-b-2 ${
                  activeTab === id
                    ? "border-anchor-500 text-anchor-400"
                    : isEmpty
                    ? "border-transparent text-gray-700 cursor-default"
                    : "border-transparent text-gray-500 hover:text-gray-300"
                }`}
                disabled={isEmpty}
                aria-current={activeTab === id ? "true" : undefined}
              >
                {label}
              </button>
            );
          })}
        </div>
      )}

      {/* Tab content */}
      {!result.error && (
        <div className="p-5">
          {activeTab === "answer" && (
            <AnswerTab result={result} confidenceStyle={confidenceStyle} confidenceLabel={confidenceLabel} />
          )}
          {activeTab === "chart" && hasChart && (
            <ChartTab result={result} />
          )}
          {activeTab === "table" && hasTable && (
            <TableTab result={result} />
          )}
          {activeTab === "sql" && hasSql && (
            <SqlDisplay sql={result.sql!} executionMs={result.execution_ms} />
          )}
          {activeTab === "assumptions" && (
            <AssumptionsTab result={result} />
          )}
          {activeTab === "provenance" && (
            <ProvenanceTab result={result} />
          )}
        </div>
      )}

      {/* Dev Panel */}
      {devMode && !result.error && (
        <div className="border-t border-gray-800 p-5">
          <DevPanel result={result} />
        </div>
      )}

      {/* Feedback modal */}
      {showFeedback && (
        <FeedbackModal
          questionId={result.id}
          questionText={result.question}
          onClose={() => setShowFeedback(false)}
          onSubmitted={(type) => setFeedbackSent(type)}
        />
      )}
    </div>
  );
}

// ── Tab panels ─────────────────────────────────────────────────────────────────

function AnswerTab({
  result,
  confidenceStyle,
  confidenceLabel,
}: {
  result: QuestionResponse;
  confidenceStyle: string;
  confidenceLabel: string;
}) {
  return (
    <div className="space-y-4">
      {result.answer && (
        <p className="text-gray-100 text-sm leading-relaxed">{result.answer}</p>
      )}

      {/* Single metric KPI */}
      {result.chart_type === "metric" && result.rows.length > 0 && (
        <KpiCard
          value={result.rows[0][0]}
          label={result.columns[0] ?? "Value"}
        />
      )}

      {result.confidence && (
        <div
          className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs ${confidenceStyle}`}
        >
          <span>{confidenceLabel}</span>
          {result.confidence_note && (
            <span className="opacity-70">— {result.confidence_note}</span>
          )}
        </div>
      )}

      {!result.answer && !result.clarifying_question && (
        <p className="text-sm text-gray-600">No answer generated.</p>
      )}
    </div>
  );
}

function ChartTab({ result }: { result: QuestionResponse }) {
  const { chart_type, columns, rows } = result;

  if (chart_type === "metric" && rows.length > 0) {
    return <KpiCard value={rows[0][0]} label={columns[0] ?? "Value"} />;
  }

  if ((chart_type === "bar" || chart_type === "grouped_bar") && rows.length > 0) {
    const data = rows.map((row) => ({
      label: row[0] != null ? String(row[0]) : "—",
      value: typeof row[1] === "number" ? row[1] : parseFloat(String(row[1] ?? 0)) || 0,
    }));
    return <BarChart data={data} valueLabel={columns[1]} />;
  }

  if (chart_type === "line" && rows.length > 0) {
    const data = rows.map((row) => ({
      x: row[0] != null ? String(row[0]) : "",
      y: typeof row[1] === "number" ? row[1] : parseFloat(String(row[1] ?? 0)) || 0,
    }));
    return <LineChart data={data} xLabel={columns[0]} yLabel={columns[1]} />;
  }

  return (
    <p className="text-xs text-gray-500">
      Chart not available for this result type. Switch to the Table tab to see the data.
    </p>
  );
}

function TableTab({ result }: { result: QuestionResponse }) {
  const { columns, rows, row_count } = result;
  const visible = rows.slice(0, 200);

  return (
    <div className="overflow-x-auto">
      <p className="mb-2 text-xs text-gray-500">
        {row_count} row{row_count !== 1 ? "s" : ""}
        {row_count > 200 ? ` — showing first 200` : ""}
      </p>
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-800">
            {columns.map((col) => (
              <th
                key={col}
                className="pb-2 pr-5 text-left font-medium text-gray-400 uppercase tracking-wide"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {visible.map((row, i) => (
            <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
              {row.map((cell, j) => (
                <td key={j} className="py-1.5 pr-5 font-mono text-gray-200">
                  {cell == null ? <span className="text-gray-600">null</span> : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AssumptionsTab({ result }: { result: QuestionResponse }) {
  const { assumptions, caveats } = result;

  if (assumptions.length === 0 && caveats.length === 0) {
    return (
      <p className="text-xs text-gray-600">No assumptions or caveats for this answer.</p>
    );
  }

  return (
    <div className="space-y-5">
      {assumptions.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
            Assumptions made
          </p>
          <ul className="space-y-1.5">
            {assumptions.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
                <span className="mt-0.5 text-anchor-500 shrink-0">→</span>
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}
      {caveats.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-yellow-600">
            Caveats
          </p>
          <ul className="space-y-1.5">
            {caveats.map((c, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-yellow-400">
                <span className="mt-0.5 shrink-0">!</span>
                {c}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ProvenanceTab({ result }: { result: QuestionResponse }) {
  // Type guard for provenance steps
  const provenanceSteps: Array<{ step: string; output?: Record<string, unknown> }> = (() => {
    const raw = result.provenance?.["steps"];
    return Array.isArray(raw)
      ? (raw as Array<{ step: string; output?: Record<string, unknown> }>)
      : [];
  })();

  return (
    <div className="space-y-5">
      {/* Semantic mappings */}
      {result.semantic_mappings.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
            Business terms resolved
          </p>
          <div className="flex flex-wrap gap-2">
            {result.semantic_mappings.map((m, i) => (
              <MappingChip key={i} mapping={m} />
            ))}
          </div>
        </div>
      )}

      {/* Pipeline steps */}
      {provenanceSteps.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
            Pipeline steps
          </p>
          <div className="space-y-1">
            {provenanceSteps.map((s, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-gray-400">
                <span className="font-mono text-green-500">✓</span>
                <span className="font-mono">{s.step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.semantic_mappings.length === 0 && provenanceSteps.length === 0 && (
        <p className="text-xs text-gray-600">No provenance data available.</p>
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
    <div
      className={`rounded-full border px-2.5 py-1 text-xs flex items-center gap-1.5 ${typeColor}`}
    >
      <span>&quot;{mapping.phrase}&quot;</span>
      <span className="text-gray-600">→</span>
      <span className="font-mono">{mapping.resolved_to}</span>
      {mapping.via !== "exact" && (
        <span className="text-gray-500">({mapping.via})</span>
      )}
    </div>
  );
}
