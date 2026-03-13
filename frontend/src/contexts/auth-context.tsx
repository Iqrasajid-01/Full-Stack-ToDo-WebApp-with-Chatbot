'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { User } from '@/types';
import { authService } from '@/lib/auth/service';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  signIn: (credentials: { email: string; password: string }) => Promise<boolean>;
  signUp: (userData: { email: string; password: string; name: string }) => Promise<boolean>;
  signOut: () => Promise<void>;
  updateUser: (userData: Partial<User>) => void;
  refreshSession: () => Promise<{ success: boolean; user: User | null }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshSession = useCallback(async (): Promise<{ success: boolean; user: User | null }> => {
    try {
      const response = await authService.getCurrentUser();
      if (response.success && response.user) {
        setUser(response.user);
        return { success: true, user: response.user };
      }
      setUser(null);
      return { success: false, user: null };
    } catch (error) {
      console.error('Error refreshing session:', error);
      setUser(null);
      return { success: false, user: null };
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    let isMounted = true;
    
    // Fast path: Check if token exists in localStorage first
    const token = localStorage.getItem('auth-token');
    if (token) {
      // Token exists, assume authenticated initially for fast UI
      // Then verify in background
      authService.getCurrentUser()
        .then(response => {
          if (isMounted && response.success && response.user) {
            setUser(response.user);
          } else if (isMounted && !response.success) {
            // Token invalid, clear it
            localStorage.removeItem('auth-token');
            setUser(null);
          }
        })
        .catch(() => {
          if (isMounted) {
            localStorage.removeItem('auth-token');
            setUser(null);
          }
        })
        .finally(() => {
          if (isMounted) {
            setLoading(false);
          }
        });
    } else {
      // No token, not authenticated
      if (isMounted) {
        setLoading(false);
      }
    }
    
    return () => { isMounted = false; };
  }, []);

  const signIn = useCallback(async (credentials: { email: string; password: string }): Promise<boolean> => {
    try {
      const response = await authService.signin(credentials);
      if (response.success && response.user) {
        setUser(response.user);
        return true;
      }
      if (response.error) {
        localStorage.setItem('auth-error', response.error);
      }
      return false;
    } catch (error: any) {
      localStorage.setItem('auth-error', error.message || 'Sign in failed');
      return false;
    }
  }, []);

  const signUp = useCallback(async (userData: { email: string; password: string; name: string }): Promise<boolean> => {
    try {
      const response = await authService.signup(userData);
      if (response.success && response.user) {
        setUser(response.user);
        return true;
      }
      if (response.error) {
        localStorage.setItem('auth-error', response.error);
      }
      return false;
    } catch (error: any) {
      localStorage.setItem('auth-error', error.message || 'Sign up failed');
      return false;
    }
  }, []);

  const signOut = useCallback(async () => {
    await authService.signout();
    setUser(null);
  }, []);

  const updateUser = useCallback((userData: Partial<User>) => {
    setUser(prevUser => prevUser ? { ...prevUser, ...userData } : null);
  }, []);

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    signIn,
    signUp,
    signOut,
    updateUser,
    refreshSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};