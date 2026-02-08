// [Task T077] Chat page with OpenAI ChatKit integration
// [Task T094] Framer Motion page transitions

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { PageTransition } from "@/components/page-transition";
import { sendMessage, hasToolCalls } from "@/lib/chat-api";
import { useSession } from "@/components/providers/session-provider";
import { logoutAndRedirect } from "@/lib/logout";
import { ChatResponse, ToolCall } from "@/lib/types";

/**
 * Chat page content component.
 *
 * Features:
 * - OpenAI ChatKit integration for conversational UI
 * - JWT authentication with automatic token handling
 * - Conversation persistence with conversation_id
 * - Tool call display when AI agent performs actions
 * - Loading and error states
 * - Responsive design with Tailwind CSS
 *
 * Security:
 * - Protected with authentication check
 * - JWT token automatically included in API requests
 * - User can only access their own chat conversations
 */
function ChatPageContent() {
  const router = useRouter();
  const { session, loading: sessionLoading } = useSession();
  const [userId, setUserId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<
    Array<{ role: "user" | "assistant"; content: string; toolCalls?: ToolCall[] }>
  >([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Use cached session and set user ID.
   */
  useEffect(() => {
    const currentUserId = session?.user?.id;

    if (currentUserId) {
      setUserId(currentUserId);
    } else if (!sessionLoading) {
      setError("Failed to get user session");
      router.push("/auth/signin");
    }
  }, [session, sessionLoading, router]);

  /**
   * Handle logout action.
   */
  const handleLogout = async () => {
    await logoutAndRedirect();
  };

  /**
   * Handle sending a message to the AI agent.
   */
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!userId) {
      setError("User session not available");
      return;
    }

    if (!inputMessage.trim()) {
      return;
    }

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setLoading(true);
    setError(null);

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      { role: "user" as const, content: userMessage },
    ]);

    try {
      // Send message to backend AI agent
      const response: ChatResponse = await sendMessage(
        userMessage,
        conversationId || undefined
      );

      // Store conversation ID for future messages
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to chat
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant" as const,
          content: response.response,
          toolCalls: response.tool_calls,
        },
      ]);
    } catch (err) {
      console.error("Error sending message:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);

      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant" as const,
          content: `Error: ${errorMessage}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Render tool calls as badges.
   */
  const renderToolCalls = (toolCalls: ToolCall[] | undefined) => {
    if (!toolCalls || toolCalls.length === 0) {
      return null;
    }

    return (
      <div className="mt-2 flex flex-wrap gap-2">
        {toolCalls.map((toolCall) => (
          <div
            key={toolCall.id}
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
          >
            <svg
              className="mr-1.5 h-3 w-3"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"
                clipRule="evenodd"
              />
            </svg>
            {toolCall.function.name}
          </div>
        ))}
      </div>
    );
  };

  if (sessionLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Loading chat...</div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Navigation Bar */}
        <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">AI Chat</h1>
              <button
                onClick={() => router.push("/tasks")}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                View Tasks
              </button>
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

      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full py-8 px-4 sm:px-6 lg:px-8">
        {/* Messages Area */}
        <div className="flex-1 bg-white rounded-lg shadow-sm p-6 mb-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No messages yet
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Start a conversation by sending a message below.
              </p>
              <p className="mt-2 text-xs text-gray-400">
                Try: &quot;Add a task to buy groceries&quot; or &quot;List my
                tasks&quot;
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-3/4 rounded-lg px-4 py-2 ${
                      message.role === "user"
                        ? "bg-indigo-600 text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">
                      {message.content}
                    </p>
                    {message.role === "assistant" &&
                      renderToolCalls(message.toolCalls)}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError(null)}
                  className="inline-flex text-red-400 hover:text-red-500"
                >
                  <span className="sr-only">Dismiss</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSendMessage} className="bg-white rounded-lg shadow-sm p-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message... (e.g., 'Add a task to buy groceries')"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </form>
      </div>
      </div>
    </PageTransition>
  );
}

/**
 * Exported chat page component wrapped with authentication protection.
 * This ensures the page is only accessible to authenticated users.
 */
export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatPageContent />
    </ProtectedRoute>
  );
}
