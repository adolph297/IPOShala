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


  return (
    <>
      <div className="bg-gray-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-[#1a2332]">
            {ipo.company_name}
          </h1>

          <div className="mt-2 text-base text-gray-600">
            Symbol: {ipo.symbol || symbol}
          </div>

          {ipo?.description && (
            <div className="mt-4 text-sm text-gray-600 max-w-4xl leading-relaxed">
              {ipo.description}
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-6">
          <Link to="/closed-ipos" className="text-blue-600 hover:underline text-sm">
            ← Back to Closed IPOs
          </Link>
        </div>

        {/* ================= DOCUMENT BUTTONS ================= */}
        <div className="mt-4 mb-6 flex flex-wrap gap-2">

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
              UPI ASBA Video
            </a>
          )}

          {ipo.issue_information?.anchor_allocation_zip && (
            <a
              href={ipo.issue_information.anchor_allocation_zip}
              target="_blank"
              rel="noreferrer"
              onClick={() => markClicked("anchor_allocation_zip")}
              className={getBtnClass("anchor_allocation_zip")}
            >
              Anchor Allocation (ZIP)
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
              BHIM UPI Registration Video
            </a>
          )}

          {/* Standardized document buttons */}
          {docButtons.map((d) => {
            const hasDoc = ipo.documents?.[d.doc_type];
            if (!hasDoc) return null;

            return (
              <a
                key={d.doc_type}
                href={`${API_BASE}/api/docs/${sym}/${d.doc_type}`}
                target="_blank"
                rel="noreferrer"
                onClick={() => markClicked(`doc_${d.doc_type}`)}
                className={getBtnClass(`doc_${d.doc_type}`, "bg-white")}
                title={`Open ${d.label}`}
              >
                {d.label}
              </a>
            );
          })}
        </div>

        {/* ================= IPO DETAILS CARD ================= */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-[#1a2332] mb-4">
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
