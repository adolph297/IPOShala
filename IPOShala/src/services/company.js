import { apiGet } from "./http";
import { API_BASE } from "../config/api";

export const getCompany = (symbol) => apiGet(`/api/company/${symbol}`);
export const getCompanyQuote = (symbol) => apiGet(`/api/company/${symbol}/quote`);

export const getCompanyTabs = (symbol) => apiGet(`/api/company/${symbol}/tabs`);

export const getAnnouncements = (symbol, limit = 50, offset = 0) =>
  apiGet(`/api/company/${symbol}/announcements?limit=${limit}&offset=${offset}`);

export const getCorporateActions = (symbol, limit = 50, offset = 0) =>
  apiGet(`/api/company/${symbol}/corporate-actions?limit=${limit}&offset=${offset}`);

export const getAnnualReports = (symbol, limit = 50, offset = 0) =>
  apiGet(`/api/company/${symbol}/annual-reports?limit=${limit}&offset=${offset}`);

export const getBRSRReports = (symbol, limit = 50, offset = 0) =>
  apiGet(`/api/company/${symbol}/brsr-reports?limit=${limit}&offset=${offset}`);

export const getBoardMeetings = (symbol, limit = 50, offset = 0) =>
  apiGet(`/api/company/${symbol}/board-meetings?limit=${limit}&offset=${offset}`);

export const getEventCalendar = (symbol, limit = 100, offset = 0) =>
  apiGet(`/api/company/${symbol}/event-calendar?limit=${limit}&offset=${offset}`);

export const getShareholdingPattern = (symbol) =>
  apiGet(`/api/company/${symbol}/shareholding-pattern`);

export const getFinancialResults = (symbol) =>
  apiGet(`/api/company/${symbol}/financial-results`);

export async function getCompanyHistorical(symbol) {
  const res = await fetch(`${API_BASE}/api/company/${symbol}/historical`);
  if (!res.ok) throw new Error("Failed to load historical data");
  return res.json();
}
