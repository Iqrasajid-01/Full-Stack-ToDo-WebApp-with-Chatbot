// API service for handling backend calls

const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  private readonly maxRetries: number = 1; // Reduced from 3
  private readonly retryDelay: number = 500; // Reduced from 1000ms

  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${BACKEND_BASE_URL}${endpoint}`;

    // Get JWT token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth-token') : null;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Log the request for debugging
    console.log(`Making ${options.method || 'GET'} request to: ${url}`);
    console.log(`Using token: ${token ? 'Yes' : 'No'}`);
    console.log(`Headers:`, headers);

    // Retry logic for network errors
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        console.log(`Attempt ${attempt} for request to: ${url}`);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // Increased from 5s to 15s

        const response = await fetch(url, {
          ...options,
          headers,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        // Log the response for debugging
        console.log(`Response status: ${response.status} for request to: ${url}`);

        // If we get a 401 error, it means the token is invalid/expired
        if (response.status === 401) {
          // Clear the invalid token
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth-token');
          }
          
          // Try to refresh the session by redirecting to login
          // We'll throw a specific error that the calling function can handle
          const errorData = await response.json().catch(() => ({}));
          const errorMessage = `HTTP error! status: ${response.status} - ${errorData.detail || 'Unauthorized'}`;
          throw new Error(errorMessage);
        }

        if (!response.ok) {
          // Handle specific status codes
          if (response.status === 429) {
            // Rate limit exceeded - try to get retry info from headers
            const retryAfter = response.headers.get('Retry-After');
            let errorMessage = `Rate limit exceeded. Please try again `;
            
            if (retryAfter) {
              errorMessage += `after ${retryAfter} seconds.`;
            } else {
              errorMessage += `later.`;
            }
            
            try {
              const errorData = await response.json();
              if (errorData.detail) {
                errorMessage += ` - ${errorData.detail}`;
              }
            } catch (e) {
              // If response is not JSON, use status text
              errorMessage += ` - ${response.statusText}`;
            }
            
            throw new Error(errorMessage);
          }
          
          // Try to get error details from response
          let errorMessage = `HTTP error! status: ${response.status}`;
          try {
            const errorData = await response.json();
            if (errorData.detail) {
              errorMessage += ` - ${errorData.detail}`;
            }
          } catch (e) {
            // If response is not JSON, use status text
            errorMessage += ` - ${response.statusText}`;
          }
          throw new Error(errorMessage);
        }

        // For DELETE requests (status 204), return early without parsing JSON
        if (response.status === 204) {
          return {}; // Return empty object for successful DELETE
        }

        return await response.json();
      } catch (networkError: any) {
        // Check if the error is due to abort (e.g., component unmounted, timeout)
        if (networkError.name === 'AbortError' || networkError.message.includes('aborted')) {
          console.warn(`Request to ${url} was aborted (attempt ${attempt})`);
          // Don't retry on abort errors, just throw immediately
          throw new Error('Request was aborted');
        }

        // Check if this is an authentication error (401)
        if (networkError.message && networkError.message.includes('401')) {
          // Don't retry authentication errors
          throw networkError;
        }

        lastError = networkError;
        console.error(`Attempt ${attempt} failed for request to: ${url}:`, networkError);

        // If this was the last attempt, rethrow the error
        if (attempt === this.maxRetries) {
          break;
        }

        // Wait before retrying (exponential backoff could be implemented here)
        await this.delay(this.retryDelay * attempt);
      }
    }

    // Handle network errors (Failed to fetch, CORS, etc.)
    console.error(`Network error after ${this.maxRetries} attempts when requesting ${url}:`, lastError);

    // Provide more specific error information
    let errorMessage = `Network error: Unable to connect to the server.`;

    if (lastError instanceof TypeError && lastError.message.includes('fetch')) {
      errorMessage += ` The request to ${url} failed after ${this.maxRetries} attempts. This could be due to:`;
      errorMessage += `\n- Backend server not running on ${BACKEND_BASE_URL}`;
      errorMessage += `\n- Network connectivity issues`;
      errorMessage += `\n- CORS policy violations`;
      errorMessage += `\n- Firewall blocking the connection`;
      errorMessage += `\n- DNS resolution issues`;
    } else if (lastError) {
      errorMessage += ` ${lastError.message}`;
    }

    errorMessage += ` Please check that the backend is running and accessible at ${BACKEND_BASE_URL}.`;

    throw new Error(errorMessage);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async post(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async get(endpoint: string) {
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  async put(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint: string) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }
}

export const apiService = new ApiService();