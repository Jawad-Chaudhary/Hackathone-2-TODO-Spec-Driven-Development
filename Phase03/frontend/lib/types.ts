/**
 * Type definitions for AI Todo Chatbot
 * Aligned with backend API contracts
 */

/**
 * Tool call made by the AI agent
 */
export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
}

/**
 * Request payload for chat API
 */
export interface ChatRequest {
  message: string;  // 1-2000 characters
  conversation_id?: number;
}

/**
 * Response from chat API
 */
export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

/**
 * Conversation metadata
 */
export interface Conversation {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Chat message in UI
 */
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCall[];
  timestamp: Date;
}

/**
 * API error response
 */
export interface ApiError {
  detail: string;
  status?: number;
}

/**
 * Auth context (mock for now)
 */
export interface AuthContext {
  userId: string;
  token: string;
  isAuthenticated: boolean;
}
