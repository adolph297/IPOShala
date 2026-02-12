import React from 'react';

const UpcomingIPOsTable = () => {
  const upcomingIPOs = [
    {
      companyName: 'Digital Payments Ltd',
      expectedDate: '25-Jan-2026',
      issueSize: '₹4,500 Cr',
      exchange: 'NSE, BSE',
      drhpFiled: 'Yes',
      status: 'SEBI Approved'
    },
    {
      companyName: 'Retail Ventures Inc',
      expectedDate: '02-Feb-2026',
      issueSize: '₹1,200 Cr',
      exchange: 'NSE, BSE',
      drhpFiled: 'Yes',
      status: 'SEBI Approved'
    },
    {
      companyName: 'Auto Components Pro',
      expectedDate: '10-Feb-2026',
      issueSize: '₹850 Cr',
      exchange: 'NSE',
      drhpFiled: 'Yes',
      status: 'Under Review'
    },
    {
      companyName: 'Food & Beverages Co',
      expectedDate: '15-Feb-2026',
      issueSize: '₹2,100 Cr',
      exchange: 'NSE, BSE',
      drhpFiled: 'Yes',
      status: 'SEBI Approved'
    },
    {
      companyName: 'Manufacturing Hub',
      expectedDate: '20-Feb-2026',
      issueSize: '₹3,300 Cr',
      exchange: 'BSE',
      drhpFiled: 'No',
      status: 'Expected'
    },
    {
      companyName: 'Logistics Express',
      expectedDate: '28-Feb-2026',
      issueSize: '₹1,750 Cr',
      exchange: 'NSE, BSE',
      drhpFiled: 'Yes',
      status: 'Under Review'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-[#1a2332] mb-6">Upcoming IPOs</h2>
      <div className="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#1a2332]">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Company Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Expected Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Issue Size
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Exchange
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  DRHP Filed
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-white uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {upcomingIPOs.map((ipo, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="px-4 py-4 text-sm font-medium text-[#1a2332]">
                    {ipo.companyName}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.expectedDate}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.issueSize}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.exchange}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-700">
                    {ipo.drhpFiled}
                  </td>
                  <td className="px-4 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      ipo.status === 'SEBI Approved' 
                        ? 'bg-green-100 text-green-800' 
                        : ipo.status === 'Under Review'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}>
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

export default UpcomingIPOsTable;