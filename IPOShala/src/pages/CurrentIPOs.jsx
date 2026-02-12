import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import CurrentIPOsTable from '@/components/CurrentIPOsTable';

const CurrentIPOs = () => {
  return (
    <>
      <Helmet>
        <title>Current IPOs - IPOshala</title>
      </Helmet>
      <PageHeader title="Current IPOs" subtitle="Open for subscription right now" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <CurrentIPOsTable />
      </div>
    </>
  );
};

export default CurrentIPOs;