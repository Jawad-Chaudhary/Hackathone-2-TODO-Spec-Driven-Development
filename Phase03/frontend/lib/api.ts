/**
 * API Client for AI Todo Chatbot Backend
 * Handles all communication with the FastAPI backend
 */

import type { ChatRequest, ChatResponse, Conversation, ApiError } from './types';

/**
 * API Client class with type-safe methods
 */
export class ApiClient {
  private baseUrl: string;
  private token: string;

  constructor(baseUrl?: string, token?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.token = token || this.getMockToken();
  }

  /**
   * Generate a mock JWT token for development
   * In production, this would come from Better Auth
   */
  private getMockToken(): string {
    // Mock JWT token for development - in production, use real auth
    return 'mock-jwt-token-for-development';
  }

  /**
   * Handle API errors with user-friendly messages
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;

      try {
        const errorData: ApiError = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If error response is not JSON, use default message
      }

      throw new Error(errorMessage);
    }

    return response.json();
  }

  /**
   * Send a chat message to the AI agent
   * @param userId - User ID (for now, use "demo-user")
   * @param message - User message (1-2000 chars)
   * @param conversationId - Optional conversation ID to continue existing conversation
   */
  async sendMessage(
    userId: string,
    message: string,
    conversationId?: number
  ): Promise<ChatResponse> {
    if (!message || message.length === 0) {
      throw new Error('Message cannot be empty');
    }

    if (message.length > 2000) {
      throw new Error('Message is too long (max 2000 characters)');
    }

    const requestBody: ChatRequest = {
      message,
      ...(conversationId && { conversation_id: conversationId }),
    };

    const response = await fetch(`${this.baseUrl}/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      },
      body: JSON.stringify(requestBody),
    });

    return this.handleResponse<ChatResponse>(response);
  }

  /**
   * Get list of all conversations for a user
   * @param userId - User ID
   */
  async getConversations(userId: string): Promise<Conversation[]> {
    const response = await fetch(`${this.baseUrl}/api/${userId}/conversations`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    return this.handleResponse<Conversation[]>(response);
  }

  /**
   * Get conversation history with all messages
   * @param userId - User ID
   * @param conversationId - Conversation ID
   */
  async getConversationHistory(
    userId: string,
    conversationId: number
  ): Promise<ChatResponse[]> {
    const response = await fetch(
      `${this.baseUrl}/api/${userId}/conversations/${conversationId}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      }
    );

    return this.handleResponse<ChatResponse[]>(response);
  }

  /**
   * Update the auth token
   * @param token - New JWT token
   */
  setToken(token: string): void {
    this.token = token;
  }
}

/**
 * Default API client instance
 * For use in Client Components
 */
export const apiClient = new ApiClient();
