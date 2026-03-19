"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import SemanticModelWizard from "@/components/SemanticModelWizard";
import YamlEditor from "@/components/YamlEditor";
import { listDatasets, type Dataset } from "@/lib/api";

type Mode = "wizard" | "yaml";

export default function NewSemanticModelPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("wizard");
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listDatasets()
      .then((r) => setDatasets(r.datasets))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load datasets"))
      .finally(() => setLoading(false));
  }, []);

  function handleSuccess(modelId: string) {
    router.push(`/semantic-models/${modelId}`);
  }

  function handleCancel() {
    router.push("/semantic-models");
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="mx-auto max-w-4xl flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-anchor-500 font-mono text-sm hover:underline">
              MetricAnchor
            </Link>
            <span className="text-gray-600">/</span>
            <Link href="/semantic-models" className="text-gray-400 text-sm hover:text-gray-200">
              Semantic Models
            </Link>
            <span className="text-gray-600">/</span>
            <span className="text-gray-300 text-sm">New</span>
          </div>

          {/* Mode toggle */}
          <div className="flex items-center gap-1 rounded-md border border-gray-700 bg-gray-800 p-1">
            <button
              onClick={() => setMode("wizard")}
              className={`rounded px-3 py-1 text-xs font-medium transition-colors ${
                mode === "wizard"
                  ? "bg-anchor-500 text-white"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              Guided wizard
            </button>
            <button
              onClick={() => setMode("yaml")}
              className={`rounded px-3 py-1 text-xs font-medium transition-colors ${
                mode === "yaml"
                  ? "bg-anchor-500 text-white"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              YAML editor
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-10">
        {loading && (
          <p className="text-sm text-gray-500">Loading datasets...</p>
        )}

        {error && (
          <div className="rounded-md border border-red-700 bg-red-900/20 p-4 text-sm text-red-300">
            {error}
            <br />
            <Link href="/datasets/upload" className="underline mt-1 inline-block">
              Upload a dataset first
            </Link>
          </div>
        )}

        {!loading && !error && datasets.length === 0 && (
          <div className="rounded-xl border border-dashed border-gray-700 bg-gray-900/40 py-16 text-center">
            <p className="text-gray-400 text-sm">No datasets found.</p>
            <p className="text-gray-500 text-xs mt-1">
              Upload a CSV or Parquet file before creating a semantic model.
            </p>
            <Link
              href="/datasets/upload"
              className="mt-6 inline-block rounded-md bg-anchor-500 px-5 py-2 text-sm font-medium text-white hover:bg-anchor-600 transition-colors"
            >
              Upload dataset
            </Link>
          </div>
        )}

        {!loading && !error && datasets.length > 0 && (
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-8">
            {mode === "wizard" ? (
              <SemanticModelWizard
                datasets={datasets}
                onSuccess={handleSuccess}
                onCancel={handleCancel}
              />
            ) : (
              <YamlEditor
                datasetId={datasets[0].id}
                onSuccess={handleSuccess}
                onCancel={handleCancel}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}
