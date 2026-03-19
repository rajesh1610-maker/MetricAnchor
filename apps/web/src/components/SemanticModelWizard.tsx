"use client";

import { useState } from "react";
import { createSemanticModel, type Dataset, type SemanticModelDefinition } from "@/lib/api";

// ── Types ──────────────────────────────────────────────────────────────────────

interface WizardProps {
  datasets: Dataset[];
  onSuccess: (modelId: string) => void;
  onCancel: () => void;
}

interface StepProps {
  state: WizardState;
  onChange: (updates: Partial<WizardState>) => void;
  datasets: Dataset[];
}

interface WizardState {
  // Step 1
  datasetId: string;
  modelName: string;
  description: string;
  grain: string;

  // Step 2
  timeColumn: string;
  metrics: MetricRow[];

  // Step 3
  dimensions: DimensionRow[];

  // Step 4
  synonyms: SynonymRow[];
  businessRules: RuleRow[];
  caveats: string;

  // Step 5: review (no extra state)
}

interface MetricRow {
  id: string;
  name: string;
  description: string;
  expression: string;
  format: string;
  aliases: string;
}

interface DimensionRow {
  id: string;
  name: string;
  column: string;
  description: string;
  is_date: boolean;
  aliases: string;
}

interface SynonymRow {
  id: string;
  phrase: string;
  maps_to: string;
}

interface RuleRow {
  id: string;
  name: string;
  description: string;
  filter: string;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

let _id = 0;
const uid = () => String(++_id);

function emptyMetric(): MetricRow {
  return { id: uid(), name: "", description: "", expression: "", format: "number", aliases: "" };
}
function emptyDimension(): DimensionRow {
  return { id: uid(), name: "", column: "", description: "", is_date: false, aliases: "" };
}
function emptySynonym(): SynonymRow {
  return { id: uid(), phrase: "", maps_to: "" };
}
function emptyRule(): RuleRow {
  return { id: uid(), name: "", description: "", filter: "" };
}

const STEPS = ["Dataset", "Metrics", "Dimensions", "Rules & Terms", "Review"] as const;

// ── Main Wizard ────────────────────────────────────────────────────────────────

export default function SemanticModelWizard({ datasets, onSuccess, onCancel }: WizardProps) {
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<WizardState>({
    datasetId: datasets[0]?.id ?? "",
    modelName: "",
    description: "",
    grain: "",
    timeColumn: "",
    metrics: [emptyMetric()],
    dimensions: [emptyDimension()],
    synonyms: [],
    businessRules: [],
    caveats: "",
  });

  function onChange(updates: Partial<WizardState>) {
    setState((prev) => ({ ...prev, ...updates }));
  }

  function canAdvance(): boolean {
    if (step === 0) return !!state.datasetId && !!state.modelName.trim();
    if (step === 1) return state.metrics.some((m) => m.name.trim() && m.expression.trim());
    return true;
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const selectedDataset = datasets.find((d) => d.id === state.datasetId);
      const definition: SemanticModelDefinition = {
        name: state.modelName.trim(),
        dataset: selectedDataset?.name ?? state.datasetId,
        description: state.description.trim() || undefined,
        grain: state.grain.trim() || undefined,
        time_column: state.timeColumn.trim() || undefined,
        metrics: state.metrics
          .filter((m) => m.name.trim() && m.expression.trim())
          .map((m) => ({
            name: m.name.trim(),
            description: m.description.trim() || undefined,
            expression: m.expression.trim(),
            format: m.format || "number",
            aliases: m.aliases ? m.aliases.split(",").map((a) => a.trim()).filter(Boolean) : undefined,
          })),
        dimensions: state.dimensions
          .filter((d) => d.name.trim() && d.column.trim())
          .map((d) => ({
            name: d.name.trim(),
            column: d.column.trim(),
            description: d.description.trim() || undefined,
            is_date: d.is_date || undefined,
            aliases: d.aliases ? d.aliases.split(",").map((a) => a.trim()).filter(Boolean) : undefined,
          })),
        synonyms: state.synonyms
          .filter((s) => s.phrase.trim() && s.maps_to.trim())
          .map((s) => ({ phrase: s.phrase.trim(), maps_to: s.maps_to.trim() })),
        business_rules: state.businessRules
          .filter((r) => r.name.trim() && r.filter.trim())
          .map((r) => ({
            name: r.name.trim(),
            description: r.description.trim() || undefined,
            filter: r.filter.trim(),
          })),
        caveats: state.caveats
          ? state.caveats.split("\n").map((c) => c.trim()).filter(Boolean)
          : undefined,
      };

      const created = await createSemanticModel({
        dataset_id: state.datasetId,
        name: definition.name,
        definition,
      });
      onSuccess(created.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  const stepProps: StepProps = { state, onChange, datasets };

  return (
    <div className="flex flex-col min-h-0">
      {/* Step indicator */}
      <div className="flex items-center gap-0 mb-8">
        {STEPS.map((label, i) => (
          <div key={label} className="flex items-center">
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                i === step
                  ? "bg-anchor-500 text-white"
                  : i < step
                  ? "bg-anchor-900 text-anchor-300"
                  : "text-gray-500"
              }`}
            >
              <span
                className={`flex h-5 w-5 items-center justify-center rounded-full text-xs ${
                  i < step
                    ? "bg-anchor-400 text-white"
                    : i === step
                    ? "bg-white text-anchor-600"
                    : "bg-gray-700 text-gray-400"
                }`}
              >
                {i < step ? "✓" : i + 1}
              </span>
              {label}
            </div>
            {i < STEPS.length - 1 && (
              <div className={`h-px w-6 ${i < step ? "bg-anchor-400" : "bg-gray-700"}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step content */}
      <div className="flex-1">
        {step === 0 && <Step1Dataset {...stepProps} />}
        {step === 1 && <Step2Metrics {...stepProps} />}
        {step === 2 && <Step3Dimensions {...stepProps} />}
        {step === 3 && <Step4Rules {...stepProps} />}
        {step === 4 && <Step5Review {...stepProps} />}
      </div>

      {error && (
        <div className="mt-4 rounded-md border border-red-700 bg-red-900/20 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Navigation */}
      <div className="mt-8 flex items-center justify-between border-t border-gray-800 pt-6">
        <button
          onClick={step === 0 ? onCancel : () => setStep((s) => s - 1)}
          className="rounded-md px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
        >
          {step === 0 ? "Cancel" : "Back"}
        </button>
        {step < STEPS.length - 1 ? (
          <button
            onClick={() => setStep((s) => s + 1)}
            disabled={!canAdvance()}
            className="rounded-md bg-anchor-500 px-5 py-2 text-sm font-medium text-white hover:bg-anchor-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Continue
          </button>
        ) : (
          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded-md bg-anchor-500 px-6 py-2 text-sm font-semibold text-white hover:bg-anchor-600 disabled:opacity-40 transition-colors"
          >
            {saving ? "Saving..." : "Create Model"}
          </button>
        )}
      </div>
    </div>
  );
}

// ── Step 1: Dataset & Identity ─────────────────────────────────────────────────

function Step1Dataset({ state, onChange, datasets }: StepProps) {
  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Dataset & Identity</h2>
        <p className="text-sm text-gray-400 mt-0.5">
          Which dataset does this model describe, and what should it be called?
        </p>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-400 mb-1.5">
          Dataset <span className="text-red-400">*</span>
        </label>
        <select
          value={state.datasetId}
          onChange={(e) => onChange({ datasetId: e.target.value })}
          className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 focus:border-anchor-500 focus:outline-none"
        >
          {datasets.length === 0 && <option value="">No datasets uploaded yet</option>}
          {datasets.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name} ({d.original_filename})
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-400 mb-1.5">
          Model name <span className="text-red-400">*</span>
        </label>
        <input
          type="text"
          placeholder="e.g. retail_sales"
          value={state.modelName}
          onChange={(e) => onChange({ modelName: e.target.value })}
          className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
        />
        <p className="mt-1 text-xs text-gray-600">Lowercase, underscores OK. Used internally.</p>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-400 mb-1.5">
          Description
        </label>
        <textarea
          placeholder="What does this dataset represent? Who uses it?"
          value={state.description}
          onChange={(e) => onChange({ description: e.target.value })}
          rows={2}
          className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none resize-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">
            Grain (what is one row?)
          </label>
          <input
            type="text"
            placeholder="e.g. one row = one order"
            value={state.grain}
            onChange={(e) => onChange({ grain: e.target.value })}
            className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1.5">
            Primary date column
          </label>
          <input
            type="text"
            placeholder="e.g. order_date"
            value={state.timeColumn}
            onChange={(e) => onChange({ timeColumn: e.target.value })}
            className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
          />
        </div>
      </div>
    </div>
  );
}

// ── Step 2: Metrics ────────────────────────────────────────────────────────────

function Step2Metrics({ state, onChange }: StepProps) {
  function addMetric() {
    onChange({ metrics: [...state.metrics, emptyMetric()] });
  }

  function updateMetric(id: string, updates: Partial<MetricRow>) {
    onChange({
      metrics: state.metrics.map((m) => (m.id === id ? { ...m, ...updates } : m)),
    });
  }

  function removeMetric(id: string) {
    onChange({ metrics: state.metrics.filter((m) => m.id !== id) });
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Metrics</h2>
        <p className="text-sm text-gray-400 mt-0.5">
          Define the measures that matter — revenue, tickets, conversions. At least one required.
        </p>
      </div>

      <div className="space-y-4">
        {state.metrics.map((metric, idx) => (
          <div key={metric.id} className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Metric {idx + 1}
              </span>
              {state.metrics.length > 1 && (
                <button
                  onClick={() => removeMetric(metric.id)}
                  className="text-xs text-red-500 hover:text-red-400"
                >
                  Remove
                </button>
              )}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. revenue"
                  value={metric.name}
                  onChange={(e) => updateMetric(metric.id, { name: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Format</label>
                <select
                  value={metric.format}
                  onChange={(e) => updateMetric(metric.id, { format: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 focus:border-anchor-500 focus:outline-none"
                >
                  <option value="number">Number</option>
                  <option value="currency">Currency</option>
                  <option value="percent">Percent</option>
                  <option value="duration">Duration</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-xs text-gray-500 mb-1">
                  SQL expression <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. SUM(order_total)"
                  value={metric.expression}
                  onChange={(e) => updateMetric(metric.id, { expression: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm font-mono text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Description</label>
                <input
                  type="text"
                  placeholder="What does this measure?"
                  value={metric.description}
                  onChange={(e) => updateMetric(metric.id, { description: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  Aliases (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. sales, total revenue"
                  value={metric.aliases}
                  onChange={(e) => updateMetric(metric.id, { aliases: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={addMetric}
        className="rounded-md border border-dashed border-gray-700 px-4 py-2 text-sm text-gray-500 hover:border-anchor-500 hover:text-anchor-400 transition-colors w-full"
      >
        + Add metric
      </button>
    </div>
  );
}

// ── Step 3: Dimensions ─────────────────────────────────────────────────────────

function Step3Dimensions({ state, onChange }: StepProps) {
  function addDimension() {
    onChange({ dimensions: [...state.dimensions, emptyDimension()] });
  }

  function updateDimension(id: string, updates: Partial<DimensionRow>) {
    onChange({
      dimensions: state.dimensions.map((d) => (d.id === id ? { ...d, ...updates } : d)),
    });
  }

  function removeDimension(id: string) {
    onChange({ dimensions: state.dimensions.filter((d) => d.id !== id) });
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Dimensions</h2>
        <p className="text-sm text-gray-400 mt-0.5">
          Define the axes you slice by — region, product, team, plan, date.
        </p>
      </div>

      <div className="space-y-4">
        {state.dimensions.map((dim, idx) => (
          <div key={dim.id} className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Dimension {idx + 1}
              </span>
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-1.5 text-xs text-gray-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={dim.is_date}
                    onChange={(e) => updateDimension(dim.id, { is_date: e.target.checked })}
                    className="rounded border-gray-600"
                  />
                  Date field
                </label>
                {state.dimensions.length > 1 && (
                  <button
                    onClick={() => removeDimension(dim.id)}
                    className="text-xs text-red-500 hover:text-red-400"
                  >
                    Remove
                  </button>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Name</label>
                <input
                  type="text"
                  placeholder="e.g. product_category"
                  value={dim.name}
                  onChange={(e) => updateDimension(dim.id, { name: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Column in table</label>
                <input
                  type="text"
                  placeholder="e.g. product_category"
                  value={dim.column}
                  onChange={(e) => updateDimension(dim.id, { column: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm font-mono text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Description</label>
                <input
                  type="text"
                  placeholder="What does this group by?"
                  value={dim.description}
                  onChange={(e) => updateDimension(dim.id, { description: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  Aliases (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. category, product type"
                  value={dim.aliases}
                  onChange={(e) => updateDimension(dim.id, { aliases: e.target.value })}
                  className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={addDimension}
        className="rounded-md border border-dashed border-gray-700 px-4 py-2 text-sm text-gray-500 hover:border-anchor-500 hover:text-anchor-400 transition-colors w-full"
      >
        + Add dimension
      </button>
    </div>
  );
}

// ── Step 4: Synonyms, Rules, Caveats ──────────────────────────────────────────

function Step4Rules({ state, onChange }: StepProps) {
  function addSynonym() {
    onChange({ synonyms: [...state.synonyms, emptySynonym()] });
  }
  function updateSynonym(id: string, updates: Partial<SynonymRow>) {
    onChange({
      synonyms: state.synonyms.map((s) => (s.id === id ? { ...s, ...updates } : s)),
    });
  }
  function removeSynonym(id: string) {
    onChange({ synonyms: state.synonyms.filter((s) => s.id !== id) });
  }

  function addRule() {
    onChange({ businessRules: [...state.businessRules, emptyRule()] });
  }
  function updateRule(id: string, updates: Partial<RuleRow>) {
    onChange({
      businessRules: state.businessRules.map((r) => (r.id === id ? { ...r, ...updates } : r)),
    });
  }
  function removeRule(id: string) {
    onChange({ businessRules: state.businessRules.filter((r) => r.id !== id) });
  }

  const metricNames = state.metrics
    .filter((m) => m.name.trim())
    .map((m) => `metric:${m.name.trim()}`);
  const dimensionNames = state.dimensions
    .filter((d) => d.name.trim())
    .map((d) => `dimension:${d.name.trim()}`);
  const allTargets = [...metricNames, ...dimensionNames];

  return (
    <div className="space-y-8">
      {/* Synonyms */}
      <div className="space-y-4">
        <div>
          <h2 className="text-base font-semibold text-gray-100">Synonyms</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Map business phrases to metrics or dimensions so users can ask naturally.
            e.g. &quot;sales&quot; → metric:revenue
          </p>
        </div>

        {state.synonyms.map((syn) => (
          <div key={syn.id} className="flex items-center gap-3">
            <input
              type="text"
              placeholder="phrase (e.g. sales)"
              value={syn.phrase}
              onChange={(e) => updateSynonym(syn.id, { phrase: e.target.value })}
              className="flex-1 rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
            />
            <span className="text-gray-600 text-sm">→</span>
            <select
              value={syn.maps_to}
              onChange={(e) => updateSynonym(syn.id, { maps_to: e.target.value })}
              className="flex-1 rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 focus:border-anchor-500 focus:outline-none"
            >
              <option value="">Select target...</option>
              {allTargets.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <button
              onClick={() => removeSynonym(syn.id)}
              className="text-xs text-red-500 hover:text-red-400 px-1"
            >
              ×
            </button>
          </div>
        ))}

        <button
          onClick={addSynonym}
          className="rounded border border-dashed border-gray-700 px-3 py-1.5 text-xs text-gray-500 hover:border-anchor-500 hover:text-anchor-400 transition-colors"
        >
          + Add synonym
        </button>
      </div>

      {/* Business Rules */}
      <div className="space-y-4">
        <div>
          <h2 className="text-base font-semibold text-gray-100">Business Rules</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Common filters the AI should always apply. e.g. &quot;active users only&quot;.
          </p>
        </div>

        {state.businessRules.map((rule) => (
          <div key={rule.id} className="rounded-lg border border-gray-700 bg-gray-800/50 p-3 space-y-2">
            <div className="flex items-center justify-between">
              <input
                type="text"
                placeholder="Rule name (e.g. active_only)"
                value={rule.name}
                onChange={(e) => updateRule(rule.id, { name: e.target.value })}
                className="flex-1 rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
              />
              <button
                onClick={() => removeRule(rule.id)}
                className="ml-2 text-xs text-red-500 hover:text-red-400"
              >
                Remove
              </button>
            </div>
            <input
              type="text"
              placeholder="SQL filter (e.g. status = 'active')"
              value={rule.filter}
              onChange={(e) => updateRule(rule.id, { filter: e.target.value })}
              className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm font-mono text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={rule.description}
              onChange={(e) => updateRule(rule.id, { description: e.target.value })}
              className="w-full rounded border border-gray-600 bg-gray-800 px-2.5 py-1.5 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none"
            />
          </div>
        ))}

        <button
          onClick={addRule}
          className="rounded border border-dashed border-gray-700 px-3 py-1.5 text-xs text-gray-500 hover:border-anchor-500 hover:text-anchor-400 transition-colors"
        >
          + Add business rule
        </button>
      </div>

      {/* Caveats */}
      <div>
        <label className="block text-base font-semibold text-gray-100 mb-1">
          Caveats & Warnings
        </label>
        <p className="text-xs text-gray-400 mb-2">
          Anything the AI should surface when using this model. One per line.
        </p>
        <textarea
          placeholder={"e.g. Refunds are not deducted from revenue\nData is refreshed daily at 6am UTC"}
          value={state.caveats}
          onChange={(e) => onChange({ caveats: e.target.value })}
          rows={3}
          className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:border-anchor-500 focus:outline-none resize-none"
        />
      </div>
    </div>
  );
}

// ── Step 5: Review ─────────────────────────────────────────────────────────────

function Step5Review({ state, datasets }: StepProps) {
  const dataset = datasets.find((d) => d.id === state.datasetId);
  const validMetrics = state.metrics.filter((m) => m.name.trim() && m.expression.trim());
  const validDimensions = state.dimensions.filter((d) => d.name.trim() && d.column.trim());
  const validSynonyms = state.synonyms.filter((s) => s.phrase.trim() && s.maps_to.trim());

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Review & Create</h2>
        <p className="text-sm text-gray-400 mt-0.5">
          Check everything looks right before saving.
        </p>
      </div>

      <Section label="Dataset">
        <p className="text-sm text-gray-200">{dataset?.name ?? state.datasetId}</p>
      </Section>

      <Section label="Identity">
        <p className="text-sm text-gray-200 font-medium">{state.modelName}</p>
        {state.description && <p className="text-sm text-gray-400 mt-0.5">{state.description}</p>}
        {state.grain && <p className="text-xs text-gray-500 mt-1">{state.grain}</p>}
        {state.timeColumn && (
          <p className="text-xs text-gray-500">Primary date: <span className="font-mono">{state.timeColumn}</span></p>
        )}
      </Section>

      <Section label={`Metrics (${validMetrics.length})`}>
        {validMetrics.map((m) => (
          <div key={m.id} className="flex items-baseline gap-2 text-sm">
            <span className="font-medium text-gray-200">{m.name}</span>
            <span className="font-mono text-xs text-anchor-400">{m.expression}</span>
            <span className="text-xs text-gray-600">{m.format}</span>
          </div>
        ))}
      </Section>

      <Section label={`Dimensions (${validDimensions.length})`}>
        {validDimensions.map((d) => (
          <div key={d.id} className="flex items-baseline gap-2 text-sm">
            <span className="font-medium text-gray-200">{d.name}</span>
            <span className="font-mono text-xs text-gray-500">{d.column}</span>
            {d.is_date && <span className="text-xs text-blue-400">date</span>}
          </div>
        ))}
        {validDimensions.length === 0 && <p className="text-xs text-gray-600">None defined</p>}
      </Section>

      {validSynonyms.length > 0 && (
        <Section label={`Synonyms (${validSynonyms.length})`}>
          {validSynonyms.map((s) => (
            <p key={s.id} className="text-sm text-gray-300">
              &quot;{s.phrase}&quot; → <span className="font-mono text-xs text-anchor-400">{s.maps_to}</span>
            </p>
          ))}
        </Section>
      )}
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">{label}</p>
      <div className="space-y-1">{children}</div>
    </div>
  );
}
