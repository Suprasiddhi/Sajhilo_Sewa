import { getToken, logout, isTokenExpired } from '../utils/auth';

const BASE_URL = 'http://localhost:8000';

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
