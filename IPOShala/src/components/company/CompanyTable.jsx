import React from "react";

const CompanyTable = ({ title, columns = [], rows = [], emptyText = "No data found." }) => {
  if (!rows || rows.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        {title && (
          <div className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6">
            {title}
          </div>
        )}
        <div className="text-sm text-gray-500">{emptyText}</div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
      {title && (
        <div className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6">
          {title}
        </div>
      )}
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
    </div>
  );
};

export default CompanyTable;
