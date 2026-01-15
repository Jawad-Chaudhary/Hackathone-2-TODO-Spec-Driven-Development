/**
 * Authentication Service
 * Handles signup, signin, and token management for JWT authentication
 */

// Authentication types
export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface SigninRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user_id: string;
  email: string;
  full_name?: string;
}

export interface AuthError {
  detail: string;
}

/**
 * Auth Service class
 * Manages authentication state and API calls
 */
export class AuthService {
  private baseUrl: string;
  private readonly TOKEN_KEY = 'auth_token';
  private readonly USER_KEY = 'auth_user';

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Store authentication data in localStorage
   */
  private saveAuth(auth: AuthResponse): void {
    if (typeof window === 'undefined') return;

    localStorage.setItem(this.TOKEN_KEY, auth.token);
    localStorage.setItem(this.USER_KEY, JSON.stringify({
      user_id: auth.user_id,
      email: auth.email,
      full_name: auth.full_name,
    }));
  }

  /**
   * Clear authentication data from localStorage
   */
  private clearAuth(): void {
    if (typeof window === 'undefined') return;

    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  /**
   * Get stored JWT token
   */
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Get stored user info
   */
  getUser(): { user_id: string; email: string; full_name?: string } | null {
    if (typeof window === 'undefined') return null;

    const userStr = localStorage.getItem(this.USER_KEY);
    if (!userStr) return null;

    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  /**
   * Handle API errors
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `Error: ${response.status} ${response.statusText}`;

      try {
        const errorData: AuthError = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If error response is not JSON, use default message
      }

      throw new Error(errorMessage);
    }

    return response.json();
  }

  /**
   * Sign up a new user
   */
  async signup(request: SignupRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    const auth = await this.handleResponse<AuthResponse>(response);
    this.saveAuth(auth);
    return auth;
  }

  /**
   * Sign in an existing user
   */
  async signin(request: SigninRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/signin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    const auth = await this.handleResponse<AuthResponse>(response);
    this.saveAuth(auth);
    return auth;
  }

  /**
   * Sign out the current user
   */
  signout(): void {
    this.clearAuth();
  }
}

/**
 * Default auth service instance
 */
export const authService = new AuthService();
