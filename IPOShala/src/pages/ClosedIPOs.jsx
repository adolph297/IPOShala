import React, { useEffect, useState } from "react";
import { Helmet } from "react-helmet";
import PageHeader from "@/components/common/PageHeader";
import TableContainer from "@/components/common/TableContainer";
import { Link } from "react-router-dom";
import { getClosedIPOs } from "../services/ipos";
import AdvancedTable from "@/components/common/AdvancedTable";

const ClosedIPOs = () => {
  const [closedData, setClosedData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    getClosedIPOs()
      .then((data) => {
        setClosedData(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch closed IPOs", err);
        setLoading(false);
      });
  }, []);

  const columns = [
    {
      header: 'Company',
      accessor: 'company_name',
      render: (row) => (
        <Link
          to={`/ipo/${row.ipo_id || row.symbol}`}
          className="text-blue-600 hover:underline font-medium"
        >
          {row.company_name}
        </Link>
      )
    },
    { header: 'Type', accessor: 'security_type' },
    { header: 'Close Date', accessor: 'issue_end_date' },
    {
      header: 'Final Price',
      accessor: 'issue_price',
      render: (row) => row.issue_price || row.price_range || '-'
    },
    {
      header: 'Current Status',
      accessor: 'status',
      render: () => <span className="font-medium text-orange-600">Closed</span>
    }
  ];

  return (
    <>
      <Helmet>
        <title>Closed IPOs - IPOshala</title>
      </Helmet>

      <PageHeader
        title="Closed IPOs"
        subtitle="Recently closed for subscription, awaiting listing"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Recently Closed Issues" lastUpdated="Live">
          <AdvancedTable
            columns={columns}
            data={closedData}
            loading={loading}
            emptyMessage="No closed IPOs found."
            emptyType="default"
            enableFilters={true}
          />
        </TableContainer>
      </div>
    </>
  );
};

export default ClosedIPOs;
