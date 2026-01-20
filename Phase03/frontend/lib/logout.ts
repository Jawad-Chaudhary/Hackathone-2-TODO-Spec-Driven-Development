// [Task T025] Logout handler

"use client";

/**
 * Logout utility function.
 *
 * Security Objective: Properly terminate user session and clear authentication state
 * - Clears the session cookie by setting it to expire
 * - Can be called from any component in the application
 * - Returns redirect URL for navigation after logout
 *
 * @returns Promise that resolves to the signin page URL
 */
export async function logout(): Promise<string> {
  try {
    // Call logout API to clear the httpOnly session cookie
    await fetch("/api/auth/logout", {
      method: "POST",
      credentials: "include",
    });

    // Return signin URL for redirect
    return "/auth/signin";
  } catch (error) {
    // Log error for monitoring without exposing sensitive data
    console.error("Logout error:", error);

    // Even on error, redirect to signin page
    // This ensures user is not stuck in authenticated state
    return "/auth/signin";
  }
}

/**
 * Logout function with automatic redirect.
 * Use this in components where you want automatic navigation after logout.
 *
 * Security: Always redirects to signin page, even on error (fail-secure principle)
 */
export async function logoutAndRedirect(): Promise<void> {
  const redirectUrl = await logout();

  // Client-side redirect
  if (typeof window !== "undefined") {
    window.location.href = redirectUrl;
  }
}
