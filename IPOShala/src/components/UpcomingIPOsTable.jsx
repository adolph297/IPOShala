import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getUpcomingIPOs } from '../services/ipos';
import AdvancedTable from './common/AdvancedTable';

const UpcomingIPOsTable = () => {
  const [upcomingIPOs, setUpcomingIPOs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getUpcomingIPOs()
      .then((data) => {
        if (Array.isArray(data)) {
          const formatted = data.map(ipo => {
            const info = ipo.issue_information || {};
            // Start Date
            let startDate = info.issue_start_date || 'TBD';
            if (startDate !== 'TBD' && startDate.includes('-') && !isNaN(new Date(startDate))) {
              // Formatting might not be strictly necessary if it comes formatted as '04-Mar-2026' from scraping, 
              // but just in case it's ISO we'll format it, otherwise leave as is.
              const dt = new Date(startDate);
              if (!isNaN(dt) && startDate.includes('T')) {
                startDate = dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-');
              }
            }
            // End Date
            let endDate = info.issue_end_date || 'TBD';
            if (endDate !== 'TBD' && endDate.includes('-') && !isNaN(new Date(endDate))) {
              const dt = new Date(endDate);
              if (!isNaN(dt) && endDate.includes('T')) {
                endDate = dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-');
              }
            }

            return {
              companyName: ipo.company_name || ipo.symbol,
              symbol: ipo.symbol || '-',
              securityType: ipo.security_type === 'SME' ? 'SME' : 'EQ',
              startDate: startDate,
              endDate: endDate,
              priceRange: info.issue_price && info.issue_price !== '-' ? info.issue_price : 'TBD',
              issueSize: info.issue_size && info.issue_size !== '-' ? info.issue_size : 'TBD',
              status: ipo.status || 'Forthcoming',
              ipo_id: ipo.ipo_id || ipo.symbol
            };
          });
          setUpcomingIPOs(formatted);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch upcoming IPOs:", err);
        setLoading(false);
      });
  }, []);

  const columns = [
    { header: 'Security Type', accessor: 'securityType' },
    {
      header: 'Company Name',
      accessor: 'companyName',
      render: (row) => (
        <Link to={`/ipo/${row.ipo_id}`} className="text-blue-600 hover:text-blue-800 hover:underline font-medium">
          {row.companyName}
        </Link>
      )
    },
    { header: 'Symbol', accessor: 'symbol' },
    { header: 'Issue Start Date', accessor: 'startDate' },
    { header: 'Issue End Date', accessor: 'endDate' },
    { header: 'Price Range', accessor: 'priceRange' },
    { header: 'Issue Size', accessor: 'issueSize' },
    {
      header: 'Status',
      accessor: 'status',
      render: (row) => (
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 uppercase`}>
          {row.status}
        </span>
      )
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-[#1a2332] mb-6">Upcoming IPOs</h2>
      <AdvancedTable
        columns={columns}
        data={upcomingIPOs}
        loading={loading}
        emptyMessage="No Upcoming IPOs found in the pipeline."
        emptyType="calendar"
      />
    </div>
  );
};

export default UpcomingIPOsTable;