// [Task T027, T040] Tasks page with full task management implementation
// [Task T050] Connect to WebSocket for real-time notifications
// [Task T080] Integrated search, filter, and sort UI components
// [Task T094] Framer Motion page transitions

"use client";

import { useState, useEffect } from "react";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { TaskList } from "@/components/tasks/task-list";
import { TaskForm } from "@/components/tasks/task-form";
import { SearchBar } from "@/components/search-bar";
import { FilterPanel } from "@/components/filter-panel";
import { SortSelector, SortBy, SortOrder } from "@/components/sort-selector";
import { PageTransition } from "@/components/page-transition";
import { useFilterStore } from "@/stores/filter-store";
import { logoutAndRedirect } from "@/lib/logout";
import { getTasks, createTask } from "@/lib/api";
import { useSession } from "@/components/providers/session-provider";
import { Task, TaskCreate, TaskUpdate } from "@/lib/types";
import { useNotifications } from "@/components/providers/notification-provider";

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

  // [Task T080] Get filter and sort state from Zustand store
  const {
    search,
    status,
    priority,
    tags,
    dueStart,
    dueEnd,
    sortBy,
    sortOrder,
    setSearch,
    setSort,
  } = useFilterStore();

  /**
   * Use cached session and set user ID.
   * Also connect to WebSocket for real-time notifications.
   */
  const { session, loading: sessionLoading } = useSession();
  const { connect, disconnect } = useNotifications();

  useEffect(() => {
    const currentUserId = session?.user?.id;

    if (currentUserId) {
      setUserId(currentUserId);
      // Connect to WebSocket for real-time notifications
      connect(currentUserId);
    } else if (!sessionLoading) {
      setError("Failed to get user session");
    }

    // Disconnect WebSocket on unmount
    return () => {
      disconnect();
    };
  }, [session?.user?.id, sessionLoading]); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * Fetch tasks when userId or filters change.
   * [Task T082] Integrated filter and sort parameters.
   */
  useEffect(() => {
    // Wait for session to load before fetching tasks
    if (sessionLoading || !userId) return;

    async function fetchTasks() {
      // TypeScript guard: userId is checked above
      if (!userId) return;

      setLoading(true);
      setError(null);

      try {
        const fetchedTasks = await getTasks(userId, {
          status,
          priority: priority !== "all" ? priority : undefined,
          tags: tags.length > 0 ? tags : undefined,
          search: search || undefined,
          dueStart: dueStart || undefined,
          dueEnd: dueEnd || undefined,
          sortBy,
          sortOrder,
        });
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
  }, [sessionLoading, userId, search, status, priority, tags, dueStart, dueEnd, sortBy, sortOrder]);

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
        // Phase 5 fields
        priority: data.priority || null,
        tags: data.tags || null,
        due_date: data.due_date || null,
        recurrence: data.recurrence || null,
        recurrence_interval: data.recurrence_interval || null,
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
   * [Task T082] Apply current filters when retrying.
   */
  const handleRetry = async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const fetchedTasks = await getTasks(userId, {
        status,
        priority: priority !== "all" ? priority : undefined,
        tags: tags.length > 0 ? tags : undefined,
        search: search || undefined,
        dueStart: dueStart || undefined,
        dueEnd: dueEnd || undefined,
        sortBy,
        sortOrder,
      });
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

  /**
   * [Task T080] Handle sort changes from SortSelector.
   */
  const handleSortChange = (newSortBy: SortBy, newSortOrder: SortOrder) => {
    setSort(newSortBy, newSortOrder);
  };

  return (
    <PageTransition>
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

          {/* [Task T080] Search, Filter, and Sort Controls */}
          <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
            {/* Search Bar */}
            <SearchBar onSearch={setSearch} placeholder="Search tasks by title or description..." />

            {/* Filter Panel */}
            <FilterPanel availableTags={[]} />

            {/* Sort Selector */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <span className="text-sm text-gray-500">
                {!loading && !error && `${tasks.length} task${tasks.length !== 1 ? "s" : ""}`}
              </span>
              <SortSelector
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSortChange={handleSortChange}
              />
            </div>
          </div>

          {/* Task List */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Your Tasks
              </h2>
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
    </PageTransition>
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
