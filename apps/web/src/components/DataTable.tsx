interface Props {
  columns: string[];
  rows: (string | number | null)[][];
}

export default function DataTable({ columns, rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className="rounded-xl border border-gray-100 bg-gray-50 px-6 py-12 text-center text-sm text-gray-400">
        No rows to display.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-gray-100 shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-50">
              {columns.map((col) => (
                <th
                  key={col}
                  className="whitespace-nowrap border-b border-gray-100 px-4 py-3 text-left font-medium text-gray-600"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50 bg-white">
            {rows.map((row, ri) => (
              <tr key={ri} className="hover:bg-gray-50/50">
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    className="max-w-xs truncate whitespace-nowrap px-4 py-2.5 font-mono text-xs text-gray-700"
                    title={cell === null ? "NULL" : String(cell)}
                  >
                    {cell === null ? (
                      <span className="italic text-gray-300">null</span>
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
      <div className="border-t border-gray-100 bg-gray-50 px-4 py-2 text-xs text-gray-400">
        Showing {rows.length} row{rows.length !== 1 ? "s" : ""}
      </div>
    </div>
  );
}
