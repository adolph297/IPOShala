import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';

const About = () => {
  return (
    <>
      <Helmet>
        <title>About Us - IPOshala</title>
      </Helmet>
      <PageHeader title="About IPOshala" subtitle="Democratizing IPO information for Indian investors" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-[#1a2332] mb-4">Our Mission</h2>
          <p className="text-gray-700 mb-6 leading-relaxed">
            IPOshala serves as a comprehensive, institutional-grade information platform dedicated to the Indian Primary Market. Our mission is to provide retail and HNI investors with accurate, real-time data on Mainboard and SME IPOs, enabling informed investment decisions.
          </p>

          <h2 className="text-2xl font-bold text-[#1a2332] mb-4">What We Offer</h2>
          <ul className="list-disc list-inside space-y-3 text-gray-700 mb-8">
            <li>Real-time subscription status updates across all investor categories.</li>
            <li>Accurate Grey Market Premium (GMP) trends tracking.</li>
            <li>Comprehensive analysis of upcoming and current IPOs.</li>
            <li>Detailed allotment status checking tools.</li>
            <li>Historical listing performance data and analytics.</li>
          </ul>

          <h2 className="text-2xl font-bold text-[#1a2332] mb-4">Data Integrity</h2>
          <p className="text-gray-700 leading-relaxed">
            We source our data directly from primary sources including the National Stock Exchange (NSE), Bombay Stock Exchange (BSE), and SEBI filings. Our dedicated research team validates all information before publication to ensure the highest standards of accuracy.
          </p>
        </div>
      </div>
    </>
  );
};

export default About;