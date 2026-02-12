import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import TableContainer from '@/components/common/TableContainer';

const MainboardIPOs = () => {
  const ipoData = [
    { name: 'Tech Solutions Ltd', openDate: '15-Jan-2026', closeDate: '17-Jan-2026', price: '₹450-475', lot: '30', size: '2,500 Cr', status: 'Open' },
    { name: 'Green Energy Corp', openDate: '16-Jan-2026', closeDate: '18-Jan-2026', price: '₹320-340', lot: '45', size: '1,800 Cr', status: 'Open' },
    { name: 'FinTech Innovations', openDate: '14-Jan-2026', closeDate: '16-Jan-2026', price: '₹580-620', lot: '25', size: '3,200 Cr', status: 'Closed' },
  ];

  return (
    <>
      <Helmet>
        <title>Mainboard IPOs - IPOshala</title>
      </Helmet>
      <PageHeader title="Mainboard IPOs" subtitle="List of all Mainboard IPOs listed on NSE & BSE" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <TableContainer title="Active & Recent Mainboard IPOs" lastUpdated="Today 10:30 AM">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#1a2332]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Open Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Close Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Price Band</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Lot Size</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Issue Size</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {ipoData.map((ipo, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#1a2332]">{ipo.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.openDate}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.closeDate}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.price}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.lot}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{ipo.size}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${ipo.status === 'Open' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
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

export default MainboardIPOs;