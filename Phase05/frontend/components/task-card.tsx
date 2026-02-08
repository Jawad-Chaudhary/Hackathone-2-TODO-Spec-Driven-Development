// [Task T037] Task card component with priority, tags, due date, and recurrence indicators

"use client"

import * as React from "react"
import { Calendar, Repeat, Tag, AlertCircle } from "lucide-react"

interface TaskCardProps {
  task: Task
  onComplete?: (taskId: number) => void
  onEdit?: (task: Task) => void
  onDelete?: (taskId: number) => void
}

export interface Task {
  id: number
  title: string
  description?: string
  completed: boolean
  priority?: "high" | "medium" | "low"
  tags?: string[]
  due_date?: string
  recurrence?: "daily" | "weekly" | "monthly" | "custom"
  recurrence_interval?: number
  created_at: string
  updated_at: string
}

const priorityStyles = {
  high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  low: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
}

const recurrenceLabels = {
  daily: "Daily",
  weekly: "Weekly",
  monthly: "Monthly",
  custom: "Custom"
}

export function TaskCard({ task, onComplete, onEdit, onDelete }: TaskCardProps) {
  const isDueSoon = task.due_date && !task.completed &&
    new Date(task.due_date) < new Date(Date.now() + 24 * 60 * 60 * 1000)

  const isOverdue = task.due_date && !task.completed &&
    new Date(task.due_date) < new Date()

  const formatDueDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = date.getTime() - now.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return "Today"
    if (days === 1) return "Tomorrow"
    if (days === -1) return "Yesterday"
    if (days > 1) return `In ${days} days`
    if (days < -1) return `${Math.abs(days)} days ago`

    return date.toLocaleDateString()
  }

  return (
    <div className={`rounded-lg border border-border bg-card p-4 shadow-sm transition-all hover:shadow-md ${
      task.completed ? "opacity-60" : ""
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1">
          <h3 className={`text-lg font-medium ${task.completed ? "line-through text-muted-foreground" : "text-foreground"}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
          )}
        </div>

        {/* Complete Checkbox */}
        {onComplete && (
          <button
            onClick={() => onComplete(task.id)}
            className={`flex-shrink-0 w-6 h-6 rounded border-2 transition-colors ${
              task.completed
                ? "bg-primary border-primary"
                : "border-input hover:border-primary"
            }`}
            aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
          >
            {task.completed && (
              <svg className="w-full h-full text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>
        )}
      </div>

      {/* Metadata Row */}
      <div className="flex flex-wrap items-center gap-2 mt-3">
        {/* Priority Badge */}
        {task.priority && (
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${priorityStyles[task.priority]}`}>
            <AlertCircle className="w-3 h-3 mr-1" />
            {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
          </span>
        )}

        {/* Tags */}
        {task.tags && task.tags.length > 0 && (
          <div className="flex items-center gap-1">
            <Tag className="w-3 h-3 text-muted-foreground" />
            {task.tags.map(tag => (
              <span
                key={tag}
                className="inline-flex px-2 py-1 rounded text-xs bg-secondary text-secondary-foreground"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Due Date */}
        {task.due_date && (
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${
            isOverdue
              ? "bg-destructive/20 text-destructive font-medium"
              : isDueSoon
              ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
              : "bg-muted text-muted-foreground"
          }`}>
            <Calendar className="w-3 h-3 mr-1" />
            {formatDueDate(task.due_date)}
          </span>
        )}

        {/* Recurrence */}
        {task.recurrence && (
          <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-primary/10 text-primary">
            <Repeat className="w-3 h-3 mr-1" />
            {recurrenceLabels[task.recurrence]}
            {task.recurrence === "custom" && task.recurrence_interval && ` (${task.recurrence_interval}d)`}
          </span>
        )}
      </div>

      {/* Actions */}
      {(onEdit || onDelete) && (
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border">
          {onEdit && (
            <button
              onClick={() => onEdit(task)}
              className="text-sm text-primary hover:text-primary/80 transition-colors"
            >
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              className="text-sm text-destructive hover:text-destructive/80 transition-colors"
            >
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  )
}
