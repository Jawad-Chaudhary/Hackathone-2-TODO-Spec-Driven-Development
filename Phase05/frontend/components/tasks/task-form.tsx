// [Task T043] TaskForm component for creating and editing tasks
// [Task T060] Pre-populate TaskForm with existing task data in edit mode
// [Task T061] Add "Save" button to TaskForm in edit mode
// [Task T062] Add "Cancel" button to TaskForm in edit mode
// [Task T063] Add validation to TaskForm
// [Task T064] Display validation errors inline in TaskForm
// [Task T036-T039] Phase 5: Add priority, tags, due date, and recurrence fields

"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TaskCreate, TaskUpdate } from "@/lib/types";

export interface TaskFormProps {
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void> | void;
  initialData?: {
    title: string;
    description?: string | null;
    priority?: "high" | "medium" | "low" | null;
    tags?: string[] | null;
    due_date?: string | null;
    recurrence?: "daily" | "weekly" | "monthly" | "custom" | null;
    recurrence_interval?: number | null;
  };
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
  const [priority, setPriority] = useState<"high" | "medium" | "low" | "">(
    initialData?.priority || ""
  );
  const [tags, setTags] = useState<string[]>(initialData?.tags || []);
  const [tagInput, setTagInput] = useState("");
  const [dueDate, setDueDate] = useState(initialData?.due_date || "");
  const [recurrence, setRecurrence] = useState<
    "daily" | "weekly" | "monthly" | "custom" | ""
  >(initialData?.recurrence || "");
  const [recurrenceInterval, setRecurrenceInterval] = useState<number | "">(
    initialData?.recurrence_interval || ""
  );
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
    recurrence_interval?: string;
  }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Add tag to tags list.
   */
  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput("");
    }
  };

  /**
   * Remove tag from tags list.
   */
  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  /**
   * Validate form fields before submission.
   * Returns true if valid, false otherwise.
   */
  const validate = (): boolean => {
    const newErrors: {
      title?: string;
      description?: string;
      recurrence_interval?: string;
    } = {};

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

    // Recurrence interval validation: required if custom recurrence
    if (recurrence === "custom" && !recurrenceInterval) {
      newErrors.recurrence_interval =
        "Interval is required for custom recurrence";
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
      const taskData: TaskCreate | TaskUpdate = {
        title: title.trim(),
        description: description.trim() || null,
        priority: priority || null,
        tags: tags.length > 0 ? tags : null,
        due_date: dueDate || null,
        recurrence: recurrence || null,
        recurrence_interval:
          recurrence === "custom" && recurrenceInterval
            ? Number(recurrenceInterval)
            : null,
      };

      await onSubmit(taskData);

      // Reset form after successful submission (only for create mode)
      if (!initialData) {
        setTitle("");
        setDescription("");
        setPriority("");
        setTags([]);
        setTagInput("");
        setDueDate("");
        setRecurrence("");
        setRecurrenceInterval("");
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
    setPriority(initialData?.priority || "");
    setTags(initialData?.tags || []);
    setTagInput("");
    setDueDate(initialData?.due_date || "");
    setRecurrence(initialData?.recurrence || "");
    setRecurrenceInterval(initialData?.recurrence_interval || "");
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

      {/* Priority Select - Phase 5 */}
      <div className="w-full">
        <label
          htmlFor="task-priority"
          className="block mb-2 text-sm font-medium text-gray-700"
        >
          Priority
        </label>
        <select
          id="task-priority"
          value={priority}
          onChange={(e) =>
            setPriority(e.target.value as "high" | "medium" | "low" | "")
          }
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">No priority</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Tags Input - Phase 5 */}
      <div className="w-full">
        <label
          htmlFor="task-tags"
          className="block mb-2 text-sm font-medium text-gray-700"
        >
          Tags
        </label>
        <div className="flex gap-2">
          <input
            id="task-tags"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addTag();
              }
            }}
            placeholder="Add a tag and press Enter"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            type="button"
            onClick={addTag}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Add
          </button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Due Date Input - Phase 5 */}
      <div className="w-full">
        <label
          htmlFor="task-due-date"
          className="block mb-2 text-sm font-medium text-gray-700"
        >
          Due Date
        </label>
        <input
          id="task-due-date"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Recurrence Select - Phase 5 */}
      <div className="w-full">
        <label
          htmlFor="task-recurrence"
          className="block mb-2 text-sm font-medium text-gray-700"
        >
          Recurrence
        </label>
        <select
          id="task-recurrence"
          value={recurrence}
          onChange={(e) =>
            setRecurrence(
              e.target.value as "daily" | "weekly" | "monthly" | "custom" | ""
            )
          }
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">No recurrence</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="custom">Custom interval</option>
        </select>
      </div>

      {/* Custom Recurrence Interval - Phase 5 */}
      {recurrence === "custom" && (
        <div className="w-full">
          <label
            htmlFor="task-recurrence-interval"
            className="block mb-2 text-sm font-medium text-gray-700"
          >
            Repeat every (days)
          </label>
          <input
            id="task-recurrence-interval"
            type="number"
            min="1"
            value={recurrenceInterval}
            onChange={(e) => setRecurrenceInterval(Number(e.target.value) || "")}
            placeholder="Number of days"
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-1 ${
              errors.recurrence_interval
                ? "border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:ring-blue-500"
            }`}
            aria-invalid={errors.recurrence_interval ? "true" : "false"}
          />
          {errors.recurrence_interval && (
            <p className="mt-2 text-sm text-red-600" role="alert">
              {errors.recurrence_interval}
            </p>
          )}
        </div>
      )}

      {/* Action Buttons - [Task T078] Responsive: stack on mobile, inline on tablet+ */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          type="submit"
          variant="default"
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
