import React from 'react';

const PageHeader = ({ title, subtitle }) => {
  return (
    <div className="bg-gray-100 border-b border-gray-200 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-[#1a2332]">{title}</h1>
        {subtitle && <p className="mt-2 text-lg text-gray-600">{subtitle}</p>}
      </div>
    </div>
  );
};

export default PageHeader;