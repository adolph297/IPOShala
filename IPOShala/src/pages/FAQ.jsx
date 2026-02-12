import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';

const FAQ = () => {
  const faqs = [
    {
      q: "What is ASBA?",
      a: "ASBA (Application Supported by Blocked Amount) is a process developed by SEBI for applying to IPOs. In ASBA, an applicant's account doesn't get debited until shares are allotted to them."
    },
    {
      q: "What happens if I don't get allotment?",
      a: "If you do not get any allotment, the blocked amount in your bank account will be unblocked (released) typically within 1-2 working days after the allotment date."
    },
    {
      q: "What is Cut-off Price?",
      a: "The Cut-off price is the offer price at which the shares are issued to the investors. Retail investors can bid at the 'Cut-off' price, meaning they are willing to buy at the final price determined within the price band."
    },
    {
      q: "Can I apply for an IPO without a Demat account?",
      a: "No, a Demat account is mandatory to apply for an IPO in India as shares are credited only in electronic form."
    }
  ];

  return (
    <>
      <Helmet>
        <title>FAQ - IPOshala</title>
      </Helmet>
      <PageHeader title="Frequently Asked Questions" subtitle="Common queries about IPO investing" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid gap-6">
          {faqs.map((faq, idx) => (
            <div key={idx} className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-[#1a2332] mb-2">{faq.q}</h3>
              <p className="text-gray-700">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default FAQ;