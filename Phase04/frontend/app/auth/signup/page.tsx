// [Task T021, T031] Signup page with Better Auth integration using UI components

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

/**
 * Signup page with Better Auth email/password registration.
 *
 * Security Objective: Secure user registration with JWT token-based authentication
 * - Uses Better Auth's signUp.email method for credential creation
 * - JWT token automatically stored in httpOnly cookie by Better Auth
 * - Redirects to /tasks on successful registration
 * - Displays validation errors to user (inline and general)
 *
 * @returns Signup form component
 */

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
}

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
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

  // [Task T021] Client-side validation
  const validateForm = (): boolean => {
    const errors: FormErrors = {};

    // Name validation
    if (!formData.name.trim()) {
      errors.name = "Name is required";
    }

    // Email format validation
    if (!formData.email) {
      errors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = "Please enter a valid email address";
    }

    // Password minimum 8 characters
    if (!formData.password) {
      errors.password = "Password is required";
    } else if (formData.password.length < 8) {
      errors.password = "Password must be at least 8 characters";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * [Task T021] Handles signup form submission.
   * Security: Validates input, calls Better Auth API, handles errors without leaking sensitive info
   */
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError("");
    setFieldErrors({});

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call custom signup API endpoint
      // This will:
      // 1. Create user in user store
      // 2. Generate JWT token
      // 3. Store token in httpOnly cookie
      const response = await fetch("/api/auth/sign-up", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          name: formData.name,
        }),
      });

      const data = await response.json();

      // Check if signup was successful
      if (!response.ok || data.error) {
        // [Task T031] Display API error at top of form
        setGeneralError(data.error || "Signup failed. Email may already be in use.");
        setIsLoading(false);
        return;
      }

      // [Task T021] On success: redirect to /tasks
      // Use window.location for hard refresh to ensure session is loaded
      window.location.href = "/tasks";
    } catch (err) {
      // [Task T031] Display error message
      setGeneralError("An error occurred during signup. Please try again.");
      setIsLoading(false);
      console.error("Signup error:", err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{" "}
            <Link href="/auth/signin" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSignup}>
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
            {/* [Task T021] Name field (type="text") */}
            <Input
              id="name"
              type="text"
              label="Name"
              placeholder="Enter your name"
              value={formData.name}
              onChange={(e) => handleInputChange("name", e.target.value)}
              error={fieldErrors.name}
              required
            />

            {/* [Task T021] Email field (type="email") with format validation */}
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

            {/* [Task T021] Password field (type="password") minimum 8 characters */}
            <Input
              id="password"
              type="password"
              label="Password"
              placeholder="At least 8 characters"
              value={formData.password}
              onChange={(e) => handleInputChange("password", e.target.value)}
              error={fieldErrors.password}
              required
            />
          </div>

          {/* [Task T021] Use Button component from components/ui/ */}
          <div className="w-full">
            <Button
              type="submit"
              disabled={isLoading}
              variant="primary"
              className="w-full"
            >
              {isLoading ? "Creating account..." : "Sign up"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
