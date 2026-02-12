import React, { useEffect, useState } from "react";
import TabLoader from "@/components/common/TabLoader";
import { getCompanyQuote } from "@/services/company";

const fmt2 = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(2) : (v ?? "-");
};

const Field = ({ label, value }) => (
  <div className="flex justify-between gap-4 py-2 border-b last:border-b-0">
    <div className="text-xs text-gray-500">{label}</div>
    <div className="text-sm font-medium text-[#1a2332] text-right">
      {value ?? "-"}
    </div>
  </div>
);

const Card = ({ title, children }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
    <div className="text-sm font-semibold text-[#1a2332] mb-3">{title}</div>
    {children}
  </div>
);

const extractQuote = (payload) => {
  return (
    payload?.nse_quote ||
    payload?.quote ||
    payload?.data?.nse_quote ||
    payload?.data?.quote ||
    payload?.data ||
    payload ||
    {}
  );
};

const quoteValue = (q, key) => {
  return (
    q?.[key] ??
    q?.priceInfo?.[key] ??
    q?.securityInfo?.[key] ??
    q?.info?.[key] ??
    q?.data?.[key] ??
    q?.data?.priceInfo?.[key] ??
    null
  );
};

const NseOverviewCards = ({ symbol, ipo }) => {
  const [quoteRaw, setQuoteRaw] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!symbol) return;

    setLoading(true);
    setError("");

    getCompanyQuote(symbol)
      .then((data) => setQuoteRaw(data))
      .catch((e) => setError(e.message || "Failed to load quote"))
      .finally(() => setLoading(false));
  }, [symbol]);

  const q = extractQuote(quoteRaw);

  const change = quoteValue(q, "change");
  const pChange = quoteValue(q, "pChange");
  const isUp = Number(change ?? 0) >= 0;

  if (loading) return <TabLoader text="Loading NSE overview..." />;
  if (error) return <div className="text-sm text-red-600">{error}</div>;

  return (
    <div className="space-y-6">
      {/* Top LTP strip */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm flex flex-wrap items-center gap-6">
        <div>
          <div className="text-xs text-gray-500">LTP</div>
          <div className="text-xl font-bold">
            {fmt2(quoteValue(q, "lastPrice"))}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500">Change</div>
          <div
            className={`text-lg font-bold ${isUp ? "text-green-600" : "text-red-600"
              }`}
          >
            {fmt2(change)} ({fmt2(pChange)}%)
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500">Previous Close</div>
          <div className="text-lg font-semibold">
            {fmt2(quoteValue(q, "previousClose"))}
          </div>
        </div>
      </div>

      {/* 4 cards grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Issue Info */}
        <Card title="Issue Information">
          <Field label="Issue Start Date" value={ipo?.issue_start_date} />
          <Field label="Issue End Date" value={ipo?.issue_end_date} />
          <Field label="Listing Date" value={ipo?.listing_date || "-"} />
          <Field
            label="Price / Range"
            value={ipo?.issue_price !== "-" ? ipo?.issue_price : ipo?.price_range}
          />
          <Field label="Issue Size" value={ipo?.issue_size || "-"} />
          <Field label="Lot Size" value={ipo?.lot_size || "-"} />
        </Card>

        {/* Trade Info */}
        <Card title="Trade Information">
          <Field label="Total Traded Volume" value={fmt2(quoteValue(q, "totalTradedVolume"))} />
          <Field label="Total Traded Value" value={fmt2(quoteValue(q, "totalTradedValue"))} />
          <Field
            label="VWAP"
            value={fmt2(quoteValue(q, "averagePrice") ?? quoteValue(q, "vwap"))}
          />
          <Field label="No. of Trades" value={quoteValue(q, "totalTrades") ?? "-"} />
          <Field label="Face Value" value={fmt2(quoteValue(q, "faceValue"))} />
        </Card>

        {/* Price Info */}
        <Card title="Price Information">
          <Field label="Open" value={fmt2(quoteValue(q, "open"))} />
          <Field label="Close" value={fmt2(quoteValue(q, "close"))} />
          <Field label="Day High" value={fmt2(quoteValue(q, "dayHigh"))} />
          <Field label="Day Low" value={fmt2(quoteValue(q, "dayLow"))} />
          <Field label="52W High" value={fmt2(q?.weekHighLow?.max)} />
          <Field label="52W Low" value={fmt2(q?.weekHighLow?.min)} />
          <Field label="Upper Circuit" value={fmt2(quoteValue(q, "upperCP"))} />
          <Field label="Lower Circuit" value={fmt2(quoteValue(q, "lowerCP"))} />
        </Card>

        {/* Security Info */}
        <Card title="Security Information">
          <Field label="ISIN" value={quoteValue(q, "isin")} />
          <Field label="Trading Status" value={q?.securityInfo?.tradingStatus ?? "-"} />
          <Field label="Market" value={q?.securityInfo?.market ?? "-"} />
          <Field
            label="Face Value"
            value={fmt2(q?.securityInfo?.faceValue ?? quoteValue(q, "faceValue"))}
          />
          <Field label="Series" value={q?.securityInfo?.series ?? "-"} />
        </Card>
      </div>
    </div>
  );
};

export default NseOverviewCards;
