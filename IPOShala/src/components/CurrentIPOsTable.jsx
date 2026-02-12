import React from 'react';

const CurrentIPOsTable = () => {
  const currentIPOs = [
    {
      companyName: 'Tech Solutions Ltd',
      issueType: 'Book Built',
      priceBand: '₹450-475',
      issueSize: '₹2,500 Cr',
      openDate: '15-Jan-2026',
      closeDate: '17-Jan-2026',
      subscription: '3.45x',
      gmp: '₹85',
      status: 'Open'
    },
    {
      companyName: 'Green Energy Corp',
      issueType: 'Book Built',
      priceBand: '₹320-340',
      issueSize: '₹1,800 Cr',
      openDate: '16-Jan-2026',
      closeDate: '18-Jan-2026',
      subscription: '1.89x',
      gmp: '₹45',
      status: 'Open'
    },
    {
      companyName: 'FinTech Innovations',
      issueType: 'Book Built',
      priceBand: '₹580-620',
      issueSize: '₹3,200 Cr',
      openDate: '14-Jan-2026',
      closeDate: '16-Jan-2026',
      subscription: '5.67x',
      gmp: '₹125',
      status: 'Open'
    },
    {
      companyName: 'Healthcare Plus',
      issueType: 'Fixed Price',
      priceBand: '₹215',
      issueSize: '₹950 Cr',
      openDate: '17-Jan-2026',
      closeDate: '19-Jan-2026',
      subscription: '0.78x',
      gmp: '₹12',
      status: 'Open'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-[#1a2332] mb-6">Current IPOs</h2>
      <div className="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#1a2332]">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Company Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Issue Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Price Band
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Issue Size
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Open Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Close Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Subscription
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  GMP
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {currentIPOs.map((ipo, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="px-4 py-4 text-sm font-medium text-[#1a2332]">
                    {ipo.companyName}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.issueType}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.priceBand}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.issueSize}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.openDate}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.closeDate}
                  </td>
                  <td className="px-4 py-4 text-sm font-medium text-green-700">
                    {ipo.subscription}
                  </td>
                  <td className="px-4 py-4 text-sm font-medium text-green-700">
                    {ipo.gmp}
                  </td>
                  <td className="px-4 py-4">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      {ipo.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CurrentIPOsTable;