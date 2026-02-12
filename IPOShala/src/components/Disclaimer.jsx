import React from 'react';
import { AlertCircle } from 'lucide-react';

const Disclaimer = () => {
  return (
    <section className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-3">
              <h3 className="text-lg font-bold text-[#1a2332]">Important Disclaimer</h3>
              <div className="text-sm text-gray-700 space-y-2">
                <p>
                  <strong>Information Accuracy:</strong> The information provided on this platform is compiled from publicly available sources including company filings, stock exchange notifications, and regulatory announcements. While we strive for accuracy, IPOshala does not guarantee the completeness or accuracy of the information presented.
                </p>
                <p>
                  <strong>Investment Advisory:</strong> This platform is for informational purposes only and does not constitute investment advice, recommendation, or solicitation to buy or sell securities. Investors should conduct their own due diligence and consult with qualified financial advisors before making investment decisions.
                </p>
                <p>
                  <strong>Grey Market Premium (GMP):</strong> GMP data is sourced from unofficial grey market channels and should be treated as indicative only. GMP values are subject to rapid fluctuations and may not reflect actual listing prices.
                </p>
                <p>
                  <strong>Regulatory Compliance:</strong> All IPO investments are subject to SEBI regulations and exchange guidelines. Investors must comply with all applicable laws and regulations in their jurisdiction.
                </p>
                <p>
                  <strong>Risk Warning:</strong> Investing in IPOs carries inherent risks including price volatility, market risk, and potential loss of capital. Past performance is not indicative of future results.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Disclaimer;