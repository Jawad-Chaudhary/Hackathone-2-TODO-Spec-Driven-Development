import type { ToolCall } from '@/lib/types';
import { clsx } from 'clsx';

interface ToolCallBadgeProps {
  toolCall: ToolCall;
}

/**
 * Display badge for AI tool usage
 * Shows tool name with appropriate icon/styling
 */
export function ToolCallBadge({ toolCall }: ToolCallBadgeProps) {
  // Extract tool name (handle both {name: ...} and {tool: ...} formats)
  const toolName = (toolCall as any).name || (toolCall as any).tool || 'unknown';

  // Map tool names to user-friendly labels
  const getToolLabel = (name: string): string => {
    const labels: Record<string, string> = {
      add_task: 'Added task',
      list_tasks: 'Listed tasks',
      update_task: 'Updated task',
      delete_task: 'Deleted task',
      mark_complete: 'Marked complete',
      mark_incomplete: 'Marked incomplete',
      complete_task: 'Completed task',
    };

    return labels[name] || (name ? name.replace(/_/g, ' ') : 'unknown tool');
  };

  // Get icon emoji for tool
  const getToolIcon = (name: string): string => {
    const icons: Record<string, string> = {
      add_task: '➕',
      list_tasks: '📋',
      update_task: '✏️',
      delete_task: '🗑️',
      mark_complete: '✅',
      complete_task: '✅',
      mark_incomplete: '⭕',
    };

    return icons[name] || '🔧';
  };

  // Get color scheme for tool type
  const getToolColors = (name: string): string => {
    const colors: Record<string, string> = {
      add_task: 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 border-green-300 hover:from-green-200 hover:to-emerald-200',
      list_tasks: 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border-blue-300 hover:from-blue-200 hover:to-indigo-200',
      update_task: 'bg-gradient-to-r from-orange-100 to-amber-100 text-orange-700 border-orange-300 hover:from-orange-200 hover:to-amber-200',
      delete_task: 'bg-gradient-to-r from-red-100 to-rose-100 text-red-700 border-red-300 hover:from-red-200 hover:to-rose-200',
      mark_complete: 'bg-gradient-to-r from-purple-100 to-violet-100 text-purple-700 border-purple-300 hover:from-purple-200 hover:to-violet-200',
      complete_task: 'bg-gradient-to-r from-purple-100 to-violet-100 text-purple-700 border-purple-300 hover:from-purple-200 hover:to-violet-200',
      mark_incomplete: 'bg-gradient-to-r from-gray-100 to-slate-100 text-gray-700 border-gray-300 hover:from-gray-200 hover:to-slate-200',
    };

    return colors[name] || 'bg-gradient-to-r from-gray-100 to-slate-100 text-gray-700 border-gray-300 hover:from-gray-200 hover:to-slate-200';
  };

  // Format arguments for display in tooltip
  const formatArgs = (args: Record<string, unknown>): string => {
    return Object.entries(args)
      .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
      .join(', ');
  };

  return (
    <div
      className={clsx(
        'group relative inline-flex items-center gap-2 px-3 py-1.5',
        'text-xs font-semibold rounded-xl',
        'border shadow-sm',
        'transition-all duration-200 transform hover:scale-105',
        getToolColors(toolName)
      )}
      role="status"
      aria-label={`Tool used: ${getToolLabel(toolName)}`}
      title={toolCall.args ? formatArgs(toolCall.args) : undefined}
    >
      <span className="text-base leading-none" aria-hidden="true">
        {getToolIcon(toolName)}
      </span>
      <span className="leading-none">{getToolLabel(toolName)}</span>

      {/* Tooltip on hover showing arguments */}
      {toolCall.args && Object.keys(toolCall.args).length > 0 && (
        <div className="invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-opacity duration-200 absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap z-10 shadow-xl pointer-events-none">
          <div className="font-mono text-xs">
            {formatArgs(toolCall.args)}
          </div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
        </div>
      )}
    </div>
  );
}
