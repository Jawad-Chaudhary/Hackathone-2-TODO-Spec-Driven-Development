// [Task T036] Task form component with recurrence, priority, tags, and due date

"use client"

import * as React from "react"
import { useState } from "react"

interface TaskFormProps {
  onSubmit: (taskData: TaskFormData) => void
  initialData?: Partial<TaskFormData>
  submitLabel?: string
}

export interface TaskFormData {
  title: string
  description?: string
  priority?: "high" | "medium" | "low"
  tags?: string[]
  due_date?: string
  recurrence?: "daily" | "weekly" | "monthly" | "custom"
  recurrence_interval?: number
}

export function TaskForm({ onSubmit, initialData, submitLabel = "Create Task" }: TaskFormProps) {
  const [formData, setFormData] = useState<TaskFormData>({
    title: initialData?.title || "",
    description: initialData?.description || "",
    priority: initialData?.priority,
    tags: initialData?.tags || [],
    due_date: initialData?.due_date || "",
    recurrence: initialData?.recurrence,
    recurrence_interval: initialData?.recurrence_interval
  })

  const [tagInput, setTagInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title.trim()) return
    onSubmit(formData)
  }

  const addTag = () => {
    if (tagInput.trim() && !formData.tags?.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), tagInput.trim()]
      }))
      setTagInput("")
    }
  }

  const removeTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(t => t !== tag) || []
    }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Title */}
      <div className="space-y-2">
        <label htmlFor="title" className="text-sm font-medium text-foreground">
          Title <span className="text-destructive">*</span>
        </label>
        <input
          id="title"
          type="text"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="Task title"
          required
        />
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label htmlFor="description" className="text-sm font-medium text-foreground">
          Description
        </label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring min-h-[100px]"
          placeholder="Task description (optional)"
        />
      </div>

      {/* Priority */}
      <div className="space-y-2">
        <label htmlFor="priority" className="text-sm font-medium text-foreground">
          Priority
        </label>
        <select
          id="priority"
          value={formData.priority || ""}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            priority: e.target.value as "high" | "medium" | "low" | undefined
          }))}
          className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">No priority</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <label htmlFor="tags" className="text-sm font-medium text-foreground">
          Tags
        </label>
        <div className="flex gap-2">
          <input
            id="tags"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault()
                addTag()
              }
            }}
            className="flex-1 px-3 py-2 rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Add a tag and press Enter"
          />
          <button
            type="button"
            onClick={addTag}
            className="px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
          >
            Add
          </button>
        </div>
        {formData.tags && formData.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {formData.tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary/10 text-primary text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="hover:text-destructive transition-colors"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Due Date */}
      <div className="space-y-2">
        <label htmlFor="due_date" className="text-sm font-medium text-foreground">
          Due Date
        </label>
        <input
          id="due_date"
          type="datetime-local"
          value={formData.due_date}
          onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
          className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      {/* Recurrence */}
      <div className="space-y-2">
        <label htmlFor="recurrence" className="text-sm font-medium text-foreground">
          Recurrence
        </label>
        <select
          id="recurrence"
          value={formData.recurrence || ""}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            recurrence: e.target.value as "daily" | "weekly" | "monthly" | "custom" | undefined
          }))}
          className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">No recurrence</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="custom">Custom interval</option>
        </select>
      </div>

      {/* Custom Recurrence Interval */}
      {formData.recurrence === "custom" && (
        <div className="space-y-2">
          <label htmlFor="recurrence_interval" className="text-sm font-medium text-foreground">
            Repeat every (days)
          </label>
          <input
            id="recurrence_interval"
            type="number"
            min="1"
            value={formData.recurrence_interval || ""}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              recurrence_interval: parseInt(e.target.value) || undefined
            }))}
            className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Number of days"
          />
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!formData.title.trim()}
        className="w-full px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {submitLabel}
      </button>
    </form>
  )
}
