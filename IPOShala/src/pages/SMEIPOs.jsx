import React, { useEffect, useState } from "react";
import { Helmet } from "react-helmet";
import PageHeader from "@/components/common/PageHeader";
import TableContainer from "@/components/common/TableContainer";
import { Link } from "react-router-dom";
import { getClosedIPOs } from "../services/ipos";
import AdvancedTable from "@/components/common/AdvancedTable";

const SMEIPOs = () => {
  const [smeData, setSmeData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    getClosedIPOs('sme')
      .then((data) => {
        setSmeData(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch SME IPOs", err);
        setLoading(false);
      });
  }, []);

  const columns = [
    {
      header: 'Company',
      accessor: 'company_name',
      render: (row) => (
        <Link
          to={`/ipo/${row.symbol}`}
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
      render: (row) => (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
          {row.status}
        </span>
      )
    }
  ];

  return (
    <>
      <Helmet>
        <title>SME IPOs - IPOshala</title>
      </Helmet>

      <PageHeader
        title="SME IPOs"
        subtitle="Small and Medium Enterprise IPOs on NSE Emerge & BSE SME"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Latest SME IPOs" lastUpdated="Live">
          <AdvancedTable
            columns={columns}
            data={smeData}
            loading={loading}
            emptyMessage="No SME IPOs found. The pipeline might be empty."
            emptyType="ipo"
            enableFilters={true}
          />
        </TableContainer>
      </div>
    </>
  );
};

export default SMEIPOs;