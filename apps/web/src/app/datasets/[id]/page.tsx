"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getDataset, getDatasetRows, type Dataset, type RowsResponse } from "@/lib/api";
import ColumnProfileCard from "@/components/ColumnProfile";
import DataTable from "@/components/DataTable";

type Tab = "profile" | "data";

function FormatBadge({ format }: { format: string }) {
  const colors: Record<string, string> = {
    csv: "bg-green-100 text-green-700",
    parquet: "bg-blue-100 text-blue-700",
  };
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium uppercase ${colors[format] ?? "bg-gray-100 text-gray-600"}`}>
      {format}
    </span>
  );
}

export default function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [rows, setRows] = useState<RowsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("profile");
  const [loading, setLoading] = useState(true);
  const [rowsLoading, setRowsLoading] = useState(false);
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

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-gray-400">
        Loading dataset…
      </div>
    );
  }

  if (error || !dataset) {
    return (
      <div className="min-h-screen bg-gray-50 px-6 py-20 text-center">
        <p className="text-lg font-medium text-red-600">{error ?? "Dataset not found."}</p>
        <Link href="/datasets" className="mt-4 inline-block text-sm text-anchor-600 underline">
          Back to datasets
        </Link>
      </div>
    );
  }

  const profile = dataset.profile;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-anchor-600">
              <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="font-semibold text-gray-900">MetricAnchor</span>
          </Link>
          <span className="text-gray-300">/</span>
          <Link href="/datasets" className="text-sm text-gray-500 hover:text-gray-700">
            Datasets
          </Link>
          <span className="text-gray-300">/</span>
          <span className="text-sm font-medium text-gray-500 truncate max-w-xs">{dataset.name}</span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* Dataset meta */}
        <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{dataset.name}</h1>
              <FormatBadge format={dataset.file_format} />
            </div>
            <p className="mt-1 text-sm text-gray-400">{dataset.original_filename}</p>
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            {dataset.row_count !== null && (
              <div className="text-right">
                <p className="text-xl font-bold text-gray-900">{dataset.row_count.toLocaleString()}</p>
                <p className="text-xs text-gray-400">rows</p>
              </div>
            )}
            {dataset.column_count !== null && (
              <div className="text-right">
                <p className="text-xl font-bold text-gray-900">{dataset.column_count}</p>
                <p className="text-xs text-gray-400">columns</p>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-1 rounded-lg border border-gray-100 bg-gray-50 p-1 w-fit">
          {(["profile", "data"] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors capitalize ${
                activeTab === tab
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab === "profile" ? "Schema Profile" : "Sample Data"}
            </button>
          ))}
        </div>

        {/* Tab: Schema Profile */}
        {activeTab === "profile" && profile && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {profile.columns.map((col) => (
              <ColumnProfileCard key={col.name} column={col} />
            ))}
          </div>
        )}

        {activeTab === "profile" && !profile && (
          <div className="rounded-xl border border-dashed border-gray-200 py-16 text-center text-sm text-gray-400">
            No schema profile available for this dataset.
          </div>
        )}

        {/* Tab: Sample Data */}
        {activeTab === "data" && (
          rowsLoading ? (
            <div className="flex items-center justify-center py-16 text-sm text-gray-400">
              Loading rows…
            </div>
          ) : rows ? (
            <DataTable columns={rows.columns} rows={rows.rows} />
          ) : null
        )}
      </main>
    </div>
  );
}
