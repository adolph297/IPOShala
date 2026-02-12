import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import TableContainer from '@/components/common/TableContainer';

const SMEIPOs = () => {
  const smeData = [
    { name: 'Creative Tech SME', openDate: '18-Jan-2026', closeDate: '20-Jan-2026', price: '₹85', lot: '1600', size: '12 Cr', status: 'Upcoming' },
    { name: 'Agro Products Ltd', openDate: '12-Jan-2026', closeDate: '14-Jan-2026', price: '₹42', lot: '3000', size: '8.5 Cr', status: 'Closed' },
    { name: 'Solar Components', openDate: '16-Jan-2026', closeDate: '19-Jan-2026', price: '₹110', lot: '1200', size: '25 Cr', status: 'Open' },
  ];

  return (
    <>
      <Helmet>
        <title>SME IPOs - IPOshala</title>
      </Helmet>
      <PageHeader title="SME IPOs" subtitle="Small and Medium Enterprise IPOs on NSE Emerge & BSE SME" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Latest SME IPOs" lastUpdated="Today 11:15 AM">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#1a2332]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Open Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Close Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Price</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Lot Size</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Issue Size</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {smeData.map((ipo, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#1a2332]">{ipo.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.openDate}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.closeDate}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.price}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.lot}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.size}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${ipo.status === 'Open' ? 'bg-green-100 text-green-800' : ipo.status === 'Upcoming' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                      {ipo.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableContainer>
      </div>
    </>
  );
};

export default SMEIPOs;