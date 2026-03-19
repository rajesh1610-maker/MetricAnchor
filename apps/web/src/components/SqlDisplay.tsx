"use client";

import { useState } from "react";

interface SqlDisplayProps {
  sql: string;
  executionMs?: number | null;
}

export default function SqlDisplay({ sql, executionMs }: SqlDisplayProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  // Basic keyword highlighting
  const highlighted = sql
    .replace(
      /\b(SELECT|FROM|WHERE|GROUP BY|ORDER BY|HAVING|LIMIT|AND|OR|AS|FILTER|DISTINCT|COUNT|SUM|AVG|MIN|MAX|CASE|WHEN|THEN|ELSE|END|NULLIF|NULL|NOT|IN|IS)\b/g,
      '<span class="text-blue-400 font-semibold">$1</span>'
    )
    .replace(
      /'([^']*)'/g,
      '<span class="text-green-400">\'$1\'</span>'
    )
    .replace(
      /("([^"]+)")/g,
      '<span class="text-yellow-300">$1</span>'
    );

  return (
    <div className="rounded-lg border border-gray-700 bg-gray-900 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800/60 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-gray-400">Generated SQL</span>
          {executionMs != null && (
            <span className="rounded-full bg-gray-700 px-2 py-0.5 text-xs text-gray-400">
              {executionMs}ms
            </span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="text-xs text-gray-500 hover:text-gray-200 transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <pre
        className="px-4 py-3 text-sm font-mono text-gray-200 overflow-x-auto leading-relaxed"
        dangerouslySetInnerHTML={{ __html: highlighted }}
      />
    </div>
  );
}
