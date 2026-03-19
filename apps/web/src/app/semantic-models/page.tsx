"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  deleteSemanticModel,
  exportSemanticModelYaml,
  listSemanticModels,
  type SemanticModel,
} from "@/lib/api";

export default function SemanticModelsPage() {
  const [models, setModels] = useState<SemanticModel[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listSemanticModels();
      setModels(data.semantic_models);
      setTotal(data.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load models");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(id: string, name: string) {
    if (!confirm(`Delete semantic model "${name}"? This cannot be undone.`)) return;
    try {
      await deleteSemanticModel(id);
      setModels((prev) => prev.filter((m) => m.id !== id));
      setTotal((prev) => prev - 1);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Delete failed");
    }
  }

  async function handleExport(id: string, name: string) {
    try {
      const yaml = await exportSemanticModelYaml(id);
      const blob = new Blob([yaml], { type: "text/yaml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${name}.yml`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Export failed");
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="mx-auto max-w-6xl flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-anchor-500 font-mono text-sm hover:underline">
              MetricAnchor
            </Link>
            <span className="text-gray-600">/</span>
            <span className="text-gray-300 text-sm font-medium">Semantic Models</span>
          </div>
          <Link
            href="/semantic-models/new"
            className="rounded-md bg-anchor-500 px-4 py-2 text-sm font-medium text-white hover:bg-anchor-600 transition-colors"
          >
            + New Model
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-100">Semantic Models</h1>
          <p className="mt-1 text-sm text-gray-400">
            Define business concepts — metrics, dimensions, synonyms — so the AI
            answers questions consistently and with full transparency.
          </p>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20 text-gray-500 text-sm">
            Loading models...
          </div>
        )}

        {error && (
          <div className="rounded-md border border-red-700 bg-red-900/20 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {!loading && !error && total === 0 && (
          <div className="rounded-xl border border-dashed border-gray-700 bg-gray-900/40 py-20 text-center">
            <p className="text-gray-400 text-sm">No semantic models yet.</p>
            <p className="mt-1 text-gray-500 text-xs">
              Create one to start grounding AI answers in your business definitions.
            </p>
            <Link
              href="/semantic-models/new"
              className="mt-6 inline-block rounded-md bg-anchor-500 px-5 py-2 text-sm font-medium text-white hover:bg-anchor-600 transition-colors"
            >
              Create your first model
            </Link>
          </div>
        )}

        {!loading && !error && total > 0 && (
          <div className="space-y-4">
            <p className="text-xs text-gray-500">{total} model{total !== 1 ? "s" : ""}</p>
            {models.map((model) => (
              <ModelCard
                key={model.id}
                model={model}
                onDelete={handleDelete}
                onExport={handleExport}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function ModelCard({
  model,
  onDelete,
  onExport,
}: {
  model: SemanticModel;
  onDelete: (id: string, name: string) => void;
  onExport: (id: string, name: string) => void;
}) {
  const def = model.definition;
  const metricCount = def.metrics?.length ?? 0;
  const dimensionCount = def.dimensions?.length ?? 0;
  const synonymCount = def.synonyms?.length ?? 0;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-6 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-base font-semibold text-gray-100">{model.name}</h2>
            <span className="rounded-full bg-anchor-900 px-2 py-0.5 text-xs text-anchor-300 font-mono">
              {def.dataset}
            </span>
          </div>
          {def.description && (
            <p className="mt-1 text-sm text-gray-400 line-clamp-2">{def.description}</p>
          )}
          <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
            <span>
              <span className="font-semibold text-gray-300">{metricCount}</span> metric{metricCount !== 1 ? "s" : ""}
            </span>
            <span>
              <span className="font-semibold text-gray-300">{dimensionCount}</span> dimension{dimensionCount !== 1 ? "s" : ""}
            </span>
            {synonymCount > 0 && (
              <span>
                <span className="font-semibold text-gray-300">{synonymCount}</span> synonym{synonymCount !== 1 ? "s" : ""}
              </span>
            )}
            {def.grain && (
              <span className="italic text-gray-600">{def.grain}</span>
            )}
          </div>
          {/* Metric chips */}
          {metricCount > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {def.metrics.slice(0, 5).map((m) => (
                <span
                  key={m.name}
                  className="rounded bg-gray-800 px-2 py-0.5 text-xs font-mono text-gray-300"
                >
                  {m.name}
                </span>
              ))}
              {metricCount > 5 && (
                <span className="rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-500">
                  +{metricCount - 5} more
                </span>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => onExport(model.id, model.name)}
            className="rounded px-3 py-1.5 text-xs text-gray-400 hover:bg-gray-800 hover:text-gray-200 transition-colors"
          >
            Export YAML
          </button>
          <Link
            href={`/semantic-models/${model.id}`}
            className="rounded px-3 py-1.5 text-xs text-anchor-400 hover:bg-anchor-900/40 transition-colors"
          >
            Edit
          </Link>
          <button
            onClick={() => onDelete(model.id, model.name)}
            className="rounded px-3 py-1.5 text-xs text-red-500 hover:bg-red-900/20 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
