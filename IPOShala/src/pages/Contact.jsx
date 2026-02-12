import React from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import { Mail } from 'lucide-react';

const Contact = () => {
  return (
    <>
      <Helmet>
        <title>Contact Us - IPOshala</title>
      </Helmet>
      <PageHeader title="Contact Us" subtitle="Get in touch with our team" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-2 gap-12">
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#1a2332]">Reach Out</h2>
            <p className="text-gray-600">
              Have questions about our data, partnerships, or general inquiries? Fill out the form or email us directly.
            </p>
            <div className="flex items-center gap-3 text-gray-700">
              <Mail className="h-5 w-5" />
              <span>admin@rusaka.com</span>
            </div>
          </div>

          <div className="bg-white p-8 rounded-lg border border-gray-200 shadow-sm">
            <form className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input type="text" className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                <textarea rows="4" className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2"></textarea>
              </div>
              <button type="button" className="w-full bg-[#1a2332] text-white py-2 px-4 rounded-md hover:bg-[#2a3442] transition-colors">
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default Contact;