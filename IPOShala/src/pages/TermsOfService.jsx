import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';

const TermsOfService = () => {
  return (
    <>
      <Helmet>
        <title>Terms of Service - IPOshala</title>
      </Helmet>
      <PageHeader title="Terms of Service" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white p-8 rounded-lg border border-gray-200 prose max-w-none text-gray-700">
             <p className="mb-4">Last updated: January 2026</p>
          <p className="mb-4">
            Please read these Terms of Service carefully before using the IPOshala website.
          </p>

          <h3 className="text-xl font-bold text-[#1a2332] mt-6 mb-3">Acceptance of Terms</h3>
          <p className="mb-4">
            By accessing or using our service, you agree to be bound by these terms. If you disagree with any part of the terms, then you may not access the service.
          </p>

          <h3 className="text-xl font-bold text-[#1a2332] mt-6 mb-3">Data Accuracy</h3>
          <p className="mb-4">
            The data provided on IPOshala is for informational purposes only. While we strive for accuracy, we make no guarantees regarding the completeness or accuracy of any information.
          </p>

          <h3 className="text-xl font-bold text-[#1a2332] mt-6 mb-3">Investment Disclaimer</h3>
          <p className="mb-4">
            IPOshala is not an investment advisor. The information provided does not constitute investment advice. Users should consult with a qualified financial advisor before making any investment decisions.
          </p>
        </div>
      </div>
    </>
  );
};

export default TermsOfService;