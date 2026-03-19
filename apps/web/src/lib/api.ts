const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ColumnProfile {
  name: string;
  data_type: string;
  null_count: number;
  null_pct: number;
  distinct_count: number;
  is_numeric: boolean;
  is_date: boolean;
  is_bool: boolean;
  min_value: string | null;
  max_value: string | null;
  sample_values: string[];
}

export interface DatasetProfile {
  row_count: number;
  column_count: number;
  columns: ColumnProfile[];
}

export interface Dataset {
  id: string;
  name: string;
  original_filename: string;
  file_format: string;
  row_count: number | null;
  column_count: number | null;
  profile: DatasetProfile | null;
  created_at: string;
}

export interface DatasetListResponse {
  datasets: Dataset[];
  total: number;
}

export interface RowsResponse {
  columns: string[];
  rows: (string | number | null)[][];
  total_returned: number;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail?.detail ?? `API error ${res.status}`);
  }
  return res.json();
}

// ── Dataset API ───────────────────────────────────────────────────────────────

export async function listDatasets(): Promise<DatasetListResponse> {
  return apiFetch("/api/datasets");
}

export async function getDataset(id: string): Promise<Dataset> {
  return apiFetch(`/api/datasets/${id}`);
}

export async function getDatasetRows(
  id: string,
  limit = 100,
  offset = 0
): Promise<RowsResponse> {
  return apiFetch(`/api/datasets/${id}/rows?limit=${limit}&offset=${offset}`);
}

export async function uploadDataset(file: File): Promise<Dataset> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/datasets`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail?.detail ?? `Upload failed (${res.status})`);
  }
  return res.json();
}

// ── Question / Q&A types ──────────────────────────────────────────────────────

export interface SemanticMappingItem {
  phrase: string;
  resolved_to: string;
  resolved_name: string;
  type: string;
  via: string;
}

export interface QuestionResponse {
  id: string;
  dataset_id: string;
  question: string;
  answer: string | null;
  sql: string | null;
  columns: string[];
  rows: (string | number | null)[][];
  row_count: number;
  chart_type: string | null;
  semantic_mappings: SemanticMappingItem[];
  assumptions: string[];
  caveats: string[];
  confidence: string | null;
  confidence_note: string | null;
  clarifying_question: string | null;
  provenance: Record<string, unknown> | null;
  execution_ms: number | null;
  error: string | null;
  created_at: string;
}

export interface QuestionListResponse {
  questions: QuestionResponse[];
  total: number;
}

export interface FeedbackResponse {
  id: string;
  question_id: string;
  feedback_type: string;
  note: string | null;
  created_at: string;
}

// ── Question API ──────────────────────────────────────────────────────────────

export async function askQuestion(payload: {
  question: string;
  dataset_id: string;
  model_id?: string;
}): Promise<QuestionResponse> {
  return apiFetch("/api/questions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listQuestions(
  datasetId?: string,
  limit = 50
): Promise<QuestionListResponse> {
  const params = new URLSearchParams();
  if (datasetId) params.set("dataset_id", datasetId);
  params.set("limit", String(limit));
  return apiFetch(`/api/questions?${params}`);
}

export async function getQuestion(id: string): Promise<QuestionResponse> {
  return apiFetch(`/api/questions/${id}`);
}

export async function submitFeedback(
  questionId: string,
  feedbackType: "correct" | "partial" | "wrong",
  note?: string
): Promise<FeedbackResponse> {
  return apiFetch(`/api/questions/${questionId}/feedback`, {
    method: "POST",
    body: JSON.stringify({ feedback_type: feedbackType, note }),
  });
}

// ── Semantic Model types ───────────────────────────────────────────────────────

export interface MetricDef {
  name: string;
  description?: string;
  expression: string;
  filters?: { column: string; operator: string; value: string }[];
  aliases?: string[];
  format?: string;
  unit?: string;
  default_aggregation?: string;
}

export interface DimensionDef {
  name: string;
  column: string;
  description?: string;
  aliases?: string[];
  values?: string[];
  is_date?: boolean;
}

export interface EntityDef {
  name: string;
  column: string;
  description?: string;
  aliases?: string[];
}

export interface SynonymDef {
  phrase: string;
  maps_to: string;
}

export interface BusinessRuleDef {
  name: string;
  description?: string;
  filter: string;
  applies_to?: string[];
}

export interface SemanticModelDefinition {
  name: string;
  dataset: string;
  description?: string;
  grain?: string;
  time_column?: string;
  metrics: MetricDef[];
  dimensions?: DimensionDef[];
  entities?: EntityDef[];
  synonyms?: SynonymDef[];
  business_rules?: BusinessRuleDef[];
  caveats?: string[];
  exclusions?: { description: string; filter?: string }[];
}

export interface SemanticModel {
  id: string;
  dataset_id: string;
  name: string;
  definition: SemanticModelDefinition;
  created_at: string;
  updated_at: string;
}

export interface SemanticModelListResponse {
  semantic_models: SemanticModel[];
  total: number;
}

export interface ValidationResponse {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

// ── Semantic Model API ─────────────────────────────────────────────────────────

export async function listSemanticModels(
  datasetId?: string
): Promise<SemanticModelListResponse> {
  const qs = datasetId ? `?dataset_id=${datasetId}` : "";
  return apiFetch(`/api/semantic_models${qs}`);
}

export async function getSemanticModel(id: string): Promise<SemanticModel> {
  return apiFetch(`/api/semantic_models/${id}`);
}

export async function createSemanticModel(payload: {
  dataset_id: string;
  name: string;
  definition: SemanticModelDefinition;
}): Promise<SemanticModel> {
  return apiFetch("/api/semantic_models", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateSemanticModel(
  id: string,
  definition: SemanticModelDefinition
): Promise<SemanticModel> {
  return apiFetch(`/api/semantic_models/${id}`, {
    method: "PUT",
    body: JSON.stringify({ definition }),
  });
}

export async function deleteSemanticModel(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/semantic_models/${id}`, {
    method: "DELETE",
  });
  if (!res.ok && res.status !== 204) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail?.detail ?? `Delete failed (${res.status})`);
  }
}

export async function validateSemanticModel(
  definition: object
): Promise<ValidationResponse> {
  return apiFetch("/api/semantic_models/validate", {
    method: "POST",
    body: JSON.stringify(definition),
  });
}

export async function exportSemanticModelYaml(id: string): Promise<string> {
  const res = await fetch(`${API_BASE}/api/semantic_models/${id}/export`);
  if (!res.ok) throw new Error(`Export failed (${res.status})`);
  return res.text();
}
