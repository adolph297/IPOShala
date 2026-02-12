import React from "react";

const CompanyTable = ({ columns = [], rows = [], emptyText = "No data found." }) => {
  if (!rows || rows.length === 0) {
    return <div className="py-6 text-sm text-gray-500">{emptyText}</div>;
  }

  return (
    <div className="overflow-auto border rounded-lg">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                className="px-4 py-3 text-left font-semibold whitespace-nowrap"
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className="divide-y divide-gray-200 bg-white">
          {rows.map((r, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {columns.map((c) => {
                const value = typeof c.render === "function" ? c.render(r) : r[c.key];

                return (
                  <td key={c.key} className="px-4 py-3 whitespace-nowrap">
                    {value ?? "-"}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CompanyTable;
