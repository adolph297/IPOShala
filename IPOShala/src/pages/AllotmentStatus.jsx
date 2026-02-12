import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import { Search } from 'lucide-react';

const AllotmentStatus = () => {
  return (
    <>
      <Helmet>
        <title>Allotment Status - IPOshala</title>
      </Helmet>
      <PageHeader title="IPO Allotment Status" subtitle="Check your application status" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 max-w-2xl mx-auto">
          <div className="space-y-6">
            <div>
              <label htmlFor="ipo-select" className="block text-sm font-medium text-gray-700 mb-2">Select IPO</label>
              <select id="ipo-select" className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md border p-2">
                <option>Select Company</option>
                <option>Retail Chain Ltd</option>
                <option>BioChem Labs</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="pan-number" className="block text-sm font-medium text-gray-700 mb-2">PAN Number / Application No</label>
              <input type="text" id="pan-number" className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="Enter PAN or Application Number" />
            </div>

            <button className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#1a2332] hover:bg-[#2a3442] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 items-center gap-2">
              <Search size={18} />
              Check Status
            </button>
          </div>
          <div className="mt-6 text-sm text-gray-500 text-center">
            <p>Data provided by respective Registrar & Transfer Agents (RTA).</p>
          </div>
        </div>
      </div>
    </>
  );
};

export default AllotmentStatus;