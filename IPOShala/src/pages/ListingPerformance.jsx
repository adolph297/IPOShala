import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import TableContainer from '@/components/common/TableContainer';

const ListingPerformance = () => {
  const perfData = [
    { name: 'Auto Components Pro', issuePrice: '₹210', listPrice: '₹315', gain: '+50.00%', current: '₹340' },
    { name: 'Food & Beverages Co', issuePrice: '₹450', listPrice: '₹460', gain: '+2.22%', current: '₹445' },
    { name: 'Logistics Express', issuePrice: '₹180', listPrice: '₹170', gain: '-5.55%', current: '₹165' },
    { name: 'Tech Start Ltd', issuePrice: '₹500', listPrice: '₹950', gain: '+90.00%', current: '₹1100' },
  ];

  return (
    <>
      <Helmet>
        <title>Listing Performance - IPOshala</title>
      </Helmet>
      <PageHeader title="Listing Day Performance" subtitle="Historical analysis of listing gains and losses" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Recent Listing Performance" lastUpdated="Market Close">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#1a2332]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Issue Price</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Listing Price</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Listing Gain/Loss</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Current Price</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {perfData.map((data, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#1a2332]">{data.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.issuePrice}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.listPrice}</td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${data.gain.includes('-') ? 'text-red-600' : 'text-green-600'}`}>{data.gain}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.current}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableContainer>
      </div>
    </>
  );
};

export default ListingPerformance;