import React, { useEffect, useState } from "react";
import { Helmet } from "react-helmet";
import PageHeader from "@/components/common/PageHeader";
import TableContainer from "@/components/common/TableContainer";
import { Link } from "react-router-dom";
import { getClosedIPOs } from "../services/ipos";

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
          {loading ? (
            <div className="text-center py-8 text-gray-500">
              Loading closed IPOs...
            </div>
          ) : closedData.length === 0 ? (
            <div className="text-center py-10 text-gray-500">
              No closed IPOs found.
            </div>
          ) : (
            <div className="w-full overflow-x-auto">
              <div className="max-h-[520px] overflow-y-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-[#1a2332] sticky top-0 z-10">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase">
                        Close Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase">
                        Final Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase">
                        Current Status
                      </th>
                    </tr>
                  </thead>

                  <tbody className="bg-white divide-y divide-gray-200">
                    {closedData.map((ipo) => (
                      <tr key={ipo.symbol} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-[#1a2332]">
                          <Link
                            to={`/ipo/${ipo.symbol}`}
                            className="text-blue-600 hover:underline"
                          >
                            {ipo.company_name}
                          </Link>
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-700">
                          {ipo.security_type}
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-700">
                          {ipo.issue_end_date || "-"}
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-700">
                          {ipo.issue_price || ipo.price_range || "-"}
                        </td>

                        <td className="px-6 py-4 text-sm font-medium text-orange-600">
                          Closed
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </TableContainer>
      </div>
    </>
  );
};

export default ClosedIPOs;
