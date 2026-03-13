// src/lib/auth/api-service.ts
// Custom API service to directly communicate with our backend endpoints

interface User {
  id: string;
  email: string;
  name: string | null;
  emailVerified: boolean;
  createdAt: string;
  updatedAt: string | null;
}

interface Session {
  id: string;
  userId: string;
  expiresAt: string;
}

interface AuthResponse {
  user: User;
  session: Session;
  token: string;
}

interface SignUpData {
  email: string;
  password: string;
  name?: string;
}

interface SignInData {
  email: string;
  password: string;
}

export const authApiService = {
  /**
   * Sign up a new user
   */
  async signUp(userData: SignUpData): Promise<AuthResponse> {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/sign-up`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      let errorData: { detail?: string } = {};
      try {
        errorData = await response.json();
      } catch (e) {
        // If response is not JSON, create a generic error object
        errorData = { detail: `Sign up failed with status ${response.status}` };
      }
      throw new Error(errorData.detail || `Sign up failed with status ${response.status}`);
    }

    return await response.json();
  },

  /**
   * Sign in a user
   */
  async signIn(credentials: SignInData): Promise<AuthResponse> {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/sign-in/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      let errorData: { detail?: string } = {};
      try {
        errorData = await response.json();
      } catch (e) {
        // If response is not JSON, create a generic error object
        errorData = { detail: `Sign in failed with status ${response.status}` };
      }
      throw new Error(errorData.detail || `Sign in failed with status ${response.status}`);
    }

    return await response.json();
  },

  /**
   * Get current session
   */
  async getSession(): Promise<AuthResponse> {
    // Get token from wherever it's stored (localStorage, cookie, etc.)
    const token = localStorage.getItem('auth-token'); // Or however you store the token

    if (!token) {
      // If no token exists, return a specific error that can be handled gracefully
      throw new Error('No authentication token found');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/session`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Check if the response is JSON before parsing
      const contentType = response.headers.get('content-type');
      let errorData = {};
      
      if (contentType && contentType.includes('application/json')) {
        errorData = await response.json().catch(() => ({}));
      } else {
        // If not JSON, create a generic error object
        errorData = { detail: await response.text().catch(() => 'Unknown error') };
      }

      // If the token is invalid/expired, the server will return a 401
      if (response.status === 401) {
        // Clear the invalid token
        localStorage.removeItem('auth-token');
      }
      throw new Error((errorData as any).detail || `Get session failed with status ${response.status}`);
    }

    return await response.json();
  },

  /**
   * Sign out the current user
   */
  async signOut(): Promise<void> {
    // Remove token from storage
    localStorage.removeItem('auth-token');
    
    // Optionally call backend sign-out endpoint
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/sign-out`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      // Even if backend sign-out fails, we still clear the local token
      console.warn('Sign out request failed, but clearing local token anyway', error);
    }
  }
};