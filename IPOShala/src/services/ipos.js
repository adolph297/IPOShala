import { apiGet } from "./http";

export const getClosedIPOs = async (type = null) => {
  const url = type ? `/api/ipos/closed?type=${type}` : `/api/ipos/closed`;
  return await apiGet(url);
};

export const getIPODetails = async (symbol) => {
  return await apiGet(`/api/ipos/${symbol}`);
};

export const getLiveIPOs = async () => {
  return await apiGet(`/api/ipos/live`);
};

export const getUpcomingIPOs = async () => {
  return await apiGet(`/api/ipos/upcoming`);
};

export const getIPOStats = async () => {
  return await apiGet(`/api/ipos/stats`);
};

export const getGMPData = async () => {
  return await apiGet(`/api/gmp/`);
};
