"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import QuestionResult from "@/components/QuestionResult";
import {
  askQuestion,
  listDatasets,
  listQuestions,
  listSemanticModels,
  type Dataset,
  type QuestionResponse,
} from "@/lib/api";

const EXAMPLE_QUESTIONS = [
  "What is total revenue?",
  "Show revenue by product category",
  "Top 5 categories by revenue",
  "Revenue last month",
  "Revenue trend over time",
  "What was revenue in Q1?",
];

const SAVED_QUERIES_KEY = "metricanchor:saved_queries";

interface SavedQuery {
  id: string;
  text: string;
  savedAt: string;
}

function loadSavedQueries(): SavedQuery[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(SAVED_QUERIES_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function saveQuery(text: string): SavedQuery[] {
  const existing = loadSavedQueries();
  if (existing.some((q) => q.text === text)) return existing;
  const next: SavedQuery[] = [
    { id: crypto.randomUUID(), text, savedAt: new Date().toISOString() },
    ...existing,
  ].slice(0, 20);
  localStorage.setItem(SAVED_QUERIES_KEY, JSON.stringify(next));
  return next;
}

function removeSavedQuery(id: string): SavedQuery[] {
  const next = loadSavedQueries().filter((q) => q.id !== id);
  localStorage.setItem(SAVED_QUERIES_KEY, JSON.stringify(next));
  return next;
}

export default function AskPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [hasModel, setHasModel] = useState<boolean | null>(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QuestionResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [devMode, setDevMode] = useState(false);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [history, setHistory] = useState<QuestionResponse[]>([]);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load datasets
  useEffect(() => {
    listDatasets().then((r) => {
      setDatasets(r.datasets);
      if (r.datasets.length > 0) setSelectedDatasetId(r.datasets[0].id);
    });
  }, []);

  // Load semantic model status
  useEffect(() => {
    if (!selectedDatasetId) {
      setHasModel(null);
      return;
    }
    listSemanticModels(selectedDatasetId).then((r) => {
      setHasModel(r.total > 0);
    });
  }, [selectedDatasetId]);

  // Load saved queries and history
  useEffect(() => {
    setSavedQueries(loadSavedQueries());
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) return;
    listQuestions(selectedDatasetId, 20)
      .then((r) => setHistory(r.questions))
      .catch(() => {});
  }, [selectedDatasetId]);

  // Cmd+Shift+D toggles dev mode
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key.toLowerCase() === "d") {
        e.preventDefault();
        setDevMode((v) => !v);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const handleSubmit = useCallback(
    async (q?: string) => {
      const text = (q ?? question).trim();
      if (!text || !selectedDatasetId || loading) return;

      setLoading(true);
      setError(null);
      try {
        const result = await askQuestion({ question: text, dataset_id: selectedDatasetId });
        setResults((prev) => [result, ...prev]);
        setHistory((prev) => [result, ...prev.slice(0, 19)]);
        setQuestion("");
        inputRef.current?.focus();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Request failed");
      } finally {
        setLoading(false);
      }
    },
    [question, selectedDatasetId, loading]
  );

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleSaveQuery(text: string) {
    setSavedQueries(saveQuery(text));
  }

  function handleRemoveSaved(id: string) {
    setSavedQueries(removeSavedQuery(id));
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      {/* Top nav */}
      <header className="sticky top-0 z-10 border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-screen-xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-anchor-500">
                <svg className="h-3.5 w-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="font-semibold text-sm text-gray-100">MetricAnchor</span>
            </Link>
            <span className="text-gray-700">/</span>
            <span className="text-sm text-gray-300 font-medium">Ask</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/datasets" className="text-xs text-gray-500 hover:text-gray-300 transition-colors">Datasets</Link>
            <Link href="/semantic-models" className="text-xs text-gray-500 hover:text-gray-300 transition-colors">Models</Link>
            <button
              onClick={() => setDevMode((v) => !v)}
              aria-pressed={devMode}
              title="Toggle developer mode (⌘⇧D)"
              className={`rounded-md border px-2.5 py-1 text-xs font-mono transition-colors ${
                devMode
                  ? "border-anchor-600 bg-anchor-900/40 text-anchor-300"
                  : "border-gray-700 text-gray-500 hover:border-gray-600 hover:text-gray-300"
              }`}
            >
              DEV
            </button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 mx-auto w-full max-w-screen-xl">
        {/* Left sidebar */}
        <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-gray-800 px-4 py-6 gap-6">
          {/* Dataset selector */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Dataset</p>
            {datasets.length === 0 ? (
              <p className="text-xs text-gray-600">
                No datasets.{" "}
                <Link href="/datasets/upload" className="text-anchor-400 underline">
                  Upload one
                </Link>
              </p>
            ) : (
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full rounded-md border border-gray-700 bg-gray-900 px-3 py-1.5 text-xs text-gray-200 focus:border-anchor-500 focus:outline-none"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            )}
            {hasModel === false && selectedDatasetId && (
              <p className="mt-2 text-xs text-yellow-500">
                No semantic model.{" "}
                <Link href="/semantic-models/new" className="underline">
                  Create one
                </Link>
              </p>
            )}
          </div>

          {/* Saved queries */}
          {savedQueries.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Saved queries</p>
              <ul className="space-y-1">
                {savedQueries.map((q) => (
                  <li key={q.id} className="group flex items-center gap-1.5">
                    <button
                      onClick={() => handleSubmit(q.text)}
                      disabled={!selectedDatasetId || loading}
                      className="flex-1 text-left text-xs text-gray-400 hover:text-anchor-300 truncate disabled:opacity-40"
                      title={q.text}
                    >
                      {q.text}
                    </button>
                    <button
                      onClick={() => handleRemoveSaved(q.id)}
                      className="shrink-0 opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition-opacity"
                      aria-label="Remove saved query"
                    >
                      <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recent history */}
          {history.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">Recent</p>
              <ul className="space-y-1">
                {history.slice(0, 10).map((q) => (
                  <li key={q.id} className="group flex items-center gap-1.5">
                    <button
                      onClick={() => handleSubmit(q.question)}
                      disabled={!selectedDatasetId || loading}
                      className="flex-1 text-left text-xs text-gray-500 hover:text-gray-300 truncate disabled:opacity-40"
                      title={q.question}
                    >
                      {q.question}
                    </button>
                    <button
                      onClick={() => handleSaveQuery(q.question)}
                      className="shrink-0 opacity-0 group-hover:opacity-100 text-gray-600 hover:text-anchor-400 transition-opacity"
                      aria-label="Save query"
                      title="Save"
                    >
                      <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0 px-6 py-8">
          {/* Mobile dataset selector */}
          <div className="lg:hidden mb-4">
            {datasets.length > 0 && (
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-200 focus:border-anchor-500 focus:outline-none"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            )}
          </div>

          {/* Question input */}
          <div className="mb-6 space-y-3">
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
                <div className="flex items-center gap-3">
                  <p className="text-xs text-gray-600">Enter to submit · Shift+Enter for newline</p>
                  {question.trim() && (
                    <button
                      onClick={() => handleSaveQuery(question.trim())}
                      className="text-xs text-gray-600 hover:text-anchor-400 transition-colors"
                      title="Save this query"
                    >
                      Save query
                    </button>
                  )}
                </div>
                <button
                  onClick={() => handleSubmit()}
                  disabled={!question.trim() || !selectedDatasetId || loading}
                  className="rounded-md bg-anchor-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-anchor-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
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
                    className="rounded-full border border-gray-700 bg-gray-900 px-3 py-1 text-xs text-gray-400 hover:border-anchor-600 hover:text-anchor-300 disabled:opacity-40 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="mb-4 rounded-md border border-red-700 bg-red-900/20 p-4 text-sm text-red-300">
              {error}
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="mb-4 rounded-xl border border-gray-800 bg-gray-900 p-5">
              <div className="flex items-center gap-3 text-sm text-gray-400 mb-3">
                <PipelineSpinner />
                Running pipeline…
              </div>
              <div className="space-y-2">
                {["Parsing question", "Mapping semantic terms", "Generating SQL", "Executing query", "Formatting answer"].map((step) => (
                  <div key={step} className="flex items-center gap-2 text-xs text-gray-600">
                    <span className="h-1.5 w-1.5 rounded-full bg-anchor-500 animate-pulse shrink-0" />
                    {step}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty state */}
          {!loading && results.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              {datasets.length === 0 ? (
                <>
                  <p className="text-sm text-gray-400 mb-3">No datasets yet.</p>
                  <Link
                    href="/datasets/upload"
                    className="rounded-lg bg-anchor-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-anchor-400 transition-colors"
                  >
                    Upload your first dataset
                  </Link>
                </>
              ) : (
                <>
                  <p className="text-sm text-gray-500 mb-1">Ask a question about your data.</p>
                  <p className="text-xs text-gray-600">
                    Every answer shows its SQL, mappings, and confidence level.
                  </p>
                </>
              )}
            </div>
          )}

          {/* Results */}
          <div className="space-y-5">
            {results.map((r) => (
              <QuestionResult key={r.id} result={r} devMode={devMode} />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

function PipelineSpinner() {
  return (
    <svg className="h-4 w-4 animate-spin text-anchor-400" fill="none" viewBox="0 0 24 24" aria-hidden>
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}
