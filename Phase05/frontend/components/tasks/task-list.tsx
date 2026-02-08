// [Task T041, T044, T045, T046] TaskList component with empty, loading, and error states
// [Task T095] Add Framer Motion animations to task list

"use client";

import React from "react";
import { AnimatePresence } from "framer-motion";
import { TaskItem } from "./task-item";
import { Task } from "@/lib/types";

export interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  userId: string; // Required for TaskItem API calls
  onRetry?: () => void;
  onTaskDelete?: (taskId: number) => void; // Callback when task is deleted
  onTaskUpdate?: (taskId: number, updatedTask: Task) => void; // Callback when task is updated
}

/**
 * TaskList component displays an array of tasks with proper handling for:
 * - Loading state (skeleton UI)
 * - Empty state (no tasks message)
 * - Error state (error message with retry button)
 * - Success state (task items)
 *
 * @param tasks - Array of Task objects to display
 * @param loading - Whether tasks are currently being fetched
 * @param error - Error message if task fetching failed
 * @param userId - User ID for making API calls in TaskItem
 * @param onRetry - Optional retry handler for error state
 * @param onTaskDelete - Optional callback when a task is deleted
 */
export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  loading,
  error,
  userId,
  onRetry,
  onTaskDelete,
  onTaskUpdate,
}) => {
  // [Task T045, T078] Loading State: Show skeleton UI with responsive padding
  if (loading) {
    return (
      <div className="space-y-3 sm:space-y-4" aria-live="polite" aria-busy="true">
        <p className="sr-only">Loading tasks...</p>
        {[1, 2, 3, 4, 5].map((index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg shadow-sm p-3 sm:p-4 bg-white animate-pulse"
            aria-hidden="true"
          >
            <div className="flex items-start gap-3">
              {/* Skeleton checkbox */}
              <div className="flex-shrink-0 mt-1">
                <div className="w-5 h-5 rounded-full bg-gray-200"></div>
              </div>

              {/* Skeleton content */}
              <div className="flex-1 space-y-2">
                <div className="h-5 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-1/4"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // [Task T046, T078] Error State: Show error message with retry button (responsive)
  if (error) {
    return (
      <div
        className="border border-red-300 rounded-lg bg-red-50 p-4 sm:p-6 text-center"
        role="alert"
        aria-live="assertive"
      >
        <div className="flex justify-center mb-3">
          <svg
            className="w-10 h-10 sm:w-12 sm:h-12 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-base sm:text-lg font-semibold text-red-900 mb-2">
          Failed to Load Tasks
        </h3>
        <p className="text-sm text-red-700 mb-4">{error}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="w-full sm:w-auto px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors duration-200"
          >
            Try Again
          </button>
        )}
      </div>
    );
  }

  // [Task T044, T078] Empty State: Show message when no tasks exist (responsive)
  if (tasks.length === 0) {
    return (
      <div
        className="border border-gray-200 rounded-lg bg-gray-50 p-8 sm:p-12 text-center"
        role="status"
      >
        <div className="flex justify-center mb-4">
          <svg
            className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 className="text-lg sm:text-xl font-semibold text-gray-700 mb-2">
          No Tasks Yet
        </h3>
        <p className="text-sm sm:text-base text-gray-600">
          No tasks yet. Create your first task to get started!
        </p>
      </div>
    );
  }

  // Success State: Render task items - [Task T078] Responsive spacing, [Task T095] Framer Motion animations
  return (
    <div className="space-y-3 sm:space-y-4" aria-live="polite">
      <p className="sr-only">{tasks.length} tasks loaded</p>
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            userId={userId}
            onDelete={onTaskDelete}
            onUpdate={onTaskUpdate}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};
