'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ChatList } from '@/components/ChatList';
import { ChatInput } from '@/components/ChatInput';
import { ApiClient } from '@/lib/api';
import { authService } from '@/lib/auth';
import type { Message } from '@/lib/types';

/**
 * Main chat page component
 * Client Component - manages chat state and API calls
 * Requires authentication to access
 */
export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | undefined>(undefined);
  const [userId, setUserId] = useState<string | null>(null);
  const [apiClient, setApiClient] = useState<ApiClient | null>(null);

  /**
   * Check authentication on mount
   */
  useEffect(() => {
    const token = authService.getToken();
    const user = authService.getUser();

    if (!token || !user) {
      // Redirect to signin if not authenticated
      router.push('/signin');
      return;
    }

    // Initialize API client with token
    const client = new ApiClient(undefined, token);
    setApiClient(client);
    setUserId(user.user_id);
  }, [router]);

  /**
   * Handle sending a message
   */
  const handleSendMessage = useCallback(
    async (content: string) => {
      // Check if authenticated
      if (!apiClient || !userId) {
        setError('Not authenticated. Please sign in.');
        router.push('/signin');
        return;
      }

      // Clear any previous errors
      setError(null);

      // Add user message to UI immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        // Send message to backend
        const response = await apiClient.sendMessage(userId, content, conversationId);

        // Update conversation ID if this is a new conversation
        if (!conversationId) {
          setConversationId(response.conversation_id);
        }

        // Add assistant response to UI
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.response,
          tool_calls: response.tool_calls.length > 0 ? response.tool_calls : undefined,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        // Handle errors gracefully
        const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
        setError(errorMessage);

        // Add error message to chat
        const errorAssistantMessage: Message = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorAssistantMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, userId, apiClient, router]
  );

  /**
   * Handle sign out
   */
  const handleSignout = () => {
    authService.signout();
    router.push('/signin');
  };

  // Show loading while checking auth
  if (!apiClient || !userId) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 px-6 py-4 flex-shrink-0 shadow-sm">
        <div className="flex items-center justify-between max-w-5xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-lg font-bold shadow-md">
              AI
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                AI Todo Chatbot
              </h1>
              <p className="text-xs text-gray-500 flex items-center gap-1.5">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                {conversationId
                  ? `Conversation #${conversationId}`
                  : 'New conversation'}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                onClick={() => {
                  setMessages([]);
                  setConversationId(undefined);
                  setError(null);
                }}
                className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-xl transition-all duration-200 border border-transparent hover:border-blue-200 hover:shadow-sm"
                aria-label="Start new conversation"
              >
                <span className="text-lg">+</span>
                <span>New Chat</span>
              </button>
            )}
            <button
              onClick={handleSignout}
              className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all duration-200"
              aria-label="Sign out"
            >
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Error banner */}
      {error && (
        <div
          className="bg-red-50/80 backdrop-blur-sm border-b border-red-200 px-6 py-3.5 animate-fade-in"
          role="alert"
        >
          <div className="max-w-5xl mx-auto flex items-center gap-3 text-sm text-red-800">
            <span className="flex-shrink-0 w-6 h-6 bg-red-100 rounded-full flex items-center justify-center text-red-600 font-bold">!</span>
            <div className="flex-1">
              <span className="font-semibold">Error:</span> {error}
            </div>
            <button
              onClick={() => setError(null)}
              className="flex-shrink-0 px-3 py-1 text-xs font-medium text-red-700 hover:text-red-800 hover:bg-red-100 rounded-lg transition-colors"
              aria-label="Dismiss error"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Chat container */}
      <div className="flex-1 flex flex-col max-w-5xl w-full mx-auto overflow-hidden">
        {/* Messages */}
        <ChatList messages={messages} isLoading={isLoading} />

        {/* Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading}
          placeholder="Ask me to manage your tasks..."
        />
      </div>
    </div>
  );
}
