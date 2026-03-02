import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getLiveIPOs } from '../services/ipos';
import AdvancedTable from './common/AdvancedTable';

const CurrentIPOsTable = () => {
  const [currentIPOs, setCurrentIPOs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getLiveIPOs()
      .then((data) => {
        if (Array.isArray(data)) {
          const formatted = data.map(ipo => {
            // Format dates
            let openDate = 'TBD';
            let closeDate = 'TBD';

            if (ipo.issue_start_date) {
              const dt = new Date(ipo.issue_start_date);
              if (!isNaN(dt)) openDate = dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-');
            }
            if (ipo.issue_end_date) {
              const dt = new Date(ipo.issue_end_date);
              if (!isNaN(dt)) closeDate = dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-');
            }

            return {
              companyName: ipo.company_name || ipo.symbol,
              issueType: ipo.security_type === 'SME' ? 'SME' : 'Book Built',
              priceBand: ipo.price_range || 'N/A',
              issueSize: ipo.issue_size ? `₹${ipo.issue_size} Cr` : 'TBD',
              openDate: openDate,
              closeDate: closeDate,
              subscription: 'N/A',
              gmp: 'N/A',
              status: ipo.status || 'LIVE',
              symbol: ipo.symbol,
              ipo_id: ipo.ipo_id || ipo.symbol
            };
          });
          setCurrentIPOs(formatted);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch live IPOs:", err);
        setLoading(false);
      });
  }, []);

  const columns = [
    {
      header: 'Company Name',
      accessor: 'companyName',
      render: (row) => (
        <Link to={`/ipo/${row.ipo_id}`} className="text-blue-600 hover:text-blue-800 hover:underline font-medium">
          {row.companyName}
        </Link>
      )
    },
    { header: 'Issue Type', accessor: 'issueType' },
    { header: 'Price Band', accessor: 'priceBand', sortable: false },
    { header: 'Issue Size', accessor: 'issueSize' },
    { header: 'Open Date', accessor: 'openDate' },
    { header: 'Close Date', accessor: 'closeDate' },
    { header: 'Subscription', accessor: 'subscription' },
    { header: 'GMP', accessor: 'gmp' },
    {
      header: 'Status',
      accessor: 'status',
      render: (row) => (
        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
          {row.status}
        </span>
      )
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-[#1a2332] mb-6">Current IPOs</h2>
      <AdvancedTable
        columns={columns}
        data={currentIPOs}
        loading={loading}
        emptyMessage="No Current IPOs found."
      />
    </div>
  );
};

export default CurrentIPOsTable;