import { apiGet } from "./http";

export const getClosedIPOs = async () => {
  return await apiGet(`/api/ipos/closed`);
};

export const getIPODetails = async (symbol) => {
  return await apiGet(`/api/ipos/${symbol}`);
};
