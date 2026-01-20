// [Task T073-T074] Chat API client with JWT authentication
// Connects to backend POST /api/{user_id}/chat endpoint

import { getSession } from './session';
import { ChatRequest, ChatResponse } from './types';

/**
 * Send a chat message to the backend AI agent.
 *
 * This function:
 * 1. Gets JWT token from session
 * 2. Sends POST request to /api/{user_id}/chat with Authorization header
 * 3. Handles errors (401, 403, 500, network)
 * 4. Returns the chat response with conversation_id
 *
 * @param message - The user's chat message
 * @param conversationId - Optional conversation ID for continuing a conversation
 * @returns Promise<ChatResponse> - Response with message, conversation_id, and optional tool_calls
 *
 * @throws Error on authentication failure (401), server error (500), or network issues
 *
 * Example usage:
 * ```typescript
 * const response = await sendMessage("Add a task to buy groceries");
 * console.log(response.response); // AI agent's response
 * console.log(response.conversation_id); // For continuing the conversation
 * ```
 */
export async function sendMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  // Get current session with JWT token
  const sessionData = await getSession();

  if (!sessionData?.session?.token || !sessionData?.user?.id) {
    throw new Error('Not authenticated. Please sign in to continue.');
  }

  // Validate message
  if (!message || message.trim().length === 0) {
    throw new Error('Message cannot be empty');
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const userId = sessionData.user.id;
  const token = sessionData.session.token;

  // Prepare request payload
  const requestPayload: ChatRequest = {
    message: message.trim(),
    ...(conversationId && { conversation_id: conversationId }),
  };

  try {
    const response = await fetch(`${apiUrl}/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(requestPayload),
    });

    // Handle authentication errors
    if (response.status === 401) {
      throw new Error('Authentication required. Please sign in again.');
    }

    if (response.status === 403) {
      throw new Error('Access forbidden. You can only access your own conversations.');
    }

    // Handle other errors
    if (!response.ok) {
      let errorMessage = `Chat request failed: ${response.statusText}`;

      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // If error parsing fails, use default message
      }

      throw new Error(errorMessage);
    }

    // Parse and return successful response
    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    // Re-throw our custom errors
    if (error instanceof Error) {
      throw error;
    }

    // Handle network errors
    throw new Error('Network error. Please check your connection and try again.');
  }
}

/**
 * Type guard to check if a chat response contains tool calls.
 *
 * @param response - The chat response to check
 * @returns true if response has tool_calls array with at least one item
 */
export function hasToolCalls(response: ChatResponse): boolean {
  return Array.isArray(response.tool_calls) && response.tool_calls.length > 0;
}
