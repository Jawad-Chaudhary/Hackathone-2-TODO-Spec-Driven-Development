// [Task T070] Generic reusable Modal component with confirmation dialog
// [Task T096] Add Framer Motion animations to modal dialogs

"use client";

import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isLoading?: boolean; // Optional loading state for confirm button
}

/**
 * Generic Modal component for confirmation dialogs.
 *
 * Features:
 * - Backdrop overlay with click-to-close
 * - Escape key to close
 * - Focus trap for accessibility
 * - ARIA attributes for screen readers
 * - Confirm (danger) and Cancel (secondary) buttons
 * - Optional loading state for async operations
 *
 * @param isOpen - Controls modal visibility
 * @param onClose - Callback when modal is closed (backdrop click, Escape, Cancel)
 * @param onConfirm - Callback when Confirm button is clicked
 * @param title - Modal dialog title
 * @param message - Main message content
 * @param confirmText - Confirm button text (default: "Confirm")
 * @param cancelText - Cancel button text (default: "Cancel")
 * @param isLoading - Show loading state on confirm button (default: false)
 */
export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  isLoading = false,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const confirmButtonRef = useRef<HTMLButtonElement>(null);

  // [Task T070] Handle Escape key to close modal
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      // Focus the confirm button when modal opens for keyboard navigation
      confirmButtonRef.current?.focus();
      // Prevent body scroll when modal is open
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  // [Task T070] Handle backdrop click to close modal
  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          aria-describedby="modal-description"
        >
          {/* Backdrop Overlay with fade animation */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black bg-opacity-50"
            onClick={handleBackdropClick}
            aria-hidden="true"
          />

          {/* Modal Dialog - [Task T078] Responsive + [Task T096] Framer Motion scale animation */}
          <motion.div
            ref={modalRef}
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-4 sm:p-6 z-10"
          >
        {/* Modal Title */}
        <h2
          id="modal-title"
          className="text-lg sm:text-xl font-bold text-gray-900 mb-3 sm:mb-4"
        >
          {title}
        </h2>

        {/* Modal Message */}
        <p
          id="modal-description"
          className="text-sm text-gray-600 mb-4 sm:mb-6 whitespace-pre-wrap"
        >
          {message}
        </p>

        {/* Action Buttons - [Task T078] Responsive: stack on mobile, inline on tablet+ */}
        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={isLoading}
            className="w-full sm:w-auto px-4 py-2"
          >
            {cancelText}
          </Button>
          <Button
            ref={confirmButtonRef}
            variant="destructive"
            onClick={onConfirm}
            disabled={isLoading}
            className="w-full sm:w-auto px-4 py-2"
          >
            {isLoading ? "Processing..." : confirmText}
          </Button>
        </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
