import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Home from '@/pages/Home';
import MainboardIPOs from '@/pages/MainboardIPOs';
import SMEIPOs from '@/pages/SMEIPOs';
import UpcomingIPOs from '@/pages/UpcomingIPOs';
import CurrentIPOs from '@/pages/CurrentIPOs';
import ClosedIPOs from '@/pages/ClosedIPOs';
import GMP from '@/pages/GMP';
import About from '@/pages/About';
import SubscriptionStatus from '@/pages/SubscriptionStatus';
import AllotmentStatus from '@/pages/AllotmentStatus';
import ListingPerformance from '@/pages/ListingPerformance';
import InvestmentGuide from '@/pages/InvestmentGuide';
import FAQ from '@/pages/FAQ';
import Contact from '@/pages/Contact';
import PrivacyPolicy from '@/pages/PrivacyPolicy';
import TermsOfService from '@/pages/TermsOfService';
import ScrollToTop from '@/components/ScrollToTop';
import { Toaster } from '@/components/ui/toaster';
import IPODetails from '@/pages/IPODetails';
import ChartDemo from '@/pages/ChartDemo';


function App() {
  return (
    <Router>
      <Helmet>
        <title>IPOshala - India's IPO Information Platform</title>
        <meta name="description" content="Comprehensive IPO information platform for Mainboard and SME IPOs, GMP updates, subscription status, and listing gains." />
      </Helmet>
      <ScrollToTop />
      <div className="min-h-screen bg-white flex flex-col">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/mainboard-ipos" element={<MainboardIPOs />} />
            <Route path="/sme-ipos" element={<SMEIPOs />} />
            <Route path="/upcoming-ipos" element={<UpcomingIPOs />} />
            <Route path="/current-ipos" element={<CurrentIPOs />} />
            <Route path="/closed-ipos" element={<ClosedIPOs />} />
            <Route path="/ipo/:symbol" element={<IPODetails />} />
            <Route path="/gmp" element={<GMP />} />
            <Route path="/about" element={<About />} />
            <Route path="/gmp-tracker" element={<GMP />} />
            <Route path="/subscription-status" element={<SubscriptionStatus />} />
            <Route path="/allotment-status" element={<AllotmentStatus />} />
            <Route path="/listing-performance" element={<ListingPerformance />} />
            <Route path="/investment-guide" element={<InvestmentGuide />} />
            <Route path="/faq" element={<FAQ />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms-of-service" element={<TermsOfService />} />
            <Route path="/chart-demo" element={<ChartDemo />} />
          </Routes>
        </main>
        <Footer />
        <Toaster />
      </div>
    </Router>
  );
}

export default App;