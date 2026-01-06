// Custom session management helpers
// Works with our custom authentication API endpoints

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface Session {
  token: string;
  expiresAt: number;
}

export interface SessionData {
  session: Session | null;
  user: User | null;
}

/**
 * Checks if the user has a valid session.
 * This calls our custom /api/auth/session endpoint.
 */
export async function getSession(): Promise<SessionData | null> {
  try {
    const response = await fetch("/api/auth/session", {
      method: "GET",
      credentials: "include", // Important: include cookies
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Session check error:", error);
    return null;
  }
}

/**
 * Checks if the user is authenticated.
 * Returns true if a valid session exists.
 */
export async function isAuthenticated(): Promise<boolean> {
  const sessionData = await getSession();
  return !!(sessionData?.session && sessionData?.user);
}
