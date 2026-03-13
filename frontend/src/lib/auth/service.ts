import { User } from '@/types';
import { authApiService } from './api-service';

export const authService = {
  /**
   * Sign up a new user
   */
  async signup(userData: { email: string; password: string; name: string }): Promise<{ success: boolean; user?: User; error?: string }> {
    if (typeof window === 'undefined') {
      // Server-side, return error
      return { success: false, error: 'Authentication can only be performed on the client' };
    }

    try {
      const response = await authApiService.signUp(userData);

      // Store the token in localStorage
      localStorage.setItem('auth-token', response.token);

      return {
        success: true,
        user: {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          emailVerified: response.user.emailVerified,
          createdAt: new Date(response.user.createdAt),
          updatedAt: response.user.updatedAt ? new Date(response.user.updatedAt) : null,
          isActive: true, // Assuming newly created/signed in users are active
        }
      };
    } catch (error: any) {
      console.error('Sign up error:', error);
      
      // Provide more specific error messages
      if (error.message.includes('Email already registered')) {
        return { success: false, error: 'Email is already registered' };
      }
      
      return { success: false, error: error.message || 'Sign up failed' };
    }
  },

  /**
   * Sign in a user
   */
  async signin(credentials: { email: string; password: string }): Promise<{ success: boolean; user?: User; error?: string }> {
    if (typeof window === 'undefined') {
      // Server-side, return error
      return { success: false, error: 'Authentication can only be performed on the client' };
    }

    try {
      const response = await authApiService.signIn(credentials);

      // Store the token in localStorage
      localStorage.setItem('auth-token', response.token);

      return {
        success: true,
        user: {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          emailVerified: response.user.emailVerified,
          createdAt: new Date(response.user.createdAt),
          updatedAt: response.user.updatedAt ? new Date(response.user.updatedAt) : null,
          isActive: true, // Assuming newly created/signed in users are active
        }
      };
    } catch (error: any) {
      console.error('Sign in error:', error);
      
      // Provide more specific error messages
      if (error.message.includes('Incorrect email or password')) {
        return { success: false, error: 'Incorrect email or password' };
      }
      
      return { success: false, error: error.message || 'Sign in failed' };
    }
  },

  /**
   * Sign out the current user
   */
  async signout(): Promise<{ success: boolean; error?: string }> {
    if (typeof window === 'undefined') {
      // Server-side, return error
      return { success: false, error: 'Authentication can only be performed on the client' };
    }
    
    try {
      await authApiService.signOut();
      return { success: true };
    } catch (error: any) {
      console.error('Sign out error:', error);
      return { success: false, error: error.message || 'Sign out failed' };
    }
  },

  /**
   * Get current user details
   */
  async getCurrentUser(): Promise<{ success: boolean; user?: User; error?: string }> {
    if (typeof window === 'undefined') {
      // Server-side, return error
      return { success: false, error: 'Authentication can only be performed on the client' };
    }
    
    try {
      const response = await authApiService.getSession();

      return {
        success: true,
        user: {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          emailVerified: response.user.emailVerified,
          createdAt: new Date(response.user.createdAt),
          updatedAt: response.user.updatedAt ? new Date(response.user.updatedAt) : null,
          isActive: true, // Assuming active session means active user
        }
      };
    } catch (error: any) {
      // If the error is about no token found, it's not really an error - just means user isn't logged in
      if (error.message.includes('No authentication token found')) {
        return { success: false, error: 'No active session' };
      }
      
      console.error('Get user error:', error);
      return { success: false, error: error.message || 'Failed to get user' };
    }
  }
};