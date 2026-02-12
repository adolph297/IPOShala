import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';

const PrivacyPolicy = () => {
  return (
    <>
      <Helmet>
        <title>Privacy Policy - IPOshala</title>
      </Helmet>
      <PageHeader title="Privacy Policy" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white p-8 rounded-lg border border-gray-200 prose max-w-none text-gray-700">
          <p className="mb-4">Last updated: January 2026</p>
          <p className="mb-4">
            IPOshala ("we", "our", or "us") respects your privacy and is committed to protecting it through our compliance with this policy.
          </p>
          
          <h3 className="text-xl font-bold text-[#1a2332] mt-6 mb-3">Information We Collect</h3>
          <p className="mb-4">
            We may collect information about you when you use our website, including technical data like IP addresses and browser types. We do not collect personal financial information.
          </p>

          <h3 className="text-xl font-bold text-[#1a2332] mt-6 mb-3">How We Use Your Information</h3>
          <p className="mb-4">
            We use the information we collect to provide, maintain, and improve our services, and to analyze how our services are used.
          </p>

          <h3 className="text-xl font-bold text-[#1a2332] mt-6 mb-3">Cookies</h3>
          <p className="mb-4">
            We use cookies to improve your experience on our site. By using our website, you consent to the use of cookies.
          </p>
        </div>
      </div>
    </>
  );
};

export default PrivacyPolicy;