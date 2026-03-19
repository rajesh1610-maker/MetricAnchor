"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listDatasets, type Dataset } from "@/lib/api";

function FormatBadge({ format }: { format: string }) {
  const colors: Record<string, string> = {
    csv: "bg-green-100 text-green-700",
    parquet: "bg-blue-100 text-blue-700",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium uppercase ${colors[format] ?? "bg-gray-100 text-gray-600"}`}>
      {format}
    </span>
  );
}

function DatasetCard({ dataset }: { dataset: Dataset }) {
  const date = new Date(dataset.created_at).toLocaleDateString("en-US", {
    month: "short", day: "numeric", year: "numeric",
  });

  return (
    <Link href={`/datasets/${dataset.id}`}>
      <div className="group rounded-xl border border-gray-100 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
        <div className="mb-3 flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="truncate font-semibold text-gray-900 group-hover:text-anchor-600">
              {dataset.name}
            </p>
            <p className="mt-0.5 truncate text-xs text-gray-400">{dataset.original_filename}</p>
          </div>
          <FormatBadge format={dataset.file_format} />
        </div>

        <div className="flex items-center gap-4 text-xs text-gray-500">
          {dataset.row_count !== null && (
            <span>{dataset.row_count.toLocaleString()} rows</span>
          )}
          {dataset.column_count !== null && (
            <span>{dataset.column_count} columns</span>
          )}
        </div>

        <p className="mt-3 text-xs text-gray-300">{date}</p>
      </div>
    </Link>
  );
}

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listDatasets()
      .then((res) => setDatasets(res.datasets))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-3">
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
            <span className="text-sm font-medium text-gray-500">Datasets</span>
          </div>
          <Link
            href="/datasets/upload"
            className="rounded-lg bg-anchor-600 px-4 py-2 text-sm font-semibold text-white hover:bg-anchor-700"
          >
            Upload dataset
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Datasets</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload CSV or Parquet files and explore their schema profiles.
          </p>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20 text-sm text-gray-400">
            Loading…
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            Could not load datasets: {error}
          </div>
        )}

        {!loading && !error && datasets.length === 0 && (
          <div className="rounded-2xl border-2 border-dashed border-gray-200 py-20 text-center">
            <p className="text-lg font-medium text-gray-400">No datasets yet</p>
            <p className="mt-1 text-sm text-gray-300">Upload a CSV or Parquet file to get started.</p>
            <Link
              href="/datasets/upload"
              className="mt-6 inline-block rounded-lg bg-anchor-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-anchor-700"
            >
              Upload your first dataset
            </Link>
          </div>
        )}

        {datasets.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {datasets.map((d) => (
              <DatasetCard key={d.id} dataset={d} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
