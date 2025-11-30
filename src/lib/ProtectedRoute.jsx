import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated, getUserRole } from './auth';

export const ProtectedRoute = ({ children, requiredRole = null }) => {
  const authenticated = isAuthenticated();
  const userRole = getUserRole();

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && userRole !== requiredRole) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export const PublicRoute = ({ children, redirectIfAuth = false }) => {
  const authenticated = isAuthenticated();

  if (authenticated && redirectIfAuth) {
    return <Navigate to="/" replace />;
  }

  return children;
};
