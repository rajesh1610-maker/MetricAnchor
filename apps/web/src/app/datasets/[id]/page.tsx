"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  getDataset,
  getDatasetRows,
  listSemanticModels,
  type Dataset,
  type RowsResponse,
  type SemanticModel,
} from "@/lib/api";
import ColumnProfileCard from "@/components/ColumnProfile";
import DataTable from "@/components/DataTable";

type Tab = "profile" | "data" | "model";

export default function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [rows, setRows] = useState<RowsResponse | null>(null);
  const [models, setModels] = useState<SemanticModel[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>("profile");
  const [loading, setLoading] = useState(true);
  const [rowsLoading, setRowsLoading] = useState(false);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDataset(id)
      .then(setDataset)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (activeTab !== "data" || rows) return;
    setRowsLoading(true);
    getDatasetRows(id, 100)
      .then(setRows)
      .catch((err) => setError(err.message))
      .finally(() => setRowsLoading(false));
  }, [activeTab, id, rows]);

  useEffect(() => {
    if (activeTab !== "model") return;
    setModelsLoading(true);
    listSemanticModels(id)
      .then((r) => setModels(r.semantic_models))
      .catch(() => {})
      .finally(() => setModelsLoading(false));
  }, [activeTab, id]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-950 text-sm text-gray-400">
        Loading dataset…
      </div>
    );
  }

  if (error || !dataset) {
    return (
      <div className="min-h-screen bg-gray-950 px-6 py-20 text-center">
        <p className="text-base font-medium text-red-400">{error ?? "Dataset not found."}</p>
        <Link href="/datasets" className="mt-4 inline-block text-sm text-anchor-400 underline">
          Back to datasets
        </Link>
      </div>
    );
  }

  const profile = dataset.profile;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-gray-800 bg-gray-950/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-2 text-sm min-w-0">
            <Link href="/" className="flex items-center gap-1.5 shrink-0">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-anchor-500">
                <svg className="h-3.5 w-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="font-semibold text-gray-100">MetricAnchor</span>
            </Link>
            <span className="text-gray-700">/</span>
            <Link href="/datasets" className="text-gray-500 hover:text-gray-300 transition-colors shrink-0">
              Datasets
            </Link>
            <span className="text-gray-700">/</span>
            <span className="text-gray-300 truncate max-w-[200px]">{dataset.name}</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Link
              href={`/semantic-models/new?dataset_id=${id}`}
              className="rounded-md border border-gray-700 px-3 py-1.5 text-xs text-gray-400 hover:border-gray-600 hover:text-gray-200 transition-colors"
            >
              + Semantic model
            </Link>
            <button
              onClick={() => router.push(`/ask?dataset_id=${id}`)}
              className="rounded-md bg-anchor-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-anchor-400 transition-colors"
            >
              Ask questions
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {/* Dataset meta */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-gray-100">{dataset.name}</h1>
              <span className="rounded-full border border-gray-700 bg-gray-800 px-2.5 py-0.5 text-xs font-medium uppercase text-gray-400">
                {dataset.file_format}
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-500 font-mono">{dataset.original_filename}</p>
          </div>
          <div className="flex gap-6 text-sm">
            {dataset.row_count !== null && (
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-100 tabular-nums">
                  {dataset.row_count.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500">rows</p>
              </div>
            )}
            {dataset.column_count !== null && (
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-100 tabular-nums">
                  {dataset.column_count}
                </p>
                <p className="text-xs text-gray-500">columns</p>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex border-b border-gray-800">
          {(
            [
              { id: "profile" as Tab, label: "Schema Profile" },
              { id: "data" as Tab, label: "Sample Data" },
              { id: "model" as Tab, label: "Semantic Model" },
            ] as const
          ).map(({ id: tabId, label }) => (
            <button
              key={tabId}
              onClick={() => setActiveTab(tabId)}
              className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tabId
                  ? "border-anchor-500 text-anchor-400"
                  : "border-transparent text-gray-500 hover:text-gray-300"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Tab: Schema Profile */}
        {activeTab === "profile" && (
          profile ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {profile.columns.map((col) => (
                <ColumnProfileCard key={col.name} column={col} />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-800 py-16 text-center text-sm text-gray-600">
              No schema profile available for this dataset.
            </div>
          )
        )}

        {/* Tab: Sample Data */}
        {activeTab === "data" && (
          rowsLoading ? (
            <div className="flex items-center justify-center py-16 text-sm text-gray-500">
              Loading rows…
            </div>
          ) : rows ? (
            <DataTable columns={rows.columns} rows={rows.rows} />
          ) : null
        )}

        {/* Tab: Semantic Model */}
        {activeTab === "model" && (
          modelsLoading ? (
            <div className="flex items-center justify-center py-16 text-sm text-gray-500">
              Loading models…
            </div>
          ) : models.length === 0 ? (
            <div className="rounded-xl border border-dashed border-gray-800 py-16 text-center">
              <p className="text-sm text-gray-500 mb-4">
                No semantic model defined for this dataset yet.
              </p>
              <p className="text-xs text-gray-600 mb-6 max-w-sm mx-auto leading-relaxed">
                A semantic model maps your column names to business terms like "revenue" and "churn",
                so the AI can answer questions accurately.
              </p>
              <Link
                href={`/semantic-models/new?dataset_id=${id}`}
                className="inline-flex rounded-lg bg-anchor-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-anchor-400 transition-colors"
              >
                Create semantic model
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {models.map((model) => (
                <ModelSummaryCard key={model.id} model={model} datasetId={id} />
              ))}
            </div>
          )
        )}
      </main>
    </div>
  );
}

function ModelSummaryCard({ model, datasetId }: { model: SemanticModel; datasetId: string }) {
  const def = model.definition;
  const metricCount = def.metrics?.length ?? 0;
  const dimCount = def.dimensions?.length ?? 0;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-100">{model.name}</h3>
          {def.description && (
            <p className="text-xs text-gray-500 mt-0.5">{def.description}</p>
          )}
        </div>
        <Link
          href={`/semantic-models/${model.id}`}
          className="text-xs text-anchor-400 hover:text-anchor-300 transition-colors"
        >
          Edit model →
        </Link>
      </div>

      <div className="flex gap-6 text-xs mb-4">
        <div>
          <p className="text-gray-600">Metrics</p>
          <p className="font-semibold text-gray-200 tabular-nums">{metricCount}</p>
        </div>
        <div>
          <p className="text-gray-600">Dimensions</p>
          <p className="font-semibold text-gray-200 tabular-nums">{dimCount}</p>
        </div>
        {def.time_column && (
          <div>
            <p className="text-gray-600">Time column</p>
            <p className="font-mono text-gray-300">{def.time_column}</p>
          </div>
        )}
      </div>

      {metricCount > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {def.metrics.map((m) => (
            <span
              key={m.name}
              className="rounded-full border border-anchor-800 bg-anchor-950/40 px-2.5 py-0.5 text-xs text-anchor-300"
            >
              {m.name}
            </span>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-800">
        <Link
          href={`/ask?dataset_id=${datasetId}`}
          className="text-xs text-anchor-400 hover:text-anchor-300 transition-colors"
        >
          Ask questions using this model →
        </Link>
      </div>
    </div>
  );
}
