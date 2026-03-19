"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import FileUpload from "@/components/FileUpload";
import type { Dataset } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();

  const handleSuccess = (dataset: Dataset) => {
    router.push(`/datasets/${dataset.id}`);
  };

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
          <span className="text-sm font-medium text-gray-500">Upload</span>
        </div>
      </header>

      <main className="mx-auto max-w-xl px-6 py-16">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Upload a dataset</h1>
          <p className="mt-2 text-sm text-gray-500">
            Drop a CSV or Parquet file. MetricAnchor will profile every column automatically —
            null rates, distinct counts, min/max, and sample values.
          </p>
        </div>

        <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
          <FileUpload onSuccess={handleSuccess} />
        </div>

        <div className="mt-6 rounded-xl bg-blue-50 p-4 text-sm text-blue-700">
          <p className="font-medium">Tip — try the sample datasets</p>
          <p className="mt-1 text-blue-600">
            Upload any file from{" "}
            <code className="rounded bg-blue-100 px-1 text-xs">sample_data/</code>{" "}
            to explore a pre-built semantic model.
          </p>
        </div>
      </main>
    </div>
  );
}
