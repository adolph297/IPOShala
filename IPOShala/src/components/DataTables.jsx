import React from 'react';
import CurrentIPOsTable from '@/components/CurrentIPOsTable';
import UpcomingIPOsTable from '@/components/UpcomingIPOsTable';

const DataTables = () => {
  return (
    <section className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <CurrentIPOsTable />
        <UpcomingIPOsTable />
      </div>
    </section>
  );
};

export default DataTables;