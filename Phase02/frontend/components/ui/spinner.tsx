// [Task T077] Reusable loading spinner component with Tailwind CSS

"use client";

import React from "react";

export type SpinnerSize = "sm" | "md" | "lg";

export interface SpinnerProps {
  size?: SpinnerSize;
  color?: string;
  className?: string;
  label?: string;
}

/**
 * Reusable Spinner component for loading states.
 *
 * Features:
 * - Three sizes: sm (16px), md (32px), lg (48px)
 * - Customizable color via Tailwind classes
 * - Smooth rotation animation using Tailwind's animate-spin
 * - Accessible with aria-label and role
 * - Can be used in buttons, pages, cards, etc.
 *
 * @param size - Spinner size: "sm" | "md" | "lg" (default: "md")
 * @param color - Tailwind text color class (default: "text-blue-600")
 * @param className - Additional CSS classes to apply
 * @param label - Accessible label for screen readers (default: "Loading")
 */
export const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  color = "text-blue-600",
  className = "",
  label = "Loading",
}) => {
  // Size mappings
  const sizeClasses: Record<SpinnerSize, string> = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  const sizeClass = sizeClasses[size];

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={label}
      className={`inline-flex items-center justify-center ${className}`}
    >
      <svg
        className={`animate-spin ${sizeClass} ${color}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span className="sr-only">{label}</span>
    </div>
  );
};

/**
 * Fullscreen loading spinner for page-level loading states.
 *
 * Features:
 * - Centers spinner in viewport
 * - Semi-transparent background
 * - Prevents interaction with underlying content
 * - Useful for page transitions or initial data loading
 *
 * @param message - Optional message to display below spinner (default: "Loading...")
 */
export const FullPageSpinner: React.FC<{ message?: string }> = ({
  message = "Loading...",
}) => {
  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white bg-opacity-90"
      role="status"
      aria-live="polite"
      aria-label={message}
    >
      <Spinner size="lg" color="text-blue-600" />
      <p className="mt-4 text-lg font-medium text-gray-700">{message}</p>
    </div>
  );
};

/**
 * Inline loading spinner for button loading states.
 *
 * Features:
 * - Small size optimized for buttons
 * - White color by default for primary buttons
 * - Inline display with text
 *
 * @param text - Text to display next to spinner (default: "Loading...")
 * @param color - Spinner color (default: "text-white")
 */
export const ButtonSpinner: React.FC<{
  text?: string;
  color?: string;
}> = ({ text = "Loading...", color = "text-white" }) => {
  return (
    <span className="inline-flex items-center gap-2">
      <Spinner size="sm" color={color} />
      <span>{text}</span>
    </span>
  );
};
