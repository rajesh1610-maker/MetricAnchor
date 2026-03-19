"use client";

import { useState } from "react";
import * as jsYaml from "js-yaml";
import {
  createSemanticModel,
  updateSemanticModel,
  validateSemanticModel,
  type SemanticModelDefinition,
} from "@/lib/api";

interface YamlEditorProps {
  datasetId: string;
  modelId?: string;
  initialYaml?: string;
  onSuccess: (modelId: string) => void;
  onCancel: () => void;
}

const PLACEHOLDER = `name: my_model
dataset: my_dataset
description: "What this data represents"
grain: "one row = one event"
time_column: event_date

metrics:
  - name: revenue
    description: "Total completed order value"
    expression: "SUM(order_total)"
    format: currency
    aliases: [sales, "total revenue"]
    filters:
      - column: status
        operator: "="
        value: completed

dimensions:
  - name: product_category
    column: product_category
    description: "Product category"
    aliases: [category]

synonyms:
  - phrase: "sales"
    maps_to: "metric:revenue"

caveats:
  - "Refunds are not deducted from revenue"
`;

export default function YamlEditor({
  datasetId,
  modelId,
  initialYaml = PLACEHOLDER,
  onSuccess,
  onCancel,
}: YamlEditorProps) {
  const [yaml, setYaml] = useState(initialYaml);
  const [validating, setValidating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [validation, setValidation] = useState<{
    valid: boolean;
    errors: string[];
    warnings: string[];
  } | null>(null);

  async function handleValidate() {
    setValidating(true);
    setValidation(null);
    try {
      // Parse YAML client-side via a simple fetch to the validate endpoint
      // We pass the raw text; the server will parse it via JSON if we use dict,
      // so we convert here using a basic approach: send to a /validate helper
      // that accepts the dict form.
      // Since we don't have a YAML-to-dict in JS, send to a temporary approach:
      // POST the yaml text as a JSON string field is not how the API works.
      // Instead we'll use the validate endpoint with the raw dict by calling
      // the server-side parse. For now, do a basic client-side check.
      const result = await validateDefinitionFromYaml(yaml);
      setValidation(result);
    } catch (e) {
      setValidation({
        valid: false,
        errors: [e instanceof Error ? e.message : "Validation failed"],
        warnings: [],
      });
    } finally {
      setValidating(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    try {
      const definition = parseYamlToDefinition(yaml);
      let result;
      if (modelId) {
        result = await updateSemanticModel(modelId, definition);
      } else {
        result = await createSemanticModel({
          dataset_id: datasetId,
          name: definition.name,
          definition,
        });
      }
      onSuccess(result.id);
    } catch (e) {
      setValidation({
        valid: false,
        errors: [e instanceof Error ? e.message : "Save failed"],
        warnings: [],
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-gray-100">YAML Editor</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Edit the semantic model definition directly. Use Validate before saving.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onCancel}
            className="rounded px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleValidate}
            disabled={validating}
            className="rounded border border-gray-600 px-3 py-1.5 text-sm text-gray-200 hover:border-anchor-500 hover:text-anchor-300 disabled:opacity-40 transition-colors"
          >
            {validating ? "Checking..." : "Validate"}
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded bg-anchor-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-anchor-600 disabled:opacity-40 transition-colors"
          >
            {saving ? "Saving..." : modelId ? "Update" : "Create"}
          </button>
        </div>
      </div>

      <div className="relative rounded-lg border border-gray-700 bg-gray-900 overflow-hidden">
        <div className="flex items-center gap-2 border-b border-gray-800 px-4 py-2 bg-gray-900/80">
          <span className="text-xs font-mono text-gray-500">semantic_model.yml</span>
        </div>
        <textarea
          value={yaml}
          onChange={(e) => {
            setYaml(e.target.value);
            setValidation(null);
          }}
          rows={28}
          spellCheck={false}
          className="w-full bg-gray-900 px-4 py-3 font-mono text-sm text-gray-200 focus:outline-none resize-none leading-relaxed"
        />
      </div>

      {validation && (
        <div
          className={`rounded-lg border p-4 space-y-2 ${
            validation.valid
              ? "border-green-700 bg-green-900/20"
              : "border-red-700 bg-red-900/20"
          }`}
        >
          <p
            className={`text-sm font-semibold ${
              validation.valid ? "text-green-400" : "text-red-400"
            }`}
          >
            {validation.valid ? "Valid" : "Invalid"}
          </p>
          {validation.errors.map((e, i) => (
            <p key={i} className="text-sm text-red-300">
              {e}
            </p>
          ))}
          {validation.warnings.map((w, i) => (
            <p key={i} className="text-sm text-yellow-400">
              Warning: {w}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Minimal YAML parser for the subset we need ────────────────────────────────
// Rather than shipping a full YAML library, we send the text through the
// backend validate endpoint by first encoding it as a JSON-compatible object.
// This is a best-effort client-side parse to give inline feedback.

async function validateDefinitionFromYaml(
  yamlText: string
): Promise<{ valid: boolean; errors: string[]; warnings: string[] }> {
  try {
    const def = parseYamlToDefinition(yamlText);
    return await validateSemanticModel(def as unknown as object);
  } catch (e) {
    return {
      valid: false,
      errors: [e instanceof Error ? e.message : "Could not parse YAML"],
      warnings: [],
    };
  }
}

function parseYamlToDefinition(yamlText: string): SemanticModelDefinition {
  const parsed = jsYaml.load(yamlText);
  if (!parsed || typeof parsed !== "object") {
    throw new Error("YAML did not parse to an object.");
  }
  return parsed as SemanticModelDefinition;
}
