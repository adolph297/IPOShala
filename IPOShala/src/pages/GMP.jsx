import React, { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import TableContainer from '@/components/common/TableContainer';
import { getGMPData } from '../services/ipos';
import { Link } from 'react-router-dom';
import AdvancedTable from '@/components/common/AdvancedTable';

const GMP = () => {
  const [gmpData, setGmpData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGMPData()
      .then(data => {
        setGmpData(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load GMP data", err);
        setLoading(false);
      });
  }, []);

  const columns = [
    {
      header: 'Company',
      accessor: 'companyName',
      render: (row) => (
        <Link to={`/ipo/${row.ipo_id}`} className="text-blue-600 hover:underline">
          {row.companyName}
        </Link>
      )
    },
    {
      header: 'Type',
      accessor: 'type',
      render: () => <span className="text-gray-500">Mainboard/SME</span>
    },
    {
      header: 'Issue Price',
      accessor: 'issuePrice',
      render: (row) => `₹${row.issuePrice}`
    },
    {
      header: 'GMP (₹)',
      accessor: 'gmp',
      render: (row) => (
        <span className={`font-bold ${row.gmp > 0 ? 'text-green-600' : row.gmp < 0 ? 'text-red-600' : 'text-gray-600'}`}>
          {row.gmp > 0 ? '+' : ''}{row.gmp || 0}
        </span>
      )
    },
    {
      header: 'Est. Listing Price',
      accessor: 'estimatedListingPrice',
      render: (row) => <span className="font-semibold text-gray-900">₹{row.estimatedListingPrice || 0}</span>
    },
    {
      header: 'Exp. Gain (%)',
      accessor: 'expectedGainPercent',
      render: (row) => (
        <span className={`font-bold ${row.expectedGainPercent > 0 ? 'text-green-600' : row.expectedGainPercent < 0 ? 'text-red-600' : 'text-gray-600'}`}>
          {row.expectedGainPercent > 0 ? '+' : ''}{row.expectedGainPercent || 0}%
        </span>
      )
    }
  ];

  return (
    <>
      <Helmet>
        <title>Grey Market Premium (GMP) - IPOshala</title>
      </Helmet>
      <PageHeader title="Grey Market Premium (GMP)" subtitle="Live GMP trends and expected listing gains" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Latest GMP Updates" lastUpdated="Live Updates">
          <AdvancedTable
            columns={columns}
            data={gmpData}
            loading={loading}
            emptyMessage="No GMP tracking data available. Ensure scraping pipeline is running."
            emptyType="gmp"
            enableFilters={true}
          />
        </TableContainer>
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-8">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>Disclaimer:</strong> GMP prices are based on market rumors and are not official. They are highly volatile and can change rapidly. Do not trade based solely on GMP.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default GMP;