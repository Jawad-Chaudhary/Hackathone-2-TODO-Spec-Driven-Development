'use client';

import { useEffect, useRef } from 'react';
import type { Message } from '@/lib/types';
import { ChatMessage } from './ChatMessage';

interface ChatListProps {
  messages: Message[];
  isLoading?: boolean;
}

/**
 * Scrollable message list component
 * Client Component - uses refs and effects for auto-scroll
 */
export function ChatList({ messages, isLoading = false }: ChatListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto chat-scrollbar"
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
      style={{
        backgroundImage: 'radial-gradient(circle at 1px 1px, rgb(229 231 235 / 0.3) 1px, transparent 0)',
        backgroundSize: '40px 40px',
      }}
    >
      {/* Empty state */}
      {messages.length === 0 && !isLoading && (
        <div className="flex items-center justify-center h-full px-4 text-center">
          <div className="max-w-lg animate-fade-in-up">
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-100 to-purple-100 rounded-3xl flex items-center justify-center text-5xl shadow-lg">
              💬
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">
              Start a Conversation
            </h2>
            <p className="text-gray-600 text-base leading-relaxed mb-6">
              Ask me to manage your tasks! I can add, list, update, and complete tasks
              for you using natural language.
            </p>

            {/* Example prompts */}
            <div className="grid gap-2 max-w-md mx-auto">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Try asking:
              </div>
              {[
                'Add a task to buy groceries',
                'Show me all my tasks',
                'Mark task 1 as complete',
              ].map((prompt, idx) => (
                <div
                  key={idx}
                  className="px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 hover:border-blue-300 hover:shadow-sm transition-all duration-200 cursor-default"
                  style={{ animationDelay: `${idx * 0.1}s` }}
                >
                  {prompt}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      {messages.length > 0 && (
        <div className="py-6">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex items-center gap-3 px-4 py-3 animate-fade-in">
          <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold shadow-md">
            AI
          </div>
          <div className="flex gap-2 px-5 py-4 bg-white border border-gray-200/50 rounded-2xl rounded-bl-md shadow-sm">
            <div
              className="w-2.5 h-2.5 bg-gradient-to-br from-blue-400 to-purple-400 rounded-full animate-bounce"
              style={{ animationDelay: '0ms' }}
            />
            <div
              className="w-2.5 h-2.5 bg-gradient-to-br from-blue-400 to-purple-400 rounded-full animate-bounce"
              style={{ animationDelay: '150ms' }}
            />
            <div
              className="w-2.5 h-2.5 bg-gradient-to-br from-blue-400 to-purple-400 rounded-full animate-bounce"
              style={{ animationDelay: '300ms' }}
            />
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={bottomRef} />
    </div>
  );
}
