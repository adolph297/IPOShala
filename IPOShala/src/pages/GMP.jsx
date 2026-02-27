import React, { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import TableContainer from '@/components/common/TableContainer';
import { getGMPData } from '../services/ipos';
import { Link } from 'react-router-dom';

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

  return (
    <>
      <Helmet>
        <title>Grey Market Premium (GMP) - IPOshala</title>
      </Helmet>
      <PageHeader title="Grey Market Premium (GMP)" subtitle="Live GMP trends and expected listing gains" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Latest GMP Updates" lastUpdated="Live Updates">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#1a2332]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Issue Price</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">GMP (₹)</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Est. Listing Price</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Exp. Gain (%)</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    Loading Live GMP Data...
                  </td>
                </tr>
              ) : gmpData.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    No GMP tracking data available. Ensure scraping pipeline is running.
                  </td>
                </tr>
              ) : (
                gmpData.map((data) => (
                  <tr key={data.ipo_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-[#1a2332]">
                      <Link to={`/ipo/${data.ipo_id}`} className="text-blue-600 hover:underline">
                        {data.companyName}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Mainboard/SME</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">₹{data.issuePrice}</td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${data.gmp > 0 ? 'text-green-600' : data.gmp < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                      {data.gmp > 0 ? '+' : ''}{data.gmp || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">₹{data.estimatedListingPrice || 0}</td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${data.expectedGainPercent > 0 ? 'text-green-600' : data.expectedGainPercent < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                      {data.expectedGainPercent > 0 ? '+' : ''}{data.expectedGainPercent || 0}%
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
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