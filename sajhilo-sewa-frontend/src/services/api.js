import { getToken, logout, isTokenExpired } from '../utils/auth';

// 1. This is your API Link (Base URL)
// All requests from the frontend go to this address.
// Since you are running locally, it points to 'http://localhost:8000'
const BASE_URL = 'http://localhost:8000';

// 2. The main handler for API communication
// It attaches your security token and ensures you're logged in before sending.
export const apiRequest = async (endpoint, options = {}) => {
  const token = getToken();
  
  if (token && isTokenExpired(token)) {
    logout();
    return null;
  }

  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    logout();
    return null;
  }

  return response;
};
