// [Task T020] API client base with JWT token extraction

import { getSession } from "./session";
import { env } from "./env";

/**
 * Base API client configuration.
 */
const API_BASE_URL = env.NEXT_PUBLIC_API_URL;

/**
 * Extract JWT token from session.
 * Returns token from httpOnly cookie.
 */
async function getAuthToken(): Promise<string | null> {
  try {
    const sessionData = await getSession();
    // Session token is stored in httpOnly cookie
    // The token is automatically sent with requests via cookies
    return sessionData?.session?.token || null;
  } catch (error) {
    console.error("Failed to get auth token:", error);
    return null;
  }
}

/**
 * Make authenticated API request with JWT token in Authorization header.
 * [Task T075] Enhanced error handling with network, server, and timeout errors.
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  // [Task T075] Add timeout for API requests (30 seconds)
  const timeoutMs = 30000;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: "include", // Include cookies for Better Auth
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Handle non-2xx responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));

      // [Task T075] Redirect to sign-in on 401 Unauthorized
      if (response.status === 401) {
        if (typeof window !== "undefined") {
          window.location.href = "/auth/signin";
        }
      }

      // [Task T075] Handle 500 Internal Server Error
      if (response.status >= 500) {
        throw new Error(
          "Server error. Please try again later or contact support if the problem persists."
        );
      }

      throw new Error(
        typeof errorData.detail === "string"
          ? errorData.detail
          : "An error occurred"
      );
    }

    // Handle 204 No Content (e.g., DELETE requests)
    if (response.status === 204) {
      return undefined as T;
    }

    // Parse JSON response for all other successful responses
    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    // [Task T075] Handle network errors
    if (error instanceof TypeError) {
      throw new Error(
        "Network error. Please check your internet connection and try again."
      );
    }

    // [Task T075] Handle timeout errors
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(
        "Request timeout. The server is taking too long to respond. Please try again."
      );
    }

    // Re-throw other errors
    throw error;
  }
}

/**
 * Export convenience method for making API requests.
 */
export const api = {
  get: <T>(endpoint: string) => apiClient<T>(endpoint, { method: "GET" }),

  post: <T>(endpoint: string, data?: unknown) =>
    apiClient<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: unknown) =>
    apiClient<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    apiClient<T>(endpoint, { method: "DELETE" }),
};

// ============================================
// Task API Functions
// ============================================

import { Task, TaskCreate, TaskUpdate } from "./types";

/**
 * [Task T038] Get all tasks for a user with optional status filtering.
 *
 * @param userId - The authenticated user's ID
 * @param status - Optional filter: "all" | "pending" | "completed"
 * @returns Promise<Task[]> - Array of tasks
 */
export async function getTasks(
  userId: string,
  status?: "all" | "pending" | "completed"
): Promise<Task[]> {
  const endpoint = status && status !== "all"
    ? `/api/${userId}/tasks?status=${status}`
    : `/api/${userId}/tasks`;

  return api.get<Task[]>(endpoint);
}

/**
 * [Task T039] Create a new task for a user.
 *
 * @param userId - The authenticated user's ID
 * @param data - Task creation payload (title, description)
 * @returns Promise<Task> - Created task with id and timestamps
 */
export async function createTask(
  userId: string,
  data: TaskCreate
): Promise<Task> {
  return api.post<Task>(`/api/${userId}/tasks`, data);
}

/**
 * [Task T052] Update an existing task for a user.
 *
 * @param userId - The authenticated user's ID
 * @param taskId - The task ID to update
 * @param data - Task update payload (title, description, completed)
 * @returns Promise<Task> - Updated task with new values
 */
export async function updateTask(
  userId: string,
  taskId: number,
  data: TaskUpdate
): Promise<Task> {
  return api.put<Task>(`/api/${userId}/tasks/${taskId}`, data);
}

/**
 * [Task T053] Toggle task completion status.
 * Helper function for convenience when toggling completed state.
 *
 * @param userId - The authenticated user's ID
 * @param taskId - The task ID to toggle
 * @param currentCompleted - Current completion status
 * @returns Promise<Task> - Updated task with toggled completion
 */
export async function toggleComplete(
  userId: string,
  taskId: number,
  currentCompleted: boolean
): Promise<Task> {
  return updateTask(userId, taskId, { completed: !currentCompleted });
}

/**
 * [Task T068] Delete a task for a user.
 *
 * @param userId - The authenticated user's ID
 * @param taskId - The task ID to delete
 * @returns Promise<void> - 204 No Content on success
 */
export async function deleteTask(
  userId: string,
  taskId: number
): Promise<void> {
  // DELETE endpoint returns 204 No Content, so we use api.delete
  // The apiClient will handle the response parsing
  await api.delete<void>(`/api/${userId}/tasks/${taskId}`);
}
