// [Task T026] Protected route HOC for authentication enforcement

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/session";

/**
 * Props for the ProtectedRoute HOC
 */
interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * Higher-Order Component (HOC) that enforces authentication on routes.
 *
 * Security Objective: Prevent unauthorized access to protected pages
 * - Checks for valid session on component mount
 * - Redirects to signin page if no session exists
 * - Only renders children if authentication is verified
 * - Implements defense-in-depth: client-side check + backend will also verify JWT
 *
 * Usage:
 * ```tsx
 * export default function ProtectedPage() {
 *   return (
 *     <ProtectedRoute>
 *       <YourContent />
 *     </ProtectedRoute>
 *   );
 * }
 * ```
 *
 * Security Notes:
 * - This is a UX optimization; backend MUST also verify tokens
 * - Session check happens on client side using Better Auth API
 * - Prevents unnecessary API calls and improves UX
 * - Always redirects on missing/invalid session (fail-secure)
 *
 * @param props - Component props containing children to render if authenticated
 * @returns Protected content or null while checking/redirecting
 */
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    /**
     * Checks if user has valid session.
     * Security: Runs on mount and validates session before rendering protected content
     */
    async function checkAuth() {
      try {
        // Check if user has valid session cookie
        const isAuth = await isAuthenticated();

        if (!isAuth) {
          // No valid session: redirect to signin
          // Fail-secure: deny access when session is missing or invalid
          router.push("/auth/signin");
          setAuthenticated(false);
        } else {
          // Valid session exists: allow access
          setAuthenticated(true);
        }
      } catch (error) {
        // On error, fail-secure: deny access
        console.error("Authentication check failed:", error);
        router.push("/auth/signin");
        setAuthenticated(false);
      }
    }

    checkAuth();
  }, [router]);

  // Show loading state while checking authentication
  // Don't render protected content until auth is verified
  if (authenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  // Don't render anything if not authenticated
  // User will be redirected to signin page
  if (!authenticated) {
    return null;
  }

  // Authenticated: render protected content
  return <>{children}</>;
}

/**
 * Alternative: HOC function pattern for wrapping page components
 *
 * Usage:
 * ```tsx
 * export default withAuth(function TasksPage() {
 *   return <div>Protected Content</div>;
 * });
 * ```
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> {
  return function AuthenticatedComponent(props: P) {
    return (
      <ProtectedRoute>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}
