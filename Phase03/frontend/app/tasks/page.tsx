// [Task T027, T040] Tasks page with full task management implementation

"use client";

import { useState, useEffect } from "react";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { TaskList } from "@/components/tasks/task-list";
import { TaskForm } from "@/components/tasks/task-form";
import { logoutAndRedirect } from "@/lib/logout";
import { getTasks, createTask } from "@/lib/api";
import { getSession } from "@/lib/session";
import { Task, TaskCreate, TaskUpdate } from "@/lib/types";

/**
 * Tasks page - main application view for managing todos.
 *
 * Security Objective: Ensure only authenticated users can access tasks
 * - Wrapped with ProtectedRoute HOC to enforce authentication
 * - Users without valid session are redirected to signin page
 * - Implements logout functionality for session termination
 *
 * Authentication Flow:
 * 1. ProtectedRoute checks for valid JWT token in cookie
 * 2. If no token or invalid token: redirect to /auth/signin
 * 3. If valid token: render tasks UI
 *
 * Authorization:
 * - Backend API will validate JWT and extract user_id
 * - All task queries will be filtered by authenticated user_id
 * - Prevents horizontal privilege escalation (users seeing others' tasks)
 *
 * Features:
 * - Create new tasks with title and description
 * - View all tasks in a list
 * - Loading, empty, and error states
 * - Responsive design with Tailwind CSS
 *
 * @returns Protected tasks page component
 */
function TasksPageContent() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(true);

  /**
   * Fetch user session and set user ID.
   */
  useEffect(() => {
    async function getUserId() {
      try {
        const sessionData = await getSession();
        if (sessionData?.user?.id) {
          setUserId(sessionData.user.id);
        } else {
          setError("Failed to get user session");
        }
      } catch (err) {
        console.error("Error getting user session:", err);
        setError("Failed to get user session");
      }
    }
    getUserId();
  }, []);

  /**
   * Fetch tasks when userId is available.
   */
  useEffect(() => {
    if (!userId) return;

    async function fetchTasks() {
      // TypeScript guard: userId is checked above
      if (!userId) return;

      setLoading(true);
      setError(null);

      try {
        const fetchedTasks = await getTasks(userId);
        setTasks(fetchedTasks);
      } catch (err) {
        console.error("Error fetching tasks:", err);
        setError(
          err instanceof Error ? err.message : "Failed to load tasks"
        );
      } finally {
        setLoading(false);
      }
    }

    fetchTasks();
  }, [userId]);

  /**
   * Handle logout action.
   */
  const handleLogout = async () => {
    await logoutAndRedirect();
  };

  /**
   * Handle task creation.
   */
  const handleCreateTask = async (data: TaskCreate | TaskUpdate) => {
    if (!userId) {
      setError("User session not available");
      return;
    }

    // Type guard: For creation, title must be present
    if (!data.title) {
      setError("Task title is required");
      return;
    }

    try {
      const taskData: TaskCreate = {
        title: data.title,
        description: data.description,
      };
      const newTask = await createTask(userId, taskData);
      // Add new task to the top of the list
      setTasks([newTask, ...tasks]);
    } catch (err) {
      console.error("Error creating task:", err);
      setError(
        err instanceof Error ? err.message : "Failed to create task"
      );
      throw err; // Re-throw to let form handle the error
    }
  };

  /**
   * Retry fetching tasks after an error.
   */
  const handleRetry = async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const fetchedTasks = await getTasks(userId);
      setTasks(fetchedTasks);
    } catch (err) {
      console.error("Error fetching tasks:", err);
      setError(
        err instanceof Error ? err.message : "Failed to load tasks"
      );
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle task deletion - remove task from local state.
   */
  const handleTaskDelete = (taskId: number) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  };

  /**
   * Handle task update - update task in local state.
   */
  const handleTaskUpdate = (taskId: number, updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) => (task.id === taskId ? updatedTask : task))
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                My Tasks
              </h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="ml-4 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {/* Task Creation Form */}
          {showForm && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Create New Task
              </h2>
              <TaskForm onSubmit={handleCreateTask} />
            </div>
          )}

          {/* Task List */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Your Tasks
              </h2>
              <span className="text-sm text-gray-500">
                {!loading && !error && `${tasks.length} task${tasks.length !== 1 ? "s" : ""}`}
              </span>
            </div>

            {userId && (
              <TaskList
                tasks={tasks}
                loading={loading}
                error={error}
                userId={userId}
                onRetry={handleRetry}
                onTaskDelete={handleTaskDelete}
                onTaskUpdate={handleTaskUpdate}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

/**
 * Exported page component wrapped with authentication protection.
 * This ensures the page is only accessible to authenticated users.
 */
export default function TasksPage() {
  return (
    <ProtectedRoute>
      <TasksPageContent />
    </ProtectedRoute>
  );
}
