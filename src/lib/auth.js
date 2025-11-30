/**
 * Authentication utilities for frontend
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

/**
 * Get access token from storage
 */
export const getAccessToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Get refresh token from storage
 */
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Set tokens in storage
 */
export const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
};

/**
 * Remove tokens from storage
 */
export const removeTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!getAccessToken();
};

/**
 * Register user
 */
export const register = async (email, password, role = 'user', additionalData = {}) => {
  const payload = { 
    email, 
    password, 
    role,
    ...additionalData 
  };

  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Registration failed');
  }

  if (data.data?.access_token) {
    setTokens(data.data.access_token, data.data.refresh_token);
  }

  return data;
};

/**
 * Login user
 */
export const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Login failed');
  }

  if (data.data?.access_token) {
    setTokens(data.data.access_token, data.data.refresh_token);
  }

  return data;
};

/**
 * Logout user
 */
export const logout = async () => {
  const token = getAccessToken();
  if (token) {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  removeTokens();
};

/**
 * Get current user
 */
export const getCurrentUser = async () => {
  const token = getAccessToken();
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        removeTokens();
        return null;
      }
      throw new Error('Failed to get user');
    }

    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('Get user error:', error);
    return null;
  }
};

/**
 * Get user role from token (decoded from JWT)
 */
export const getUserRole = () => {
  const token = getAccessToken();
  if (!token) {
    return null;
  }

  try {
    // Decode JWT token (middle part between dots)
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode the payload (add padding if needed)
    const payload = parts[1];
    const padded = payload + '='.repeat(4 - (payload.length % 4));
    const decoded = JSON.parse(atob(padded));
    return decoded.role || null;
  } catch (error) {
    console.error('Failed to decode user role:', error);
    return null;
  }
};

/**
 * Get authorization headers for API requests
 */
export const getAuthHeader = () => {
  const token = getAccessToken();
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

/**
 * Refresh access token
 */
export const refreshAccessToken = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`,
      },
    });

    if (!response.ok) {
      removeTokens();
      return null;
    }

    const data = await response.json();
    if (data.data?.access_token) {
      setTokens(data.data.access_token, refreshToken);
      return data.data.access_token;
    }

    return null;
  } catch (error) {
    console.error('Refresh token error:', error);
    removeTokens();
    return null;
  }
};

/**
 * Make authenticated API request
 */
export const authenticatedFetch = async (url, options = {}) => {
  const token = getAccessToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  // If token expired, try to refresh
  if (response.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      // Retry request with new token
      return fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${newToken}`,
          ...options.headers,
        },
      });
    } else {
      removeTokens();
      throw new Error('Authentication failed');
    }
  }

  return response;
};



