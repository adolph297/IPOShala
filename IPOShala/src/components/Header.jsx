import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const menuItems = [
    { name: 'Home', path: '/' },
    { name: 'Mainboard IPOs', path: '/mainboard-ipos' },
    { name: 'SME IPOs', path: '/sme-ipos' },
    { name: 'Upcoming IPOs', path: '/upcoming-ipos' },
    { name: 'Current IPOs', path: '/current-ipos' },
    { name: 'Closed IPOs', path: '/closed-ipos' },
    { name: 'GMP', path: '/gmp' },
    { name: 'About', path: '/about' }
  ];

  return (
    <header className="bg-[#1a2332] border-b border-gray-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/">
              <img 
                src="https://horizons-cdn.hostinger.com/250e55c4-98e6-4e8f-8c23-b04373e3acd1/66cfe7958c5021d72b6a93182bcc1f46.png"
                alt="IPOshala Logo"
                className="h-10 w-auto"
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center space-x-1">
            {menuItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={cn(
                  "px-3 py-2 text-sm font-medium rounded transition-colors duration-200",
                  location.pathname === item.path 
                    ? "text-white bg-[#2a3442]" 
                    : "text-gray-200 hover:text-white hover:bg-[#2a3442]"
                )}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Mobile menu button */}
          <button
            className="lg:hidden p-2 text-gray-200 hover:text-white hover:bg-[#2a3442] rounded transition-colors duration-200"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="lg:hidden pb-4">
            {menuItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={cn(
                    "block px-3 py-2 text-sm font-medium rounded transition-colors duration-200",
                    location.pathname === item.path 
                      ? "text-white bg-[#2a3442]" 
                      : "text-gray-200 hover:text-white hover:bg-[#2a3442]"
                  )}
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;