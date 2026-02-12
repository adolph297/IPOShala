import React from "react";

const TableContainer = ({ title, children, lastUpdated }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-8">
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center flex-wrap gap-2">
        <h3 className="text-lg font-semibold text-[#1a2332]">{title}</h3>
        {lastUpdated && (
          <span className="text-xs text-gray-500">
            Last Updated: {lastUpdated}
          </span>
        )}
      </div>

      {/* ✅ Supports both horizontal + vertical scrolling */}
      <div className="w-full overflow-x-auto">
        {children}
      </div>
    </div>
  );
};

export default TableContainer;
