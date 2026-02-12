import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {

  const footerLinks = {
    'IPO Information': [
      { name: 'Current IPOs', path: '/current-ipos' },
      { name: 'Upcoming IPOs', path: '/upcoming-ipos' },
      { name: 'Closed IPOs', path: '/closed-ipos' },
      { name: 'IPO Calendar', path: '/upcoming-ipos' } // Reusing upcoming for calendar
    ],
    'Market Data': [
      { name: 'GMP Tracker', path: '/gmp-tracker' },
      { name: 'Subscription Status', path: '/subscription-status' },
      { name: 'Allotment Status', path: '/allotment-status' },
      { name: 'Listing Performance', path: '/listing-performance' }
    ],
    'Resources': [
      { name: 'Mainboard IPOs', path: '/mainboard-ipos' },
      { name: 'SME IPOs', path: '/sme-ipos' },
      { name: 'Investment Guide', path: '/investment-guide' },
      { name: 'FAQ', path: '/faq' }
    ],
    'Company': [
      { name: 'About Us', path: '/about' },
      { name: 'Contact', path: '/contact' },
      { name: 'Privacy Policy', path: '/privacy-policy' },
      { name: 'Terms of Service', path: '/terms-of-service' }
    ]
  };

  return (
    <footer className="bg-[#1a2332] text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          <div className="lg:col-span-1">
            <img 
              src="https://horizons-cdn.hostinger.com/250e55c4-98e6-4e8f-8c23-b04373e3acd1/66cfe7958c5021d72b6a93182bcc1f46.png"
              alt="IPOshala Logo"
              className="h-10 w-auto mb-4"
            />
            <p className="text-sm text-gray-400">
              India's comprehensive IPO information platform
            </p>
          </div>

          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <span className="text-sm font-semibold text-white uppercase tracking-wider block mb-4">
                {category}
              </span>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className="text-sm hover:text-white transition-colors duration-200"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex flex-col gap-1">
                <p className="text-sm text-gray-400">
                © 2026 IPOshala. Powered by Rusaka Technologies Private Limited.
                </p>
                <p className="text-xs text-gray-500">
                    Support: admin@rusaka.com
                </p>
            </div>
            
            <p className="text-xs text-gray-500">
              Data sources: NSE, BSE, SEBI filings, and company announcements
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;