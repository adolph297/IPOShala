import React from 'react';

const Hero = () => {
  return (
    <section className="bg-gradient-to-b from-[#1a2332] to-[#2a3442] py-16 lg:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-4xl lg:text-5xl font-bold text-white mb-4">
          India's IPO Information Platform
        </h1>
        <p className="text-lg lg:text-xl text-gray-300 max-w-3xl mx-auto">
          Comprehensive real-time information on Mainboard and SME IPOs, GMP updates, subscription status, allotment details, and listing performance
        </p>
      </div>
    </section>
  );
};

export default Hero;