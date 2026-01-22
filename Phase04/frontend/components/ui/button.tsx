// [Task T029] Reusable Button component with Tailwind styling

"use client";

import React from "react";

export type ButtonVariant = "primary" | "secondary" | "danger";
export type ButtonType = "submit" | "button" | "reset";

export interface ButtonProps {
  children: React.ReactNode;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  type?: ButtonType;
  disabled?: boolean;
  variant?: ButtonVariant;
  className?: string;
}

/**
 * Reusable Button component with multiple variants
 * Supports primary, secondary, and danger variants with Tailwind styling
 */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      onClick,
      type = "button",
      disabled = false,
      variant = "primary",
      className = "",
    },
    ref
  ) => {
    // Base styles applied to all buttons
    const baseStyles =
      "px-4 py-2 rounded-lg font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

    // Variant-specific styles
    const variantStyles: Record<ButtonVariant, string> = {
      primary:
        "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 active:bg-blue-800",
      secondary:
        "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 active:bg-gray-400",
      danger:
        "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 active:bg-red-800",
    };

    // Combine all styles
    const combinedStyles = `${baseStyles} ${variantStyles[variant]} ${className}`;

    return (
      <button
        ref={ref}
        type={type}
        onClick={onClick}
        disabled={disabled}
        className={combinedStyles}
        aria-disabled={disabled}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
