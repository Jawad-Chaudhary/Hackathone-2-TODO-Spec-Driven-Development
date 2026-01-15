'use client';

import { useState, FormEvent, KeyboardEvent } from 'react';
import { clsx } from 'clsx';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * Chat input component with send button
 * Client Component - uses state and event handlers
 */
export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Type your message...',
}: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmedMessage = message.trim();

    if (trimmedMessage && !disabled) {
      onSend(trimmedMessage);
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (but allow Shift+Enter for new lines)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isMessageValid = message.trim().length > 0 && message.length <= 2000;

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-gray-200/50 bg-white/80 backdrop-blur-xl p-4 md:p-6"
    >
      <div className="relative">
        {/* Text input with floating send button */}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          rows={1}
          className={clsx(
            'w-full px-5 py-4 pr-32 rounded-2xl resize-none',
            'border-2 border-gray-200 focus:border-blue-400 focus:ring-4 focus:ring-blue-100',
            'text-sm leading-relaxed',
            'disabled:bg-gray-50 disabled:cursor-not-allowed disabled:text-gray-500',
            'transition-all duration-200',
            'max-h-32 overflow-y-auto',
            'shadow-sm focus:shadow-md',
            'placeholder:text-gray-400'
          )}
          aria-label="Message input"
          style={{
            height: 'auto',
            minHeight: '56px',
          }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = 'auto';
            target.style.height = `${Math.min(target.scrollHeight, 128)}px`;
          }}
        />

        {/* Character count indicator */}
        {message.length > 1500 && (
          <div
            className={clsx(
              'absolute bottom-3 left-4 px-2 py-1 rounded-full text-xs font-medium',
              'transition-all duration-200',
              message.length > 2000
                ? 'bg-red-100 text-red-700 animate-pulse'
                : message.length > 1800
                ? 'bg-orange-100 text-orange-700'
                : 'bg-gray-100 text-gray-600'
            )}
            aria-live="polite"
          >
            {message.length}/2000
          </div>
        )}

        {/* Floating send button */}
        <button
          type="submit"
          disabled={disabled || !isMessageValid}
          className={clsx(
            'absolute bottom-2.5 right-2.5',
            'flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm',
            'bg-gradient-to-r from-blue-600 to-indigo-600 text-white',
            'hover:from-blue-700 hover:to-indigo-700 active:scale-95',
            'disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed disabled:scale-100',
            'transition-all duration-200',
            'shadow-lg hover:shadow-xl disabled:shadow-none',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          )}
          aria-label="Send message"
        >
          {disabled ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Sending</span>
            </>
          ) : (
            <>
              <span>Send</span>
              <span className="text-lg leading-none">→</span>
            </>
          )}
        </button>
      </div>

      {/* Helper text */}
      <div className="flex items-center justify-between mt-3 px-1">
        <p className="text-xs text-gray-500 flex items-center gap-2">
          <kbd className="px-2 py-0.5 bg-gray-100 rounded text-xs font-mono">Enter</kbd>
          to send
          <span className="text-gray-400">•</span>
          <kbd className="px-2 py-0.5 bg-gray-100 rounded text-xs font-mono">Shift + Enter</kbd>
          for new line
        </p>
        {message.length > 0 && message.length <= 1500 && (
          <span className="text-xs text-gray-400">
            {message.length} characters
          </span>
        )}
      </div>
    </form>
  );
}
