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
