interface KpiCardProps {
  value: string | number | null;
  label: string;
  format?: string;
}

export default function KpiCard({ value, label, format }: KpiCardProps) {
  const formatted = _fmt(value, format);

  return (
    <div className="flex flex-col items-start gap-1 py-6">
      <p
        className="text-5xl font-bold tracking-tight text-anchor-400 font-mono tabular-nums"
        aria-label={`${label}: ${formatted}`}
      >
        {formatted}
      </p>
      <p className="text-sm text-gray-400 font-medium">{label}</p>
    </div>
  );
}

function _fmt(v: string | number | null | undefined, format?: string): string {
  if (v == null) return "—";
  const n = typeof v === "number" ? v : parseFloat(String(v));
  if (isNaN(n)) return String(v);

  if (format === "currency") {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(n);
  }
  if (format === "percent") {
    return `${n.toFixed(1)}%`;
  }
  if (Number.isInteger(n)) {
    return new Intl.NumberFormat("en-US").format(n);
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(n);
}
