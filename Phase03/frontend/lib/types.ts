// [Task T018] TypeScript types matching backend Pydantic schemas

/**
 * Task interface matching backend TaskResponse schema.
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
}

/**
 * Task creation payload matching backend TaskCreate schema.
 */
export interface TaskCreate {
  title: string; // Required, 1-200 characters
  description?: string | null; // Optional, max 1000 characters
}

/**
 * Task update payload matching backend TaskUpdate schema.
 * All fields are optional.
 */
export interface TaskUpdate {
  title?: string; // 1-200 characters if provided
  description?: string | null; // max 1000 characters if provided
  completed?: boolean;
}

/**
 * API error response structure.
 */
export interface APIError {
  detail: string | { loc: string[]; msg: string; type: string }[];
}

/**
 * Chat message request payload matching backend ChatRequest schema.
 */
export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
}

/**
 * Tool call information from OpenAI agent.
 */
export interface ToolCall {
  id: string;
  type: string;
  function: {
    name: string;
    arguments: string;
  };
}

/**
 * Chat response from backend matching ChatResponse schema.
 */
export interface ChatResponse {
  response: string;
  conversation_id: string;
  message_id?: number;
  tool_calls?: ToolCall[];
}
