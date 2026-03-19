import type { ColumnProfile } from "@/lib/api";

const TYPE_LABELS: Record<string, { label: string; color: string }> = {
  numeric: { label: "Numeric", color: "bg-blue-100 text-blue-700" },
  date: { label: "Date / Time", color: "bg-purple-100 text-purple-700" },
  bool: { label: "Boolean", color: "bg-yellow-100 text-yellow-700" },
  text: { label: "Text", color: "bg-gray-100 text-gray-600" },
};

function typeLabel(col: ColumnProfile) {
  if (col.is_numeric) return TYPE_LABELS.numeric;
  if (col.is_date) return TYPE_LABELS.date;
  if (col.is_bool) return TYPE_LABELS.bool;
  return TYPE_LABELS.text;
}

interface Props {
  column: ColumnProfile;
}

export default function ColumnProfileCard({ column }: Props) {
  const { label, color } = typeLabel(column);
  const nullBarWidth = Math.min(column.null_pct, 100);

  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
      {/* Header */}
      <div className="mb-3 flex items-start justify-between gap-2">
        <code className="text-sm font-semibold text-gray-900">{column.name}</code>
        <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
          {label}
        </span>
      </div>

      <p className="mb-3 truncate text-xs text-gray-400">{column.data_type}</p>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <Stat label="Distinct" value={column.distinct_count.toLocaleString()} />
        <Stat label="Nulls" value={`${column.null_count.toLocaleString()} (${column.null_pct}%)`} />
        {column.min_value !== null && (
          <Stat label="Min" value={column.min_value} />
        )}
        {column.max_value !== null && (
          <Stat label="Max" value={column.max_value} />
        )}
      </div>

      {/* Null % bar */}
      {column.null_pct > 0 && (
        <div className="mt-3">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-amber-400"
              style={{ width: `${nullBarWidth}%` }}
            />
          </div>
          <p className="mt-1 text-xs text-gray-400">{column.null_pct}% null</p>
        </div>
      )}

      {/* Sample values */}
      {column.sample_values.length > 0 && !column.is_numeric && !column.is_date && (
        <div className="mt-3 flex flex-wrap gap-1">
          {column.sample_values.map((v) => (
            <span
              key={v}
              className="max-w-[120px] truncate rounded bg-gray-50 px-2 py-0.5 text-xs text-gray-500"
              title={v}
            >
              {v}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-gray-400">{label}</p>
      <p className="font-medium text-gray-700 truncate">{value}</p>
    </div>
  );
}
