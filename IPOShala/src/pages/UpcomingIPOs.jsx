import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import UpcomingIPOsTable from '@/components/UpcomingIPOsTable';

const UpcomingIPOs = () => {
  return (
    <>
      <Helmet>
        <title>Upcoming IPOs - IPOshala</title>
      </Helmet>
      <PageHeader title="Upcoming IPOs" subtitle="Calendar of upcoming public issues in Indian markets" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <UpcomingIPOsTable />
      </div>
    </>
  );
};

export default UpcomingIPOs;