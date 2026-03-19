interface Props {
  columns: string[];
  rows: (string | number | null)[][];
}

export default function DataTable({ columns, rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-gray-800 px-6 py-12 text-center text-sm text-gray-600">
        No rows to display.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-gray-800">
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr className="bg-gray-900/60">
              {columns.map((col) => (
                <th
                  key={col}
                  className="whitespace-nowrap border-b border-gray-800 px-4 py-2.5 text-left font-medium text-gray-400 uppercase tracking-wide"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {rows.map((row, ri) => (
              <tr key={ri} className="hover:bg-gray-800/30 transition-colors">
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    className="max-w-xs truncate whitespace-nowrap px-4 py-2 font-mono text-gray-300"
                    title={cell === null ? "NULL" : String(cell)}
                  >
                    {cell === null ? (
                      <span className="text-gray-600 italic">null</span>
                    ) : (
                      String(cell)
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="border-t border-gray-800 bg-gray-900/40 px-4 py-2 text-xs text-gray-600">
        Showing {rows.length} row{rows.length !== 1 ? "s" : ""}
      </div>
    </div>
  );
}
