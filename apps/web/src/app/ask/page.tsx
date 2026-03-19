"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import QuestionResult from "@/components/QuestionResult";
import {
  askQuestion,
  listDatasets,
  listSemanticModels,
  type Dataset,
  type QuestionResponse,
} from "@/lib/api";

const EXAMPLE_QUESTIONS = [
  "What is total revenue?",
  "Show revenue by product category",
  "What are the top 5 categories by revenue?",
  "Revenue last month",
  "Revenue trend over time",
];

export default function AskPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [hasModel, setHasModel] = useState<boolean | null>(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QuestionResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    listDatasets().then((r) => {
      setDatasets(r.datasets);
      if (r.datasets.length > 0) setSelectedDatasetId(r.datasets[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) {
      setHasModel(null);
      return;
    }
    listSemanticModels(selectedDatasetId).then((r) => {
      setHasModel(r.total > 0);
    });
  }, [selectedDatasetId]);

  async function handleSubmit(q?: string) {
    const text = (q ?? question).trim();
    if (!text || !selectedDatasetId || loading) return;

    setLoading(true);
    setError(null);
    try {
      const result = await askQuestion({ question: text, dataset_id: selectedDatasetId });
      setResults((prev) => [result, ...prev]);
      setQuestion("");
      inputRef.current?.focus();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900 sticky top-0 z-10">
        <div className="mx-auto max-w-4xl flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-anchor-500 font-mono text-sm hover:underline">
              MetricAnchor
            </Link>
            <span className="text-gray-600">/</span>
            <span className="text-gray-300 text-sm font-medium">Ask</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/datasets" className="text-xs text-gray-500 hover:text-gray-300">
              Datasets
            </Link>
            <Link href="/semantic-models" className="text-xs text-gray-500 hover:text-gray-300">
              Models
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-10 space-y-8">
        {/* Intro */}
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Ask a question</h1>
          <p className="mt-1 text-sm text-gray-400">
            Every answer shows its SQL, business term mappings, assumptions, and confidence level.
          </p>
        </div>

        {/* Dataset selector */}
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex-1 min-w-48">
            <label className="block text-xs text-gray-500 mb-1.5">Dataset</label>
            {datasets.length === 0 ? (
              <p className="text-sm text-gray-500">
                No datasets.{" "}
                <Link href="/datasets/upload" className="text-anchor-400 underline">
                  Upload one
                </Link>
                .
              </p>
            ) : (
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-anchor-500 focus:outline-none"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.original_filename})
                  </option>
                ))}
              </select>
            )}
          </div>

          {hasModel === false && selectedDatasetId && (
            <div className="text-xs text-yellow-400 border border-yellow-700 bg-yellow-900/20 rounded-md px-3 py-2">
              No semantic model for this dataset.{" "}
              <Link href="/semantic-models/new" className="underline">
                Create one
              </Link>{" "}
              to enable accurate answers.
            </div>
          )}
        </div>

        {/* Question input */}
        <div className="space-y-3">
          <div className="relative rounded-xl border border-gray-700 bg-gray-900 focus-within:border-anchor-500 transition-colors">
            <textarea
              ref={inputRef}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your data… e.g. 'What was revenue last month by category?'"
              rows={3}
              disabled={!selectedDatasetId || loading}
              className="w-full bg-transparent px-4 py-3 text-sm text-gray-100 placeholder-gray-600 focus:outline-none resize-none disabled:opacity-50"
            />
            <div className="flex items-center justify-between px-4 py-2 border-t border-gray-800">
              <p className="text-xs text-gray-600">Press Enter to submit · Shift+Enter for newline</p>
              <button
                onClick={() => handleSubmit()}
                disabled={!question.trim() || !selectedDatasetId || loading}
                className="rounded-md bg-anchor-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-anchor-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Thinking…" : "Ask"}
              </button>
            </div>
          </div>

          {/* Example questions */}
          {results.length === 0 && (
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSubmit(q)}
                  disabled={!selectedDatasetId || loading}
                  className="rounded-full border border-gray-700 bg-gray-800/50 px-3 py-1 text-xs text-gray-400 hover:border-anchor-500 hover:text-anchor-300 disabled:opacity-40 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-md border border-red-700 bg-red-900/20 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <PipelineSpinner />
              Running pipeline…
            </div>
            <div className="mt-4 space-y-2 text-xs text-gray-600">
              {["Parsing question", "Mapping semantic terms", "Generating SQL", "Executing query", "Formatting answer"].map((step) => (
                <div key={step} className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-anchor-500 animate-pulse" />
                  {step}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        <div className="space-y-6">
          {results.map((r) => (
            <QuestionResult key={r.id} result={r} />
          ))}
        </div>
      </main>
    </div>
  );
}

function PipelineSpinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin text-anchor-400"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}
