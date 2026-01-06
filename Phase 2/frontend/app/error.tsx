// [Task T076] Global error boundary for catching React component errors

"use client";

import React from "react";
import { Button } from "@/components/ui/button";

export interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Global Error Boundary component for the application.
 * Catches unhandled errors in React components and displays a user-friendly error UI.
 *
 * Features:
 * - User-friendly error message
 * - "Reload Page" button to recover from errors
 * - Error details in development (error message)
 * - Accessible ARIA attributes
 * - Styled with Tailwind CSS
 *
 * @param error - The error that was thrown
 * @param reset - Function to reset the error boundary and retry rendering
 */
export default function Error({ error, reset }: ErrorProps) {
  return (
    <html lang="en">
      <body>
        <div
          className="min-h-screen flex items-center justify-center bg-gray-50 px-4"
          role="alert"
          aria-live="assertive"
        >
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            {/* Error Icon */}
            <div className="flex justify-center mb-4">
              <svg
                className="w-16 h-16 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>

            {/* Error Title */}
            <h1 className="text-2xl font-bold text-gray-900 mb-3">
              Something went wrong!
            </h1>

            {/* Error Description */}
            <p className="text-gray-600 mb-6">
              We encountered an unexpected error. Please try reloading the page.
              If the problem persists, contact support.
            </p>

            {/* Error Details (only in development) */}
            {process.env.NODE_ENV === "development" && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
                <p className="text-sm font-semibold text-red-900 mb-1">
                  Error Details:
                </p>
                <p className="text-xs text-red-700 font-mono break-words">
                  {error.message}
                </p>
                {error.digest && (
                  <p className="text-xs text-red-600 mt-2">
                    Error ID: {error.digest}
                  </p>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                variant="primary"
                onClick={reset}
                className="px-6 py-2"
              >
                Try Again
              </Button>
              <Button
                variant="secondary"
                onClick={() => (window.location.href = "/")}
                className="px-6 py-2"
              >
                Go Home
              </Button>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
