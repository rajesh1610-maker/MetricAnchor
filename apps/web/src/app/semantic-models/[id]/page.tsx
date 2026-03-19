"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import YamlEditor from "@/components/YamlEditor";
import {
  exportSemanticModelYaml,
  getSemanticModel,
  type SemanticModel,
} from "@/lib/api";

export default function SemanticModelDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [model, setModel] = useState<SemanticModel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [exportedYaml, setExportedYaml] = useState<string | null>(null);

  useEffect(() => {
    getSemanticModel(id)
      .then(setModel)
      .catch((e) => setError(e instanceof Error ? e.message : "Not found"))
      .finally(() => setLoading(false));
  }, [id]);

  async function loadYaml() {
    try {
      const yaml = await exportSemanticModelYaml(id);
      setExportedYaml(yaml);
    } catch {
      setExportedYaml(null);
    }
  }

  function handleEditSuccess() {
    setEditing(false);
    setExportedYaml(null);
    getSemanticModel(id).then(setModel);
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center text-gray-500 text-sm">
        Loading...
      </div>
    );
  }

  if (error || !model) {
    return (
      <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center gap-4">
        <p className="text-red-400 text-sm">{error ?? "Model not found"}</p>
        <Link href="/semantic-models" className="text-anchor-400 text-sm underline">
          Back to models
        </Link>
      </div>
    );
  }

  const def = model.definition;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="mx-auto max-w-5xl flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-anchor-500 font-mono text-sm hover:underline">
              MetricAnchor
            </Link>
            <span className="text-gray-600">/</span>
            <Link href="/semantic-models" className="text-gray-400 text-sm hover:text-gray-200">
              Semantic Models
            </Link>
            <span className="text-gray-600">/</span>
            <span className="text-gray-300 text-sm font-medium">{model.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                loadYaml();
                setEditing(true);
              }}
              className="rounded-md border border-gray-700 px-4 py-1.5 text-sm text-gray-300 hover:border-anchor-500 hover:text-anchor-300 transition-colors"
            >
              Edit YAML
            </button>
            <button
              onClick={async () => {
                const yaml = await exportSemanticModelYaml(id);
                const blob = new Blob([yaml], { type: "text/yaml" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `${model.name}.yml`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="rounded-md bg-anchor-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-anchor-600 transition-colors"
            >
              Export YAML
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10 space-y-8">
        {/* Identity */}
        <div>
          <div className="flex items-baseline gap-3 flex-wrap">
            <h1 className="text-2xl font-bold text-gray-100">{model.name}</h1>
            <span className="rounded-full bg-anchor-900 px-2.5 py-0.5 text-xs text-anchor-300 font-mono">
              {def.dataset}
            </span>
          </div>
          {def.description && (
            <p className="mt-2 text-sm text-gray-400">{def.description}</p>
          )}
          <div className="mt-3 flex flex-wrap gap-4 text-xs text-gray-500">
            {def.grain && <span>Grain: <span className="text-gray-300">{def.grain}</span></span>}
            {def.time_column && (
              <span>
                Time column:{" "}
                <span className="font-mono text-gray-300">{def.time_column}</span>
              </span>
            )}
            <span>
              Updated: {new Date(model.updated_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        {editing && (
          <div className="rounded-xl border border-anchor-700 bg-gray-900 p-6">
            <YamlEditor
              datasetId={model.dataset_id}
              modelId={model.id}
              initialYaml={exportedYaml ?? undefined}
              onSuccess={handleEditSuccess}
              onCancel={() => setEditing(false)}
            />
          </div>
        )}

        {/* Metrics */}
        <section>
          <h2 className="text-base font-semibold text-gray-300 mb-3">
            Metrics ({def.metrics?.length ?? 0})
          </h2>
          <div className="space-y-3">
            {(def.metrics ?? []).map((m) => (
              <div
                key={m.name}
                className="rounded-lg border border-gray-800 bg-gray-900 p-4"
              >
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-100">{m.name}</span>
                      {m.format && (
                        <span className="rounded bg-gray-800 px-1.5 py-0.5 text-xs text-gray-500">
                          {m.format}
                        </span>
                      )}
                    </div>
                    {m.description && (
                      <p className="text-xs text-gray-400 mt-0.5">{m.description}</p>
                    )}
                    {m.aliases && m.aliases.length > 0 && (
                      <p className="text-xs text-gray-600 mt-1">
                        Also known as: {m.aliases.join(", ")}
                      </p>
                    )}
                  </div>
                  <code className="text-xs font-mono text-anchor-400 bg-anchor-950/30 px-2 py-1 rounded">
                    {m.expression}
                  </code>
                </div>
                {m.filters && m.filters.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {m.filters.map((f, i) => (
                      <span key={i} className="rounded bg-gray-800 px-2 py-0.5 text-xs font-mono text-gray-400">
                        {f.column} {f.operator} {String(f.value)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Dimensions */}
        {(def.dimensions ?? []).length > 0 && (
          <section>
            <h2 className="text-base font-semibold text-gray-300 mb-3">
              Dimensions ({def.dimensions!.length})
            </h2>
            <div className="grid grid-cols-2 gap-3">
              {def.dimensions!.map((d) => (
                <div
                  key={d.name}
                  className="rounded-lg border border-gray-800 bg-gray-900 p-4"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-100 text-sm">{d.name}</span>
                    {d.is_date && (
                      <span className="rounded bg-blue-900/30 px-1.5 py-0.5 text-xs text-blue-400">
                        date
                      </span>
                    )}
                    <span className="font-mono text-xs text-gray-500">{d.column}</span>
                  </div>
                  {d.description && (
                    <p className="text-xs text-gray-400 mt-1">{d.description}</p>
                  )}
                  {d.aliases && d.aliases.length > 0 && (
                    <p className="text-xs text-gray-600 mt-1">
                      Also: {d.aliases.join(", ")}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Synonyms */}
        {(def.synonyms ?? []).length > 0 && (
          <section>
            <h2 className="text-base font-semibold text-gray-300 mb-3">
              Synonyms ({def.synonyms!.length})
            </h2>
            <div className="flex flex-wrap gap-2">
              {def.synonyms!.map((s, i) => (
                <div
                  key={i}
                  className="rounded-full border border-gray-700 bg-gray-900 px-3 py-1 text-xs"
                >
                  <span className="text-gray-300">&quot;{s.phrase}&quot;</span>
                  <span className="text-gray-600 mx-1.5">→</span>
                  <span className="font-mono text-anchor-400">{s.maps_to}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Business rules */}
        {(def.business_rules ?? []).length > 0 && (
          <section>
            <h2 className="text-base font-semibold text-gray-300 mb-3">Business Rules</h2>
            <div className="space-y-2">
              {def.business_rules!.map((r) => (
                <div
                  key={r.name}
                  className="rounded-lg border border-gray-800 bg-gray-900 px-4 py-3"
                >
                  <span className="text-sm font-medium text-gray-200">{r.name}</span>
                  {r.description && (
                    <p className="text-xs text-gray-400 mt-0.5">{r.description}</p>
                  )}
                  <code className="mt-1 block text-xs font-mono text-anchor-400">{r.filter}</code>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Caveats */}
        {(def.caveats ?? []).length > 0 && (
          <section>
            <h2 className="text-base font-semibold text-gray-300 mb-3">Caveats</h2>
            <ul className="space-y-1">
              {def.caveats!.map((c, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-yellow-400">
                  <span className="mt-0.5 text-yellow-600">!</span>
                  {c}
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>
    </div>
  );
}
