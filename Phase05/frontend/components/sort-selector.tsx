// [Task T079] Sort selector component with dropdown for sort options and direction toggle

"use client";

import * as React from "react";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

export type SortBy = "created" | "due_date" | "priority" | "title";
export type SortOrder = "asc" | "desc";

export interface SortState {
  sortBy: SortBy;
  sortOrder: SortOrder;
}

interface SortSelectorProps {
  sortBy: SortBy;
  sortOrder: SortOrder;
  onSortChange: (sortBy: SortBy, sortOrder: SortOrder) => void;
}

const sortOptions: { value: SortBy; label: string }[] = [
  { value: "created", label: "Created Date" },
  { value: "due_date", label: "Due Date" },
  { value: "priority", label: "Priority" },
  { value: "title", label: "Alphabetical" },
];

export function SortSelector({ sortBy, sortOrder, onSortChange }: SortSelectorProps) {
  const handleSortByChange = (newSortBy: SortBy) => {
    onSortChange(newSortBy, sortOrder);
  };

  const handleToggleSortOrder = () => {
    const newOrder = sortOrder === "asc" ? "desc" : "asc";
    onSortChange(sortBy, newOrder);
  };

  return (
    <div className="flex items-center gap-2">
      {/* Sort By Dropdown */}
      <div className="flex items-center gap-2">
        <label htmlFor="sort-by" className="text-sm font-medium text-gray-700">
          Sort by:
        </label>
        <select
          id="sort-by"
          value={sortBy}
          onChange={(e) => handleSortByChange(e.target.value as SortBy)}
          className="px-3 py-2 rounded-md border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Sort Order Toggle Button */}
      <button
        onClick={handleToggleSortOrder}
        className="inline-flex items-center justify-center w-10 h-10 rounded-md border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
        aria-label={`Sort ${sortOrder === "asc" ? "ascending" : "descending"}`}
        title={`Click to sort ${sortOrder === "asc" ? "descending" : "ascending"}`}
      >
        {sortOrder === "asc" ? (
          <ArrowUp className="w-4 h-4" />
        ) : (
          <ArrowDown className="w-4 h-4" />
        )}
      </button>
    </div>
  );
}
