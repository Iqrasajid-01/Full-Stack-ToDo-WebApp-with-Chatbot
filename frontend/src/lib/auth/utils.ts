// Authentication utilities

export interface User {
  id: string;
  email: string;
  name: string | null;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date | null;
  isActive: boolean;
}

export interface AuthTokenPayload {
  id: string;
  email: string;
  name?: string | null;
  emailVerified?: boolean;
  exp: number;
  iat: number;
}

/**
 * Checks if the user is authenticated by verifying the existence and validity of the JWT token
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') {
    return false; // Server-side, can't check auth
  }

  const token = localStorage.getItem('authToken');
  if (!token) {
    return false;
  }

  try {
    // Decode the JWT payload (second part after the dot)
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      return false; // Invalid token format
    }

    const payload = JSON.parse(atob(tokenParts[1])) as AuthTokenPayload;
    const currentTime = Math.floor(Date.now() / 1000);

    // Check if token has expired
    return payload.exp > currentTime;
  } catch (error) {
    console.error('Error decoding token:', error);
    return false;
  }
}

/**
 * Gets the current user from the JWT token
 */
export function getCurrentUser(): User | null {
  if (typeof window === 'undefined') {
    return null; // Server-side, can't get user
  }

  const token = localStorage.getItem('authToken');
  if (!token) {
    return null;
  }

  try {
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      return null; // Invalid token format
    }

    const payload = JSON.parse(atob(tokenParts[1])) as AuthTokenPayload;

    // Check if token has expired
    const currentTime = Math.floor(Date.now() / 1000);
    if (payload.exp <= currentTime) {
      return null;
    }

    return {
      id: payload.id,
      email: payload.email,
      name: payload.name || payload.email.split('@')[0] || null,
      emailVerified: payload.emailVerified || false,
      createdAt: new Date(payload.iat * 1000),
      updatedAt: null,
      isActive: true,
    };
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

/**
 * Clears the authentication token and any related user data
 */
export function clearAuth(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('authToken');
    // Remove any other user-related data
    localStorage.removeItem('user');
  }
}

/**
 * Stores the authentication token
 */
export function storeToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('authToken', token);
  }
}

/**
 * Gets the authentication token
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('authToken');
  }
  return null;
}