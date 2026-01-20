// [Task T047] Reusable Card component with Tailwind styling

"use client";

import React from "react";

export type CardVariant = "default" | "hover";

export interface CardProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  variant?: CardVariant;
}

/**
 * Reusable Card component with default and hover variants.
 * Provides a styled container with border, rounded corners, shadow, and padding.
 *
 * @param children - Content to display inside the card
 * @param onClick - Optional click handler for interactive cards
 * @param className - Additional Tailwind classes to apply
 * @param variant - Visual variant: "default" or "hover" (with interactive effects)
 */
export const Card: React.FC<CardProps> = ({
  children,
  onClick,
  className = "",
  variant = "default",
}) => {
  // Base styles applied to all cards
  const baseStyles =
    "border border-gray-200 rounded-lg shadow-sm p-4 bg-white transition-all duration-200";

  // Variant-specific styles
  const variantStyles: Record<CardVariant, string> = {
    default: "",
    hover:
      "hover:shadow-md hover:border-gray-300 cursor-pointer active:scale-[0.99]",
  };

  // Combine all styles
  const combinedStyles = `${baseStyles} ${variantStyles[variant]} ${className}`;

  // If onClick is provided, render as a clickable div with appropriate ARIA attributes
  if (onClick) {
    return (
      <div
        className={combinedStyles}
        onClick={onClick}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onClick();
          }
        }}
        role="button"
        tabIndex={0}
        aria-pressed="false"
      >
        {children}
      </div>
    );
  }

  // Otherwise, render as a static container
  return <div className={combinedStyles}>{children}</div>;
};
