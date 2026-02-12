import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import TableContainer from '@/components/common/TableContainer';

const SubscriptionStatus = () => {
  const subData = [
    { name: 'Tech Solutions Ltd', qib: '5.2x', nii: '8.4x', retail: '12.1x', employee: '1.5x', total: '8.6x' },
    { name: 'Green Energy Corp', qib: '2.1x', nii: '3.5x', retail: '4.8x', employee: '0.9x', total: '3.4x' },
    { name: 'Creative Tech SME', qib: '-', nii: '45.2x', retail: '85.6x', employee: '-', total: '65.4x' },
  ];

  return (
    <>
      <Helmet>
        <title>Subscription Status - IPOshala</title>
      </Helmet>
      <PageHeader title="Live Subscription Status" subtitle="Real-time bidding details by category" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Live Subscription Numbers" lastUpdated="Live Updates">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#1a2332]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">QIB</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">NII</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Retail</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Employee</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Total</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {subData.map((data, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#1a2332]">{data.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.qib}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.nii}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.retail}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.employee}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600">{data.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableContainer>
      </div>
    </>
  );
};

export default SubscriptionStatus;