import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getIPODetails } from "../services/ipos";
import CompanyTabs from "@/components/company/CompanyTabs";
import PageHeader from "@/components/common/PageHeader";
import { Link } from "react-router-dom";
import NseOverviewCards from "@/components/company/NseOverviewCards";

const IPODetails = () => {
  const { symbol } = useParams();
  const [ipo, setIpo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ✅ Track clicked buttons
  const [clickedDocs, setClickedDocs] = useState({});
  const [isFinancialModalOpen, setIsFinancialModalOpen] = useState(false);

  const markClicked = (key) => {
    setClickedDocs((prev) => ({
      ...prev,
      [key]: true,
    }));
  };

  const API_BASE = (import.meta?.env?.VITE_API_BASE || "http://localhost:8000").replace(/\/$/, "");

  const docButtons = [
    { doc_type: "ratios", label: "Ratios / Basis Issue Price (PDF)" },
    { doc_type: "rhp", label: "Red Herring Prospectus (RHP)" },
    { doc_type: "bidding_centers", label: "Bidding Centers (PDF)" },
    { doc_type: "forms", label: "Sample Application Forms (PDF)" },
    { doc_type: "security_pre", label: "Security Parameters (Pre-Anchor)" },
    { doc_type: "security_post", label: "Security Parameters (Post-Anchor)" },
  ];

  useEffect(() => {
    setLoading(true);
    setError("");

    getIPODetails(symbol)
      .then((data) => {
        setIpo(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "IPO not found");
        setLoading(false);
      });
  }, [symbol]);

  if (loading) return <div className="p-6">Loading IPO details...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  const sym = (ipo?.symbol || symbol || "").toUpperCase().trim();

  // Helper for dynamic button styling
  const getBtnClass = (key, baseBg = "bg-gray-50") =>
    `px-3 py-1.5 rounded-md border text-sm font-medium transition-all duration-200 ${clickedDocs[key]
      ? "bg-[#1e2a3a] text-white border-[#1e2a3a] shadow-sm"
      : `border-gray-300 ${baseBg} hover:bg-[#1e2a3a] hover:text-white hover:border-[#1e2a3a] text-[#1e2a3a]`
    }`;

  // Helper for NSE attachment links
  const extractAnnouncementUrl = (r) =>
    r?.attchmntFile || r?.url || r?.link || r?.attachment || r?.pdf || null;


  return (
    <>
      <div className="bg-gray-50 border-b border-gray-200 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex justify-between items-center relative">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-[#1a2332]">
              {ipo.company_name}
            </h1>

            <div className="mt-2 text-base text-gray-600">
              Symbol: {ipo.symbol || symbol}
            </div>
          </div>

          {/* Logo Section */}
          <div className="flex-shrink-0 ml-8 hidden sm:block">
            {ipo.logo_url ? (
              <div className="w-36 h-36 bg-white rounded-2xl shadow-md border border-gray-200 p-4 flex items-center justify-center overflow-hidden">
                <img
                  src={ipo.logo_url}
                  alt={`${ipo.company_name} Logo`}
                  className="max-w-full max-h-full object-contain"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.style.display = 'none';
                    e.target.parentNode.innerHTML = `<div class="text-[#1a2332] font-bold text-5xl">${ipo.company_name.charAt(0)}</div>`;
                  }}
                />
              </div>
            ) : (
              <div className="w-36 h-36 bg-white rounded-2xl shadow-md border border-gray-200 flex items-center justify-center">
                <div className="text-[#1a2332] font-bold text-5xl">
                  {ipo.company_name.charAt(0)}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-6">
          <Link to="/closed-ipos" className="text-blue-600 hover:underline text-sm">
            ← Back to Closed IPOs
          </Link>
        </div>

        {ipo?.description && (
          <div className="mb-10 bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6 uppercase tracking-widest">
              About the Company
            </h3>
            <div className="text-sm text-gray-700 leading-relaxed">
              {ipo.description}
            </div>
          </div>
        )}

        {/* ================= APPLICATION GUIDES ================= */}
        {(ipo.issue_information?.asba_circular_pdf ||
          ipo.issue_information?.upi_asba_video ||
          ipo.issue_information?.bhim_upi_registration_video) && (
            <div className="mb-8 bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6 flex items-center gap-2">
                <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Application Guides & Tutorials
              </h3>
              <div className="flex flex-wrap gap-3">
                {ipo.issue_information?.asba_circular_pdf && (
                  <a
                    href={ipo.issue_information.asba_circular_pdf}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => markClicked("asba_circular_pdf")}
                    className={getBtnClass("asba_circular_pdf")}
                  >
                    ASBA Circular (PDF)
                  </a>
                )}
                {ipo.issue_information?.upi_asba_video && (
                  <a
                    href={ipo.issue_information.upi_asba_video}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => markClicked("upi_asba_video")}
                    className={getBtnClass("upi_asba_video")}
                  >
                    Watch: UPI ASBA Video
                  </a>
                )}
                {ipo.issue_information?.bhim_upi_registration_video && (
                  <a
                    href={ipo.issue_information.bhim_upi_registration_video}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => markClicked("bhim_upi_registration_video")}
                    className={getBtnClass("bhim_upi_registration_video")}
                  >
                    Watch: BHIM UPI Video
                  </a>
                )}
              </div>
            </div>
          )}

        {/* ================= PROSPECTUS & RATIOS ================= */}
        {/* ================= PROSPECTUS & RATIOS ================= */}
        {ipo?.documents && (ipo.documents.rhp || ipo.documents.ratios) && (
          <div className="mb-8 bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6 flex items-center gap-2">
              <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Official Prospectus & Ratios
            </h3>
            <div className="flex flex-wrap gap-3">
              {ipo.documents?.rhp && (
                <a
                  href={`${API_BASE}/api/docs/${sym}/rhp`}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => markClicked("doc_rhp")}
                  className={getBtnClass("doc_rhp", "bg-white")}
                >
                  Red Herring Prospectus (RHP)
                </a>
              )}
              {ipo.documents?.ratios && (
                <a
                  href={`${API_BASE}/api/docs/${sym}/ratios`}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => markClicked("doc_ratios")}
                  className={getBtnClass("doc_ratios", "bg-white")}
                >
                  Ratios / Basis Issue Price
                </a>
              )}
            </div>
          </div>
        )}

        {/* ================= ANCHOR ALLOCATION ================= */}
        {ipo.issue_information?.anchor_allocation_zip && (
          <div className="mb-8 bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6 flex items-center gap-2">
              <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Anchor Allocation
            </h3>
            <div className="flex flex-wrap gap-3">
              <a
                href={ipo.issue_information.anchor_allocation_zip}
                target="_blank"
                rel="noreferrer"
                onClick={() => markClicked("anchor_allocation_zip")}
                className={getBtnClass("anchor_allocation_zip")}
              >
                Download Anchor Allocation (ZIP)
              </a>
            </div>
          </div>
        )}

        {/* ================= SUPPLEMENTARY DOCUMENTS ================= */}
        {(ipo.documents?.bidding_centers ||
          ipo.documents?.forms ||
          ipo.documents?.security_pre ||
          ipo.documents?.security_post ||
          (ipo.nse_company?.financial_results?.data || ipo.nse_company?.financial_results?.payload || []).length > 0 ||
          (ipo.nse_company?.annual_reports?.data || ipo.nse_company?.annual_reports?.payload || []).length > 0 ||
          (ipo.nse_company?.audited_financials || []).length > 0) && (
            <div className="mb-10 bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6 flex items-center gap-2">
                <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Supplementary Documents & Centers
              </h3>
              <div className="flex flex-wrap gap-3">
                {ipo.documents?.bidding_centers && (
                  <a
                    href={`${API_BASE}/api/docs/${sym}/bidding_centers`}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => markClicked("doc_bidding_centers")}
                    className={getBtnClass("doc_bidding_centers", "bg-white")}
                  >
                    Bidding Centers (PDF)
                  </a>
                )}
                {ipo.documents?.forms && (
                  <a
                    href={`${API_BASE}/api/docs/${sym}/forms`}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => markClicked("doc_forms")}
                    className={getBtnClass("doc_forms", "bg-white")}
                  >
                    Sample Application Forms
                  </a>
                )}
                {ipo.documents?.security_pre && (
                  <a
                    href={`${API_BASE}/api/docs/${sym}/security_pre`}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => markClicked("doc_security_pre")}
                    className={getBtnClass("doc_security_pre", "bg-white")}
                  >
                    Security Parameters (Pre)
                  </a>
                )}
                {ipo.documents?.security_post && (
                  <a
                    href={`${API_BASE}/api/docs/${sym}/security_post`}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => markClicked("doc_security_post")}
                    className={getBtnClass("doc_security_post", "bg-white")}
                  >
                    Security Parameters (Post)
                  </a>
                )}

                {/* ✅ Consolidated Financial Results Button & Modal */}
                {(() => {
                  const nse = ipo?.nse_company || {};

                  // Helper to unwrap [ {data: []} ] or [ {payload: []} ]
                  const unwrap = (obj) => {
                    if (!obj) return [];
                    if (Array.isArray(obj)) return obj;
                    // Support selenium wrapper { __available__, data } or { available, payload }
                    const items = obj.data || obj.payload || [];
                    return Array.isArray(items) ? items : [];
                  };

                  const financialResults = unwrap(nse.financial_results);
                  const annualReports = unwrap(nse.annual_reports);
                  const auditedIngested = Array.isArray(nse.audited_financials) ? nse.audited_financials : [];

                  console.log("DEBUG Financials:", {
                    symbol: sym,
                    has_nse: !!ipo?.nse_company,
                    fr_len: financialResults.length,
                    ar_len: annualReports.length,
                    af_len: auditedIngested.length,
                    raw_fr: nse.financial_results
                  });
                  const allFinancials = [...annualReports, ...financialResults];

                  // Add audited papers if not already covered by year
                  auditedIngested.forEach((aud) => {
                    if (!aud?.year) return;
                    const exists = allFinancials.some(f =>
                      (f.year?.toString().includes(aud.year)) ||
                      (f.m_yr?.toString().includes(aud.year)) ||
                      (f.desc?.includes(aud.year))
                    );
                    if (!exists) {
                      allFinancials.push({
                        ...aud,
                        is_audited: true,
                        label: aud.label || `Audited FY ${aud.year}`,
                        year: aud.year
                      });
                    }
                  });

                  // Sort desc by year/date roughly
                  allFinancials.sort((a, b) => {
                    const dateA = (a.year || a.m_yr || a.to_dt || "").toString();
                    const dateB = (b.year || b.m_yr || b.to_dt || "").toString();
                    return dateB.localeCompare(dateA);
                  });

                  if (allFinancials.length === 0) {
                    return (
                      <div className="px-3 py-1.5 rounded-md border border-gray-200 bg-gray-50 text-sm font-medium text-gray-400 cursor-not-allowed">
                        Financial Results: Not Available Yet
                      </div>
                    );
                  }

                  return (
                    <>
                      <button
                        onClick={() => setIsFinancialModalOpen(true)}
                        className={getBtnClass("financial_results", "bg-white")}
                      >
                        Financial Results ({allFinancials.length})
                      </button>

                      {isFinancialModalOpen && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                          <div
                            className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[80vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                              <div>
                                <h3 className="font-semibold text-gray-900">Financial Results</h3>
                                <p className="text-xs text-gray-500 mt-0.5">Audited & Quarterly Reports</p>
                              </div>
                              <button
                                onClick={() => setIsFinancialModalOpen(false)}
                                className="p-1.5 hover:bg-gray-200 rounded-full transition-colors text-gray-500 hover:text-gray-700"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                              </button>
                            </div>

                            <div className="p-4 overflow-y-auto space-y-2.5">
                              {allFinancials.map((f, i) => {
                                const url = extractAnnouncementUrl(f);
                                if (!url) return null;
                                const key = `fin_res_${i}`;
                                const label = f.label || (f.to_dt ? `Financial Results (${f.to_dt})` : "Financial Results (PDF)");

                                return (
                                  <a
                                    key={key}
                                    href={url}
                                    target="_blank"
                                    rel="noreferrer"
                                    onClick={() => markClicked(key)}
                                    className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all group"
                                  >
                                    <div className="p-2 bg-red-50 text-red-500 rounded-md group-hover:bg-red-100 transition-colors">
                                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm font-medium text-gray-900 truncate group-hover:text-blue-700">{label}</p>
                                      <p className="text-xs text-gray-500 mt-0.5">PDF Document</p>
                                    </div>
                                    <svg className="w-4 h-4 text-gray-400 group-hover:text-blue-500 opacity-0 group-hover:opacity-100 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                                  </a>
                                );
                              })}
                            </div>

                            <div className="p-4 border-t border-gray-100 bg-gray-50 text-center">
                              <button
                                onClick={() => setIsFinancialModalOpen(false)}
                                className="text-sm font-medium text-gray-600 hover:text-gray-900"
                              >
                                Close
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            </div>
          )}

        {/* ================= IPO DETAILS CARD ================= */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6">
            IPO Details
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <p><strong>Symbol:</strong> {ipo.symbol}</p>
            <p><strong>Security Type:</strong> {ipo.security_type}</p>

            <p>
              <strong>Issue Dates:</strong>{" "}
              {ipo.issue_start_date || "-"} → {ipo.issue_end_date || "-"}
            </p>

            <p>
              <strong>Listing Date:</strong>{" "}
              {ipo.listing_date || "-"}
            </p>

            <p>
              <strong>Price:</strong>{" "}
              {ipo.issue_price && ipo.issue_price !== "-"
                ? ipo.issue_price
                : ipo.price_range || "-"}
            </p>
          </div>
        </div>

        <NseOverviewCards symbol={ipo.symbol || symbol} ipo={ipo} />

        <CompanyTabs symbol={ipo.symbol || symbol} />
      </div>
    </>
  );
};

export default IPODetails;
