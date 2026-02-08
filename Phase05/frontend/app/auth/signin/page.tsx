// [Task T022, T031] Signin page with Better Auth integration using UI components

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

/**
 * Signin page with Better Auth email/password authentication.
 *
 * Security Objective: Secure user authentication with JWT token-based session
 * - Uses Better Auth's signIn.email method for credential verification
 * - JWT token automatically stored in httpOnly cookie by Better Auth
 * - Redirects to /tasks on successful authentication
 * - Generic error messages prevent user enumeration attacks
 *
 * @returns Signin form component
 */

interface FormErrors {
  email?: string;
  password?: string;
}

export default function SigninPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [fieldErrors, setFieldErrors] = useState<FormErrors>({});
  const [generalError, setGeneralError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  // [Task T031] Clear errors on input change
  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setFieldErrors((prev) => ({ ...prev, [field]: undefined }));
    setGeneralError("");
  };

  // [Task T022] Client-side validation
  const validateForm = (): boolean => {
    const errors: FormErrors = {};

    // Email format validation
    if (!formData.email) {
      errors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = "Please enter a valid email address";
    }

    // Password required
    if (!formData.password) {
      errors.password = "Password is required";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * [Task T022] Handles signin form submission.
   * Security: Prevents user enumeration by using generic error messages
   */
  const handleSignin = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError("");
    setFieldErrors({});

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call custom signin API endpoint
      // This will:
      // 1. Verify credentials against user store
      // 2. Generate JWT token with user_id claim
      // 3. Store token in httpOnly cookie
      const response = await fetch("/api/auth/sign-in", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      // Check if signin was successful
      if (!response.ok || data.error) {
        // [Task T031] Display API error at top of form
        // Generic error message to prevent user enumeration
        setGeneralError("Invalid email or password");
        setIsLoading(false);
        return;
      }

      // [Task T022] On success: redirect to /tasks
      // Use window.location for hard refresh to ensure session is loaded
      window.location.href = "/tasks";
    } catch (err) {
      // [Task T031] Display error message
      setGeneralError("Invalid email or password");
      setIsLoading(false);
      console.error("Signin error:", err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Don&apos;t have an account?{" "}
            <Link href="/auth/signup" className="font-medium text-blue-600 hover:text-blue-500">
              Sign up
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSignin}>
          {/* [Task T031] Show API errors at top of form (red alert box) */}
          {generalError && (
            <div className="rounded-md bg-red-50 p-4 border border-red-200">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-red-800">{generalError}</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            {/* [Task T022] Email field (type="email") with format validation */}
            <Input
              id="email"
              type="email"
              label="Email address"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) => handleInputChange("email", e.target.value)}
              error={fieldErrors.email}
              required
            />

            {/* [Task T022] Password field (type="password") */}
            <Input
              id="password"
              type="password"
              label="Password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={(e) => handleInputChange("password", e.target.value)}
              error={fieldErrors.password}
              required
            />
          </div>

          {/* [Task T022] Use Button component from components/ui/ */}
          <div className="w-full">
            <Button
              type="submit"
              disabled={isLoading}
              variant="default"
              className="w-full"
            >
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
