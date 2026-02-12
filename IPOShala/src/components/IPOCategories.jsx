import React from 'react';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const IPOCategories = () => {

  const categories = [
    { name: 'Mainboard IPOs', path: '/mainboard-ipos' },
    { name: 'SME IPOs', path: '/sme-ipos' },
    { name: 'IPO Calendar', path: '/upcoming-ipos' },
    { name: 'GMP Tracker', path: '/gmp' },
    { name: 'Allotment Status', path: '/allotment-status' },
    { name: 'Listing Gains/Losses', path: '/listing-performance' }
  ];

  return (
    <section className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-[#1a2332] mb-8">IPO Categories</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <Link
              key={category.name}
              to={category.path}
              className="bg-white border border-gray-200 rounded-lg p-6 text-left hover:border-[#1a2332] hover:shadow-md transition-all duration-200 group block"
            >
              <div className="flex items-center justify-between">
                <span className="text-base font-semibold text-[#1a2332]">
                  {category.name}
                </span>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-[#1a2332] group-hover:translate-x-1 transition-all duration-200" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default IPOCategories;