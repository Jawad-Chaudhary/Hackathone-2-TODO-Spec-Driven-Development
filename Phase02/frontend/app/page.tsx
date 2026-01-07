// [Task T028] Landing page with authentication redirect logic

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/session";

/**
 * Landing page root component with authentication-based routing.
 *
 * Security Objective: Route users based on authentication state
 * - Authenticated users: redirect to /tasks (their main workspace)
 * - Unauthenticated users: redirect to /auth/signin
 * - Prevents unauthorized users from accessing application
 * - Provides seamless UX for authenticated users
 *
 * Authentication Flow:
 * 1. Check for valid session using Better Auth API
 * 2. If session exists: redirect to /tasks
 * 3. If no session: redirect to /auth/signin
 * 4. Show loading state during check
 *
 * Security Notes:
 * - Session check happens client-side for UX optimization
 * - Backend still validates JWT on all API requests (defense-in-depth)
 * - Fail-secure: on error, redirect to signin
 *
 * @returns Loading indicator or null (user will be redirected)
 */
export default function HomePage() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    /**
     * Checks authentication status and redirects accordingly.
     * Security: Validates session before determining redirect target
     */
    async function checkAuthAndRedirect() {
      try {
        // Check if JWT token exists in cookie and is valid
        const authenticated = await isAuthenticated();

        if (authenticated) {
          // Valid session exists: redirect to main app
          router.push("/tasks");
        } else {
          // No valid session: redirect to signin
          router.push("/auth/signin");
        }
      } catch (error) {
        // On error, fail-secure: redirect to signin
        console.error("Session check error:", error);
        router.push("/auth/signin");
      } finally {
        setIsChecking(false);
      }
    }

    checkAuthAndRedirect();
  }, [router]);

  // Show loading state while checking authentication
  // This prevents flash of content before redirect
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Return null after redirect is initiated
  // User will be navigated to appropriate page
  return null;
}
