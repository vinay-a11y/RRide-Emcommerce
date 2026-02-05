import { api } from '../context/AuthContext';

// ✅ Export api - axios interceptor ALREADY handles token in AuthContext
export { api };

/**
 * Safe GET request - token is added by axios interceptor
 */
export const apiGet = (url) => {
  console.log("[v0] GET request:", url);
  return api.get(url);
};

/**
 * Safe POST request - token is added by axios interceptor
 */
export const apiPost = (url, data) => {
  console.log("[v0] POST request:", url, "data:", data);
  return api.post(url, data);
};

/**
 * Safe PUT request - token is added by axios interceptor
 */
export const apiPut = (url, data) => {
  console.log("[v0] PUT request:", url, "data:", data);
  return api.put(url, data);
};

/**
 * Safe DELETE request - token is added by axios interceptor
 */
export const apiDelete = (url) => {
  console.log("[v0] DELETE request:", url);
  return api.delete(url);
};

export default api;
