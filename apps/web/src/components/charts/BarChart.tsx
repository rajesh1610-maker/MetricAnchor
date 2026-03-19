"use client";

import { useState } from "react";

interface BarChartProps {
  data: { label: string; value: number }[];
  valueLabel?: string;
  maxBars?: number;
}

export default function BarChart({ data, valueLabel, maxBars = 15 }: BarChartProps) {
  const [hovered, setHovered] = useState<number | null>(null);
  const visible = data.slice(0, maxBars);
  const maxVal = Math.max(...visible.map((d) => d.value), 1);

  function fmt(v: number): string {
    if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
    if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
    if (Number.isInteger(v)) return v.toLocaleString();
    return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  return (
    <div className="w-full space-y-1.5" role="list" aria-label={valueLabel ?? "bar chart"}>
      {visible.map((d, i) => {
        const pct = (d.value / maxVal) * 100;
        const isHovered = hovered === i;

        return (
          <div
            key={i}
            role="listitem"
            aria-label={`${d.label}: ${fmt(d.value)}`}
            className="group flex items-center gap-3"
            onMouseEnter={() => setHovered(i)}
            onMouseLeave={() => setHovered(null)}
          >
            {/* Label */}
            <div
              className="w-36 shrink-0 text-right text-xs text-gray-400 truncate group-hover:text-gray-200 transition-colors"
              title={d.label}
            >
              {d.label}
            </div>

            {/* Bar track */}
            <div className="flex-1 h-6 rounded bg-gray-800 relative overflow-hidden">
              <div
                className={`h-full rounded transition-all duration-300 ${
                  isHovered ? "bg-anchor-400" : "bg-anchor-600"
                }`}
                style={{ width: `${pct}%` }}
              />
            </div>

            {/* Value */}
            <div
              className={`w-20 shrink-0 text-xs font-mono tabular-nums transition-colors ${
                isHovered ? "text-anchor-300" : "text-gray-400"
              }`}
            >
              {fmt(d.value)}
            </div>
          </div>
        );
      })}

      {data.length > maxBars && (
        <p className="text-xs text-gray-600 pt-1">
          Showing top {maxBars} of {data.length} rows
        </p>
      )}
    </div>
  );
}
