// [Task T043] TaskForm component for creating and editing tasks
// [Task T060] Pre-populate TaskForm with existing task data in edit mode
// [Task T061] Add "Save" button to TaskForm in edit mode
// [Task T062] Add "Cancel" button to TaskForm in edit mode
// [Task T063] Add validation to TaskForm
// [Task T064] Display validation errors inline in TaskForm

"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TaskCreate, TaskUpdate } from "@/lib/types";

export interface TaskFormProps {
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void> | void;
  initialData?: { title: string; description?: string | null };
  onCancel?: () => void;
}

/**
 * TaskForm component for creating new tasks or editing existing ones.
 *
 * Features:
 * - Title input (required, 1-200 characters)
 * - Description textarea (optional, max 1000 characters)
 * - Client-side validation with error messages
 * - Submit and cancel actions
 *
 * @param onSubmit - Handler for form submission with TaskCreate data
 * @param initialData - Optional initial values for edit mode
 * @param onCancel - Optional cancel handler
 */
export const TaskForm: React.FC<TaskFormProps> = ({
  onSubmit,
  initialData,
  onCancel,
}) => {
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(
    initialData?.description || ""
  );
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
  }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Validate form fields before submission.
   * Returns true if valid, false otherwise.
   */
  const validate = (): boolean => {
    const newErrors: { title?: string; description?: string } = {};

    // Title validation: required, 1-200 characters
    if (!title.trim()) {
      newErrors.title = "Task title is required";
    } else if (title.length > 200) {
      newErrors.title = "Title must be 200 characters or less";
    }

    // Description validation: optional, max 1000 characters
    if (description && description.length > 1000) {
      newErrors.description = "Description must be 1000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate before submitting
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const taskData: TaskCreate = {
        title: title.trim(),
        description: description.trim() || null,
      };

      await onSubmit(taskData);

      // Reset form after successful submission (only for create mode)
      if (!initialData) {
        setTitle("");
        setDescription("");
        setErrors({});
      }
    } catch (error) {
      // Error handling is done by parent component
      console.error("Form submission error:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle cancel action.
   */
  const handleCancel = () => {
    setTitle(initialData?.title || "");
    setDescription(initialData?.description || "");
    setErrors({});
    onCancel?.();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Title Input */}
      <Input
        id="task-title"
        label="Title"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter task title"
        required
        error={errors.title}
      />

      {/* Description Textarea */}
      <div className="w-full">
        <label
          htmlFor="task-description"
          className="block mb-2 text-sm font-medium text-gray-700"
        >
          Description
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description (optional)"
          rows={4}
          className={`w-full px-4 py-2 border rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 resize-none ${
            errors.description
              ? "border-red-500 focus:ring-red-500 focus:border-red-500"
              : "border-gray-300 focus:ring-blue-500 focus:border-blue-500"
          }`}
          aria-invalid={errors.description ? "true" : "false"}
          aria-describedby={
            errors.description ? "task-description-error" : undefined
          }
        />
        {errors.description && (
          <p
            id="task-description-error"
            className="mt-2 text-sm text-red-600"
            role="alert"
          >
            {errors.description}
          </p>
        )}
      </div>

      {/* Action Buttons - [Task T078] Responsive: stack on mobile, inline on tablet+ */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting}
          className="w-full sm:w-auto"
        >
          {isSubmitting
            ? "Saving..."
            : initialData
            ? "Save Changes"
            : "Add Task"}
        </Button>

        {onCancel && (
          <Button
            type="button"
            variant="secondary"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="w-full sm:w-auto"
          >
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};
