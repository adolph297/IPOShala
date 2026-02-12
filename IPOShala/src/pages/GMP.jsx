import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import TableContainer from '@/components/common/TableContainer';

const GMP = () => {
  const gmpData = [
    { name: 'Tech Solutions Ltd', price: '₹475', gmp: '₹85', estListing: '₹560', gain: '17.89%', type: 'Mainboard' },
    { name: 'Creative Tech SME', price: '₹85', gmp: '₹40', estListing: '₹125', gain: '47.05%', type: 'SME' },
    { name: 'FinTech Innovations', price: '₹620', gmp: '₹125', estListing: '₹745', gain: '20.16%', type: 'Mainboard' },
    { name: 'Green Energy Corp', price: '₹340', gmp: '₹45', estListing: '₹385', gain: '13.23%', type: 'Mainboard' },
  ];

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
              {gmpData.map((data, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#1a2332]">{data.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{data.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{data.price}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">+{data.gmp}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">{data.estListing}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">+{data.gain}</td>
                </tr>
              ))}
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