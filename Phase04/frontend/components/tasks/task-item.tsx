// [Task T042] TaskItem component for displaying a single task
// [Task T054] Add checkbox for task completion toggle
// [Task T055] Add strikethrough styling for completed tasks
// [Task T056] Implement optimistic UI update
// [Task T057] Add edit mode state to TaskItem component
// [Task T058] Add "Edit" button to TaskItem component
// [Task T059] Render TaskForm component when isEditing = true in TaskItem
// [Task T069] Add "Delete" button to TaskItem component
// [Task T071] Show confirmation modal on delete click
// [Task T072] Call deleteTask() on "Confirm" in modal
// [Task T073] Close modal on "Cancel" without deleting

"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Task, TaskUpdate } from "@/lib/types";
import { toggleComplete, updateTask, deleteTask } from "@/lib/api";
import { TaskForm } from "./task-form";

export interface TaskItemProps {
  task: Task;
  userId: string; // Required for API calls
  onDelete?: (taskId: number) => void; // Callback to remove task from list
  onUpdate?: (taskId: number, updatedTask: Task) => void; // Callback to update task in list
}

/**
 * TaskItem component displays a single task with all its details.
 *
 * Features:
 * - Interactive checkbox for completion toggle
 * - Title and description display with strikethrough for completed tasks
 * - Optimistic UI updates for instant feedback
 * - Error handling with revert on failure
 * - Formatted creation date
 * - Card-based layout with Tailwind styling
 * - Edit mode with inline TaskForm component
 * - Save and Cancel actions for editing
 * - Delete button with confirmation modal
 * - Task deletion with loading state
 *
 * @param task - Task object with id, title, description, completed, created_at
 * @param userId - User ID for making API calls
 * @param onDelete - Optional callback to remove task from parent list
 */
export const TaskItem: React.FC<TaskItemProps> = ({ task, userId, onDelete, onUpdate }) => {
  // [Task T056] Local state for optimistic UI updates
  const [isCompleted, setIsCompleted] = useState(task.completed);
  const [error, setError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  // [Task T057] Edit mode state
  const [isEditing, setIsEditing] = useState(false);

  // [Task T071] Delete modal state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Sync local state with prop changes (e.g., after refetch)
  useEffect(() => {
    setIsCompleted(task.completed);
  }, [task.completed]);
  /**
   * [Task T056] Handle checkbox toggle with optimistic UI update.
   * Updates UI immediately, then calls API. Reverts on error.
   */
  const handleToggle = async () => {
    const previousState = isCompleted;

    // Optimistic update
    setIsCompleted(!isCompleted);
    setError(null);
    setIsUpdating(true);

    try {
      await toggleComplete(userId, task.id, previousState);
      // Success - keep optimistic state
    } catch (err) {
      // Revert on error
      setIsCompleted(previousState);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update task";
      setError(errorMessage);
      console.error("Task toggle error:", err);
    } finally {
      setIsUpdating(false);
    }
  };

  /**
   * [Task T061] Handle task edit submission.
   * Calls updateTask API and exits edit mode on success.
   */
  const handleSaveEdit = async (data: TaskUpdate) => {
    setError(null);
    setIsUpdating(true);

    try {
      const updatedTask = await updateTask(userId, task.id, data);
      setIsEditing(false); // Exit edit mode on success
      // Notify parent component to update the task in the list
      onUpdate?.(task.id, updatedTask);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update task";
      setError(errorMessage);
      console.error("Task update error:", err);
      throw err; // Re-throw to let TaskForm handle the error state
    } finally {
      setIsUpdating(false);
    }
  };

  /**
   * [Task T062] Handle edit cancellation.
   * Exits edit mode without saving changes.
   */
  const handleCancelEdit = () => {
    setIsEditing(false);
    setError(null);
  };

  /**
   * [Task T072] Handle task deletion confirmation.
   * Calls deleteTask API and removes task from UI on success.
   */
  const handleDeleteConfirm = async () => {
    setIsDeleting(true);
    setError(null);

    try {
      await deleteTask(userId, task.id);
      // Success - close modal and notify parent to remove task from list
      setShowDeleteModal(false);
      onDelete?.(task.id);
    } catch (err) {
      // Error - show error message and keep modal open
      const errorMessage =
        err instanceof Error ? err.message : "Failed to delete task";
      setError(errorMessage);
      console.error("Task deletion error:", err);
    } finally {
      setIsDeleting(false);
    }
  };

  /**
   * [Task T073] Handle delete modal cancellation.
   * Closes modal without deleting task.
   */
  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setError(null);
  };

  /**
   * Format ISO 8601 datetime string to readable date.
   * Example: "2026-01-03T10:30:00Z" -> "Jan 3, 2026"
   */
  const formatDate = (isoString: string): string => {
    try {
      const date = new Date(isoString);
      return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      }).format(date);
    } catch (error) {
      console.error("Date formatting error:", error);
      return "Invalid date";
    }
  };

  return (
    <Card variant="default">
      {/* [Task T059] Conditionally render TaskForm in edit mode or normal display */}
      {isEditing ? (
        // Edit mode: Show TaskForm with pre-populated data
        <div className="p-2">
          <TaskForm
            onSubmit={handleSaveEdit}
            onCancel={handleCancelEdit}
            initialData={{ title: task.title, description: task.description }}
          />
        </div>
      ) : (
        // Normal mode: Show task display with Edit button
        <div className="flex items-start gap-3">
          {/* [Task T054] Interactive Checkbox for Completion Toggle */}
          <div className="flex-shrink-0 mt-1">
            <input
              type="checkbox"
              checked={isCompleted}
              onChange={handleToggle}
              disabled={isUpdating}
              className={`w-5 h-5 rounded border-2 cursor-pointer transition-colors ${
                isCompleted
                  ? "bg-green-500 border-green-500"
                  : "bg-white border-gray-300"
              } ${isUpdating ? "opacity-50 cursor-not-allowed" : ""}
              hover:border-green-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2`}
              aria-label={`Mark task "${task.title}" as ${isCompleted ? "incomplete" : "complete"}`}
              id={`task-checkbox-${task.id}`}
            />
          </div>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            {/* [Task T055] Title with strikethrough for completed tasks */}
            <label
              htmlFor={`task-checkbox-${task.id}`}
              className="cursor-pointer"
            >
              <h3
                className={`text-lg font-semibold mb-1 transition-colors ${
                  isCompleted
                    ? "line-through text-gray-500"
                    : "text-gray-900"
                }`}
              >
                {task.title}
              </h3>
            </label>

            {/* [Task T055] Description with strikethrough for completed tasks */}
            {task.description && (
              <p
                className={`text-sm mb-2 whitespace-pre-wrap transition-colors ${
                  isCompleted
                    ? "line-through text-gray-400"
                    : "text-gray-600"
                }`}
              >
                {task.description}
              </p>
            )}

            {/* Error Message */}
            {error && (
              <div className="mb-2 text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                {error}
              </div>
            )}

            {/* Metadata Row: Created Date and Action Buttons - [Task T078] Responsive layout */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <svg
                  className="w-4 h-4 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span>Created {formatDate(task.created_at)}</span>
              </div>

              {/* Action Buttons: Edit and Delete - [Task T078] Full width on mobile */}
              <div className="flex gap-2">
                {/* [Task T058] Edit Button */}
                <Button
                  variant="secondary"
                  onClick={() => setIsEditing(true)}
                  disabled={isUpdating || isDeleting}
                  className="text-sm px-3 py-1 flex-1 sm:flex-none"
                >
                  Edit
                </Button>

                {/* [Task T069] Delete Button */}
                <Button
                  variant="danger"
                  onClick={() => setShowDeleteModal(true)}
                  disabled={isUpdating || isDeleting}
                  className="text-sm px-3 py-1 flex-1 sm:flex-none"
                >
                  Delete
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* [Task T071] Confirmation Modal for Delete Action */}
      <Modal
        isOpen={showDeleteModal}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        title="Delete Task"
        message="Are you sure you want to delete this task? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        isLoading={isDeleting}
      />
    </Card>
  );
};
