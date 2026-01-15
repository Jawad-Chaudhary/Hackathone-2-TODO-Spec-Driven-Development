import type { Message } from '@/lib/types';
import { ToolCallBadge } from './ToolCallBadge';
import { clsx } from 'clsx';

interface ChatMessageProps {
  message: Message;
}

/**
 * Individual chat message component
 * Displays user or assistant messages with appropriate styling
 */
export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={clsx(
        'flex w-full gap-3 px-4 py-3 animate-fade-in',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      {/* Avatar */}
      {!isUser && (
        <div
          className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold shadow-md"
          aria-label="AI Assistant"
        >
          AI
        </div>
      )}

      {/* Message content */}
      <div
        className={clsx(
          'flex flex-col gap-2 max-w-[80%] md:max-w-[70%]',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        {/* Message bubble */}
        <div
          className={clsx(
            'px-5 py-3.5 rounded-2xl',
            'break-words whitespace-pre-wrap',
            'transition-all duration-200',
            isUser
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-md shadow-lg hover:shadow-xl'
              : 'bg-white text-gray-900 border border-gray-200/50 rounded-bl-md shadow-sm hover:shadow-md'
          )}
        >
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>

        {/* Tool calls (only for assistant) */}
        {!isUser && message.tool_calls && message.tool_calls.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-1 animate-fade-in" style={{ animationDelay: '0.1s' }}>
            {message.tool_calls.map((toolCall, index) => (
              <ToolCallBadge key={index} toolCall={toolCall} />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <span
          className={clsx(
            'text-xs px-2 py-0.5 rounded-full',
            isUser ? 'text-blue-600 bg-blue-50' : 'text-gray-500 bg-gray-100'
          )}
          aria-label={`Sent at ${message.timestamp.toLocaleTimeString()}`}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>

      {/* User avatar */}
      {isUser && (
        <div
          className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white text-sm font-bold shadow-md"
          aria-label="You"
        >
          U
        </div>
      )}
    </div>
  );
}
