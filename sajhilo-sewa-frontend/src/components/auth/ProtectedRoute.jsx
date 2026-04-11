import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { getToken, isTokenExpired } from '../../utils/auth';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const token = getToken();
  const location = useLocation();
  const isAdmin = localStorage.getItem('isAdminAuthenticated') === 'true';

  // Check if authenticated
  if (!token || isTokenExpired(token)) {
    // Clear potentially expired tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('isAdminAuthenticated');

    // Redirect to login, but save the current location to redirect back after login
    return <Navigate to="/login" state={{ from: location, error: 'user not logged in' }} replace />;
  }

  // Check admin rights if required
  if (adminOnly && !isAdmin) {
    return <Navigate to="/" state={{ error: 'access_denied' }} replace />;
  }

  return children;
};

export default ProtectedRoute;
