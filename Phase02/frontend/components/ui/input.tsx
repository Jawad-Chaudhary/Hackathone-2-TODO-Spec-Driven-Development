// [Task T030] Reusable Input component with Tailwind styling

"use client";

import React from "react";

export type InputType = "text" | "email" | "password";

export interface InputProps {
  type?: InputType;
  placeholder?: string;
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  label?: string;
  id: string;
  required?: boolean;
  className?: string;
}

/**
 * Reusable Input component with label and error handling
 * Supports text, email, and password input types with validation states
 */
export const Input: React.FC<InputProps> = ({
  type = "text",
  placeholder,
  value,
  onChange,
  error,
  label,
  id,
  required = false,
  className = "",
}) => {
  // Base input styles
  const baseInputStyles =
    "w-full px-4 py-2 border rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1";

  // Conditional styles based on error state
  const inputStyles = error
    ? `${baseInputStyles} border-red-500 focus:ring-red-500 focus:border-red-500`
    : `${baseInputStyles} border-gray-300 focus:ring-blue-500 focus:border-blue-500`;

  // Combine with custom className
  const combinedInputStyles = `${inputStyles} ${className}`;

  return (
    <div className="w-full">
      {/* Label */}
      {label && (
        <label
          htmlFor={id}
          className="block mb-2 text-sm font-medium text-gray-700"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Input field */}
      <input
        type={type}
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={combinedInputStyles}
        aria-invalid={error ? "true" : "false"}
        aria-describedby={error ? `${id}-error` : undefined}
      />

      {/* Error message */}
      {error && (
        <p
          id={`${id}-error`}
          className="mt-2 text-sm text-red-600"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
};
