import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';

const InvestmentGuide = () => {
  return (
    <>
      <Helmet>
        <title>Investment Guide - IPOshala</title>
      </Helmet>
      <PageHeader title="IPO Investment Guide" subtitle="Essential knowledge for primary market investors" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">
          <section className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-xl font-bold text-[#1a2332] mb-4">1. Understanding IPOs</h2>
            <p className="text-gray-700">An Initial Public Offering (IPO) is the process by which a private company offers shares to the public in a new stock issuance. It allows companies to raise capital from public investors.</p>
          </section>

          <section className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-xl font-bold text-[#1a2332] mb-4">2. Investor Categories</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-semibold mb-2">Retail Individual Investors (RII)</h3>
                <p className="text-sm text-gray-600">Investments up to ₹2 Lakhs. Usually 35% of the issue is reserved for this category.</p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-semibold mb-2">Non-Institutional Investors (NII/HNI)</h3>
                <p className="text-sm text-gray-600">Investments above ₹2 Lakhs. Divided into sNII (2L-10L) and bNII (10L+).</p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-semibold mb-2">Qualified Institutional Buyers (QIB)</h3>
                <p className="text-sm text-gray-600">Mutual funds, banks, and insurance companies. Usually 50% reservation.</p>
              </div>
            </div>
          </section>

          <section className="bg-white p-6 rounded-lg border border-gray-200">
            <h2 className="text-xl font-bold text-[#1a2332] mb-4">3. Application Process</h2>
            <ol className="list-decimal list-inside space-y-2 text-gray-700">
              <li>Open a Demat and Trading account with a registered broker.</li>
              <li>Setup UPI ID for payment blocking (ASBA).</li>
              <li>Select the IPO and enter bid details (Quantity & Price).</li>
              <li>Accept the mandate on your UPI app to block funds.</li>
              <li>Wait for allotment status on the specified date.</li>
            </ol>
          </section>
        </div>
      </div>
    </>
  );
};

export default InvestmentGuide;