"use client";

import { useId, useState } from "react";

interface LineChartProps {
  data: { x: string; y: number }[];
  xLabel?: string;
  yLabel?: string;
}

const PAD = { top: 20, right: 20, bottom: 40, left: 56 };
const VIEW_W = 700;
const VIEW_H = 240;
const CHART_W = VIEW_W - PAD.left - PAD.right;
const CHART_H = VIEW_H - PAD.top - PAD.bottom;

export default function LineChart({ data, xLabel, yLabel }: LineChartProps) {
  const gradientId = useId();
  const [tooltip, setTooltip] = useState<{ i: number; x: number; y: number } | null>(null);

  if (data.length < 2) {
    return (
      <div className="flex items-center justify-center h-40 text-xs text-gray-600">
        Not enough data points for a line chart.
      </div>
    );
  }

  const ys = data.map((d) => d.y);
  const yMin = Math.min(...ys);
  const yMax = Math.max(...ys);
  const yRange = yMax - yMin || 1;

  function xPos(i: number) {
    return PAD.left + (i / (data.length - 1)) * CHART_W;
  }
  function yPos(v: number) {
    return PAD.top + CHART_H - ((v - yMin) / yRange) * CHART_H;
  }

  const points = data.map((d, i) => `${xPos(i)},${yPos(d.y)}`).join(" ");
  const areaPath = [
    `M ${xPos(0)} ${PAD.top + CHART_H}`,
    ...data.map((d, i) => `L ${xPos(i)} ${yPos(d.y)}`),
    `L ${xPos(data.length - 1)} ${PAD.top + CHART_H}`,
    "Z",
  ].join(" ");

  // Y axis ticks (4 ticks)
  const yTicks = Array.from({ length: 5 }, (_, i) => yMin + (yRange * i) / 4);

  // X axis labels (max 6)
  const xStep = Math.ceil(data.length / 6);
  const xTickIndices = data
    .map((_, i) => i)
    .filter((i) => i % xStep === 0 || i === data.length - 1);

  function fmtY(v: number) {
    if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
    if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
    return v.toFixed(0);
  }

  function fmtX(s: string) {
    // Try date formatting
    const d = new Date(s);
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    }
    return s.length > 8 ? s.slice(0, 7) + "…" : s;
  }

  return (
    <div className="w-full" aria-label={`Line chart${yLabel ? `: ${yLabel}` : ""}`}>
      <svg
        viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
        className="w-full"
        style={{ height: "240px" }}
        role="img"
      >
        <defs>
          <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {yTicks.map((tick, i) => (
          <line
            key={i}
            x1={PAD.left}
            x2={PAD.left + CHART_W}
            y1={yPos(tick)}
            y2={yPos(tick)}
            stroke="#1f2937"
            strokeWidth="1"
          />
        ))}

        {/* Y axis labels */}
        {yTicks.map((tick, i) => (
          <text
            key={i}
            x={PAD.left - 8}
            y={yPos(tick)}
            textAnchor="end"
            dominantBaseline="middle"
            fontSize="10"
            fill="#6b7280"
          >
            {fmtY(tick)}
          </text>
        ))}

        {/* X axis labels */}
        {xTickIndices.map((i) => (
          <text
            key={i}
            x={xPos(i)}
            y={PAD.top + CHART_H + 16}
            textAnchor="middle"
            fontSize="10"
            fill="#6b7280"
          >
            {fmtX(data[i].x)}
          </text>
        ))}

        {/* Area fill */}
        <path d={areaPath} fill={`url(#${gradientId})`} />

        {/* Line */}
        <polyline
          points={points}
          fill="none"
          stroke="#818cf8"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Hover dots */}
        {data.map((d, i) => (
          <circle
            key={i}
            cx={xPos(i)}
            cy={yPos(d.y)}
            r={tooltip?.i === i ? 5 : 3}
            fill={tooltip?.i === i ? "#818cf8" : "#1e1b4b"}
            stroke="#818cf8"
            strokeWidth="1.5"
            className="cursor-pointer"
            onMouseEnter={(e) =>
              setTooltip({ i, x: xPos(i), y: yPos(d.y) })
            }
            onMouseLeave={() => setTooltip(null)}
            aria-label={`${d.x}: ${fmtY(d.y)}`}
          />
        ))}

        {/* Tooltip */}
        {tooltip !== null && (() => {
          const d = data[tooltip.i];
          const tooltipX = tooltip.x > VIEW_W / 2 ? tooltip.x - 8 : tooltip.x + 8;
          const anchor = tooltip.x > VIEW_W / 2 ? "end" : "start";
          return (
            <g>
              <line
                x1={tooltip.x}
                x2={tooltip.x}
                y1={PAD.top}
                y2={PAD.top + CHART_H}
                stroke="#374151"
                strokeWidth="1"
                strokeDasharray="3,3"
              />
              <rect
                x={anchor === "end" ? tooltipX - 80 : tooltipX}
                y={tooltip.y - 28}
                width="80"
                height="24"
                rx="4"
                fill="#111827"
                stroke="#374151"
              />
              <text
                x={anchor === "end" ? tooltipX - 40 : tooltipX + 40}
                y={tooltip.y - 12}
                textAnchor="middle"
                fontSize="10"
                fill="#e5e7eb"
              >
                {fmtX(d.x)}: {fmtY(d.y)}
              </text>
            </g>
          );
        })()}

        {/* Axis lines */}
        <line
          x1={PAD.left}
          x2={PAD.left}
          y1={PAD.top}
          y2={PAD.top + CHART_H}
          stroke="#374151"
          strokeWidth="1"
        />
        <line
          x1={PAD.left}
          x2={PAD.left + CHART_W}
          y1={PAD.top + CHART_H}
          y2={PAD.top + CHART_H}
          stroke="#374151"
          strokeWidth="1"
        />
      </svg>

      {(xLabel || yLabel) && (
        <div className="flex items-center justify-between px-14 text-xs text-gray-600">
          {yLabel && <span className="rotate-0">{yLabel}</span>}
          {xLabel && <span>{xLabel}</span>}
        </div>
      )}
    </div>
  );
}
