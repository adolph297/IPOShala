import React, { useEffect, useMemo, useState } from "react";
import ShareholdingDonut from "@/components/company/ShareholdingDonut";
import TabLoader from "@/components/common/TabLoader";
import CompanyTable from "@/components/company/CompanyTable";

import {
  getCompanyTabs,
  getCompanyQuote,
  getAnnouncements,
  getCorporateActions,
  getAnnualReports,
  getBRSRReports,
  getShareholdingPattern,
  getFinancialResults,
  getBoardMeetings,
  getEventCalendar,
  getCompanyHistorical, // ✅ ADDED
} from "@/services/company";

const TABS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "quote", label: "Quote" },
  { key: "historical", label: "Historical Data" }, // ✅ ADDED
  { key: "announcements", label: "Announcements" },
  { key: "corporate_actions", label: "Corporate Actions" },
  { key: "annual_reports", label: "Annual Reports" },
  { key: "brsr_reports", label: "BRSR Reports" },
  { key: "shareholding_pattern", label: "Shareholding Pattern" },
  { key: "financial_results", label: "Financial Results" },
  { key: "board_meetings", label: "Board Meetings" },
  { key: "event_calendar", label: "Event Calendar" },
];

/** ✅ Extract quote safely regardless of nesting */
const extractQuote = (payload) =>
  payload?.nse_quote ||
  payload?.quote ||
  payload?.data?.nse_quote ||
  payload?.data?.quote ||
  payload?.data ||
  payload ||
  {};

/** ✅ Quote field helper */
const quoteValue = (q, key) =>
  q?.[key] ??
  q?.priceInfo?.[key] ??
  q?.securityInfo?.[key] ??
  q?.info?.[key] ??
  q?.data?.[key] ??
  q?.data?.priceInfo?.[key] ??
  null;

/** ✅ NSE attachment link helper */
const extractAnnouncementUrl = (r) =>
  r?.attchmntFile || r?.url || r?.link || r?.attachment || r?.pdf || null;

/** ✅ NSE wrapper helpers */
const isUnavailableSection = (obj) =>
  obj && typeof obj === "object" && (obj.__available__ === false || obj.available === false);

const unwrapNseSection = (obj) => {
  // selenium wrapper style { __available__, data, url }
  if (obj && typeof obj === "object") {
    if ("__available__" in obj) return obj.data;
    if ("available" in obj) return obj.payload;
  }
  return obj;
};

const fmt2 = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(2) : v ?? "-";
};

const safeArray = (x) => (Array.isArray(x) ? x : []);

/** ✅ choose first non-empty array safely */
const pickFirstNonEmptyArray = (...arrs) => {
  for (const a of arrs) {
    if (Array.isArray(a) && a.length > 0) return a;
  }
  return [];
};

const CompanyTabs = ({ symbol }) => {
  const cleanSymbol = useMemo(() => (symbol || "").toUpperCase(), [symbol]);

  const [active, setActive] = useState("dashboard");
  const [tabsMeta, setTabsMeta] = useState(null);
  const [cache, setCache] = useState({});

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // announcements pagination
  const [annLimit] = useState(50);
  const [annOffset, setAnnOffset] = useState(0);

  // ✅ load tabs meta once
  useEffect(() => {
    if (!cleanSymbol) return;

    getCompanyTabs(cleanSymbol)
      .then(setTabsMeta)
      .catch((e) => console.warn("tabs meta failed:", e));
  }, [cleanSymbol]);

  // ✅ load active tab data
  useEffect(() => {
    if (!cleanSymbol) return;

    const loadTab = async () => {
      setError("");

      // cache everything except announcements (pagination)
      if (active !== "announcements" && cache[active]) return;

      setLoading(true);

      try {
        let data = null;

        switch (active) {
          case "dashboard": {
            const quote = await getCompanyQuote(cleanSymbol);
            data = { quote };
            break;
          }

          case "quote":
            data = await getCompanyQuote(cleanSymbol);
            break;

          case "historical": // ✅ ADDED
            data = await getCompanyHistorical(cleanSymbol);
            break;

          case "announcements":
            data = await getAnnouncements(cleanSymbol, annLimit, annOffset);
            break;

          case "corporate_actions":
            data = await getCorporateActions(cleanSymbol);
            break;

          case "annual_reports":
            data = await getAnnualReports(cleanSymbol);
            break;

          case "brsr_reports":
            data = await getBRSRReports(cleanSymbol);
            break;

          case "shareholding_pattern":
            data = await getShareholdingPattern(cleanSymbol);
            break;

          case "financial_results":
            data = await getFinancialResults(cleanSymbol);
            break;

          case "board_meetings":
            data = await getBoardMeetings(cleanSymbol);
            break;

          case "event_calendar":
            data = await getEventCalendar(cleanSymbol);
            break;

          default:
            data = null;
        }

        setCache((prev) => ({ ...prev, [active]: data }));
      } catch (e) {
        setError(e?.message || "Failed to load data");
      } finally {
        setLoading(false);
      }
    };

    loadTab();
  }, [active, cleanSymbol, annOffset]); // keep annOffset so announcements reload

  const activeData = cache[active];
  const counts = tabsMeta?.tabs || {};

  return (
    <div className="mt-10">
      {/* Tabs header */}
      <div className="border-b border-gray-200 flex gap-2 overflow-x-auto whitespace-nowrap">
        {TABS.map((t) => {
          const count = counts?.[t.key]?.count;

          return (
            <button
              key={t.key}
              onClick={() => {
                setActive(t.key);
                if (t.key === "announcements") setAnnOffset(0);
              }}
              className={`shrink-0 px-4 py-2 text-sm font-medium rounded-t-lg ${active === t.key
                ? "bg-white border border-gray-200 border-b-0 text-[#1a2332]"
                : "text-gray-600 hover:text-[#1a2332]"
                }`}
            >
              {t.label}
              {typeof count === "number" && (
                <span className="ml-2 text-xs bg-gray-100 border px-2 py-0.5 rounded-full">
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab body */}
      <div className="border border-gray-200 rounded-b-lg p-4 bg-white">
        {loading && <TabLoader text="Loading company data..." />}

        {!loading && error && (
          <div className="py-6 text-sm text-red-600">{error}</div>
        )}

        {!loading && !error && (
          <TabContent
            tab={active}
            data={activeData}
            tabsMeta={tabsMeta}
            annOffset={annOffset}
            setAnnOffset={setAnnOffset}
            annLimit={annLimit}
            setActive={setActive}
          />
        )}
      </div>
    </div>
  );
};

const TabContent = ({
  tab,
  data,
  tabsMeta,
  annOffset,
  setAnnOffset,
  annLimit,
  setActive,
}) => {
  // allow dashboard with data quote wrapper
  if (!data && tab !== "dashboard") {
    return <div className="py-6 text-sm text-gray-500">No data available.</div>;
  }

  /** ✅ DASHBOARD */
  if (tab === "dashboard") {
    const q = extractQuote(data?.quote);
    const preview = tabsMeta?.tabs?.announcements?.preview || [];
    const shareholding = tabsMeta?.tabs?.shareholding_pattern?.data || {};
    const isUp = Number(quoteValue(q, "change") ?? 0) >= 0;

    return (
      <div className="space-y-6">
        {/* KPIs */}
        <div className="border rounded-lg p-4 flex gap-6 flex-wrap">
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
              {fmt2(quoteValue(q, "change"))} ({fmt2(quoteValue(q, "pChange"))}
              %)
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-500">Prev Close</div>
            <div className="text-lg font-semibold">
              {fmt2(quoteValue(q, "previousClose"))}
            </div>
          </div>
        </div>

        {/* announcements preview */}
        <div className="border rounded-lg p-4">
          <div className="text-sm font-semibold mb-3">Latest Announcements</div>

          {preview.length === 0 ? (
            <div className="text-sm text-gray-500">No announcements.</div>
          ) : (
            <div className="divide-y">
              {preview.slice(0, 5).map((r, i) => {
                const url = extractAnnouncementUrl(r);
                return (
                  <div key={i} className="py-3">
                    <div className="text-sm font-medium">
                      {r.desc || r.title || r.subject || "-"}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {r.an_dt || r.date || "-"}
                    </div>

                    {url && (
                      <a
                        href={url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm text-blue-600 hover:underline"
                      >
                        Open Attachment →
                      </a>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          <button
            className="mt-4 px-4 py-2 border rounded text-sm hover:bg-gray-50"
            onClick={() => {
              setAnnOffset(0);
              setActive("announcements");
            }}
          >
            View All Announcements →
          </button>
        </div>

        {/* shareholding preview */}
        <div className="border rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-900">Shareholding Pattern</h3>
            <button
              className="text-xs text-blue-600 hover:underline font-medium"
              onClick={() => setActive("shareholding_pattern")}
            >
              Details →
            </button>
          </div>
          <ShareholdingDonut data={shareholding} />
        </div>
      </div>
    );
  }

  /** ✅ QUOTE */
  if (tab === "quote") {
    const q = extractQuote(data);
    const isUp = Number(quoteValue(q, "change") ?? 0) >= 0;

    return (
      <div>
        <h3 className="text-sm font-semibold mb-4">Quote</h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4">
            <div className="text-xs text-gray-500">LTP</div>
            <div className="text-xl font-bold">
              {fmt2(quoteValue(q, "lastPrice"))}
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <div className="text-xs text-gray-500">Change</div>
            <div
              className={`text-xl font-bold ${isUp ? "text-green-600" : "text-red-600"
                }`}
            >
              {fmt2(quoteValue(q, "change"))} ({fmt2(quoteValue(q, "pChange"))}
              %)
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <div className="text-xs text-gray-500">Prev Close</div>
            <div className="text-lg font-semibold">
              {fmt2(quoteValue(q, "previousClose"))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  /** ✅ HISTORICAL DATA (NEW TAB) */
  if (tab === "historical") {
    const rows = safeArray(data?.rows);

    if (!rows.length) {
      return (
        <div>
          <h3 className="text-sm font-semibold mb-3">Historical Data</h3>
          <div className="py-6 text-sm text-gray-500">
            No historical data found.
          </div>
        </div>
      );
    }

    const sortedRows = [...rows].sort((a, b) => {
      const da = new Date(a.date || a.price_date || a.DATE || 0).getTime();
      const db = new Date(b.date || b.price_date || b.DATE || 0).getTime();
      return db - da;
    });

    const columns = [
      { key: "date", label: "DATE", render: (r) => r.date || r.price_date || "-" },
      { key: "open", label: "OPEN", render: (r) => fmt2(r.open) },
      { key: "high", label: "HIGH", render: (r) => fmt2(r.high) },
      { key: "low", label: "LOW", render: (r) => fmt2(r.low) },
      { key: "close", label: "CLOSE", render: (r) => fmt2(r.close) },
      {
        key: "volume",
        label: "VOLUME",
        render: (r) => (r.volume !== null && r.volume !== undefined ? r.volume : "-"),
      },
    ];

    return (
      <div>
        <h3 className="text-sm font-semibold mb-4">Historical Data</h3>

        <div className="overflow-auto border rounded-lg">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-[#1a2332]">
              <tr>
                {columns.map((c) => (
                  <th
                    key={c.key}
                    className="px-4 py-3 text-left font-semibold text-white whitespace-nowrap"
                  >
                    {c.label}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-200 bg-white">
              {sortedRows.map((r, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  {columns.map((c) => (
                    <td key={c.key} className="px-4 py-3 whitespace-nowrap">
                      {c.render(r)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  /** ✅ ANNOUNCEMENTS */
  if (tab === "announcements") {
    const rows = safeArray(unwrapNseSection(data));

    return (
      <div>
        <h3 className="text-sm font-semibold mb-3">Announcements</h3>

        {rows.length === 0 ? (
          <div className="py-6 text-sm text-gray-500">No announcements.</div>
        ) : (
          <div className="overflow-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold">Title</th>
                  <th className="px-4 py-2 text-left font-semibold">Date</th>
                  <th className="px-4 py-2 text-left font-semibold">Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {rows.map((r, i) => {
                  const url = extractAnnouncementUrl(r);
                  return (
                    <tr key={i}>
                      <td className="px-4 py-2">
                        {r.desc || r.title || r.subject || "-"}
                      </td>
                      <td className="px-4 py-2">{r.an_dt || r.date || "-"}</td>
                      <td className="px-4 py-2">
                        {url ? (
                          <a
                            href={url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            Open
                          </a>
                        ) : (
                          "-"
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex gap-2 mt-4">
          <button
            className="px-3 py-1 border rounded text-sm disabled:opacity-50"
            onClick={() => setAnnOffset(Math.max(0, annOffset - annLimit))}
            disabled={annOffset === 0}
          >
            Prev
          </button>
          <button
            className="px-3 py-1 border rounded text-sm"
            onClick={() => setAnnOffset(annOffset + annLimit)}
          >
            Next
          </button>
        </div>
      </div>
    );
  }

  /** ✅ CORPORATE ACTIONS */
  if (tab === "corporate_actions") {
    const rows = safeArray(unwrapNseSection(data));
    return (
      <CompanyTable
        title="Corporate Actions"
        rows={rows}
        columns={[
          { key: "exDate", label: "Ex Date" },
          { key: "purpose", label: "Purpose" },
          { key: "desc", label: "Description" },
          { key: "recordDate", label: "Record Date" },
          { key: "bcStartDate", label: "BC Start" },
          { key: "bcEndDate", label: "BC End" },
        ]}
      />
    );
  }

  /** ✅ ANNUAL REPORTS */
  if (tab === "annual_reports") {
    const rows = safeArray(unwrapNseSection(data));
    return (
      <CompanyTable
        title="Annual Reports"
        rows={rows}
        columns={[
          { key: "m_yr", label: "Year" },
          { key: "desc", label: "Description" },
          {
            key: "url",
            label: "Link",
            render: (r) => (
              <a
                href={extractAnnouncementUrl(r)}
                target="_blank"
                rel="noreferrer"
                className="text-blue-600 hover:underline"
              >
                View PDF
              </a>
            ),
          },
        ]}
      />
    );
  }

  /** ✅ BRSR REPORTS */
  if (tab === "brsr_reports") {
    const rows = safeArray(unwrapNseSection(data));
    return (
      <CompanyTable
        title="BRSR Reports"
        rows={rows}
        columns={[
          { key: "m_yr", label: "Year" },
          { key: "desc", label: "Description" },
          {
            key: "url",
            label: "Link",
            render: (r) => (
              <a
                href={extractAnnouncementUrl(r)}
                target="_blank"
                rel="noreferrer"
                className="text-blue-600 hover:underline"
              >
                View PDF
              </a>
            ),
          },
        ]}
      />
    );
  }

  /** ✅ BOARD MEETINGS */
  if (tab === "board_meetings") {
    const rows = safeArray(unwrapNseSection(data));
    return (
      <CompanyTable
        title="Board Meetings"
        rows={rows}
        columns={[
          { key: "meetingDate", label: "Meeting Date" },
          { key: "purpose", label: "Purpose" },
          { key: "desc", label: "Description" },
          {
            key: "url",
            label: "Details",
            render: (r) =>
              r.url ? (
                <a
                  href={r.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  Link
                </a>
              ) : (
                "-"
              ),
          },
        ]}
      />
    );
  }

  /** ✅ FINANCIAL RESULTS */
  if (tab === "financial_results") {
    const financials = data?.data || data || {};
    const rows = safeArray(financials?.payload);

    if (isUnavailableSection(data) || isUnavailableSection(data?.data)) {
      return (
        <div className="py-12 text-center bg-white border rounded-xl shadow-sm mt-4">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="text-sm font-medium text-gray-900">Financial Results Not Available</div>
          <p className="text-xs text-gray-500 mt-1">NSE has not yet published financial results for this security.</p>
        </div>
      );
    }

    if (!rows.length && !Object.keys(financials).length) {
      return <div className="py-6 text-sm text-gray-500">No financial results available.</div>;
    }

    return (
      <div className="mt-4">
        <h3 className="text-sm font-semibold mb-3">Financial Results</h3>
        {rows.length > 0 ? (
          <CompanyTable
            rows={rows}
            columns={[
              { key: "from_dt", label: "From" },
              { key: "to_dt", label: "To" },
              { key: "desc", label: "Description" },
              {
                key: "url",
                label: "Link",
                render: (r) => (
                  <a
                    href={extractAnnouncementUrl(r)}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    PDF
                  </a>
                ),
              },
            ]}
          />
        ) : (
          <div className="py-8 text-center text-gray-500 text-sm italic">
            No specific financial records found.
          </div>
        )}
      </div>
    );
  }

  /** ✅ SHAREHOLDING PATTERN */
  if (tab === "shareholding_pattern") {
    const sh = data?.data || data || {};

    if (isUnavailableSection(data) || isUnavailableSection(data?.data)) {
      return (
        <div className="py-12 text-center bg-white border rounded-xl shadow-sm mt-4">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div className="text-sm font-medium text-gray-900">Shareholding Pattern Not Available</div>
          <p className="text-xs text-gray-500 mt-1">NSE has not yet published the shareholding pattern for this security.</p>
          {sh.source_url && (
            <a href={sh.source_url} target="_blank" rel="noreferrer" className="text-xs text-blue-600 hover:underline mt-4 inline-block">
              Check NSE Source (JSON) →
            </a>
          )}
        </div>
      );
    }



    // Mock data for demonstration if no data is found
    // Promoter & Promoter Group (Blue: #3b82f6), Public (Green: #10b981), Employee Trusts (Amber: #f59e0b)
    const mockData = {
      promoter: 74.50,
      public: 24.10,
      employee_trusts: 1.40
    };

    const hasData = sh.promoter || sh.public || sh.employee_trusts;
    const chartData = hasData ? sh : mockData;

    return (
      <div className="mt-4 bg-white border border-gray-100 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-tight">Shareholding Patterns (in %)</h3>
          {!hasData && (
            <span className="px-2 py-0.5 bg-amber-50 text-amber-600 text-[10px] font-bold rounded border border-amber-100">
              MOCK DATA (Pending Sync)
            </span>
          )}
        </div>

        <ShareholdingDonut data={sh} />

        <div className="mt-6 pt-4 border-t border-gray-50 flex items-center justify-between">
          <div className="text-[10px] text-gray-400 font-medium italic">
            * Data source: NSE / XBRL {sh.source_url ? '(Live)' : '(Awaiting Sync)'}
          </div>
          {sh.source_url && (
            <a href={sh.source_url} target="_blank" rel="noreferrer" className="text-[10px] text-blue-500 hover:underline">
              View NSE Source →
            </a>
          )}
        </div>
      </div>
    );
  }

  /** ✅ EVENT CALENDAR */
  if (tab === "event_calendar") {
    const rows = safeArray(unwrapNseSection(data));

    if (isUnavailableSection(data)) {
      return (
        <div className="py-12 text-center bg-white border rounded-xl shadow-sm mt-4">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div className="text-sm font-medium text-gray-900">Event Calendar Not Available</div>
          <p className="text-xs text-gray-500 mt-1">No upcoming events found on NSE for this security.</p>
        </div>
      );
    }

    return (
      <div className="mt-4">
        <CompanyTable
          title="Event Calendar"
          rows={rows}
          columns={[
            { key: "date", label: "Date" },
            { key: "purpose", label: "Purpose" },
            { key: "desc", label: "Description" },
          ]}
        />
      </div>
    );
  }

  // fallback
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold capitalize">{tab.replace("_", " ")}</h3>
      <pre className="text-xs bg-gray-50 p-4 rounded overflow-auto max-h-96">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default CompanyTabs;
