// [Task T072] Filter panel with dropdowns for status, priority, tags, date range
// [UX Refinement] Connected to Zustand store for state management

"use client";

import * as React from "react";
import { useState } from "react";
import { Filter, X } from "lucide-react";
import { useFilterStore } from "@/stores/filter-store";

export interface FilterState {
  status: "all" | "pending" | "completed";
  priority: "all" | "high" | "medium" | "low";
  tags: string[];
  dueStart: string;
  dueEnd: string;
}

interface FilterPanelProps {
  availableTags?: string[];
}

export function FilterPanel({ availableTags = [] }: FilterPanelProps) {
  const [showFilters, setShowFilters] = useState(false);

  // Connect to Zustand store
  const {
    status,
    priority,
    tags,
    dueStart,
    dueEnd,
    setStatus,
    setPriority,
    setTags,
    setDueStart,
    setDueEnd,
    clearFilters,
    hasActiveFilters,
  } = useFilterStore();

  const handleStatusChange = (value: string) => {
    setStatus(value as "all" | "pending" | "completed");
  };

  const handlePriorityChange = (value: string) => {
    setPriority(value as "all" | "high" | "medium" | "low");
  };

  const handleTagToggle = (tag: string) => {
    const newTags = tags.includes(tag)
      ? tags.filter((t) => t !== tag)
      : [...tags, tag];
    setTags(newTags);
  };

  const handleClearFilters = () => {
    clearFilters();
  };

  return (
    <div className="w-full">
      {/* Filter Toggle Button */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
        >
          <Filter className="w-4 h-4" />
          <span className="font-medium">Filters</span>
          {hasActiveFilters() && (
            <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold rounded-full bg-indigo-600 text-white">
              !
            </span>
          )}
        </button>

        {/* Clear Filters Button */}
        {hasActiveFilters() && (
          <button
            onClick={handleClearFilters}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <X className="w-4 h-4" />
            Clear Filters
          </button>
        )}
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="p-4 rounded-lg border border-gray-200 bg-gray-50 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Status Filter */}
            <div className="space-y-2">
              <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700">
                Status
              </label>
              <select
                id="status-filter"
                value={status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div className="space-y-2">
              <label htmlFor="priority-filter" className="block text-sm font-medium text-gray-700">
                Priority
              </label>
              <select
                id="priority-filter"
                value={priority}
                onChange={(e) => handlePriorityChange(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="all">All Priorities</option>
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="low">Low Priority</option>
              </select>
            </div>

            {/* Due Start Date */}
            <div className="space-y-2">
              <label htmlFor="due-start" className="block text-sm font-medium text-gray-700">
                Due From
              </label>
              <input
                type="date"
                id="due-start"
                value={dueStart}
                onChange={(e) => setDueStart(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Due End Date */}
            <div className="space-y-2">
              <label htmlFor="due-end" className="block text-sm font-medium text-gray-700">
                Due Until
              </label>
              <input
                type="date"
                id="due-end"
                value={dueEnd}
                onChange={(e) => setDueEnd(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Tags Filter (if available) */}
          {availableTags.length > 0 && (
            <div className="space-y-2 pt-2 border-t border-gray-200">
              <label className="block text-sm font-medium text-gray-700">Filter by Tags</label>
              <div className="flex flex-wrap gap-2">
                {availableTags.map((tag) => {
                  const isSelected = tags.includes(tag);
                  return (
                    <button
                      key={tag}
                      onClick={() => handleTagToggle(tag)}
                      className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                        isSelected
                          ? "bg-indigo-600 text-white hover:bg-indigo-700"
                          : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
                      }`}
                    >
                      {tag}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
