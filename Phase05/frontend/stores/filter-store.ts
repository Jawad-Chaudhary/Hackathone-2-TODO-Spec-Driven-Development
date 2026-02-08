// [Task T073] Zustand store for managing active filters state
// [Task T081] Added sort state for User Story 5

import { create } from "zustand";

export type SortBy = "created" | "due_date" | "priority" | "title";
export type SortOrder = "asc" | "desc";

export interface FilterState {
  // Search
  search: string;

  // Status
  status: "all" | "pending" | "completed";

  // Priority
  priority: "all" | "high" | "medium" | "low";

  // Tags
  tags: string[];

  // Date range
  dueStart: string;
  dueEnd: string;

  // [Task T081] Sort state
  sortBy: SortBy;
  sortOrder: SortOrder;
}

interface FilterStore extends FilterState {
  // Actions
  setSearch: (search: string) => void;
  setStatus: (status: FilterState["status"]) => void;
  setPriority: (priority: FilterState["priority"]) => void;
  setTags: (tags: string[]) => void;
  setDueStart: (date: string) => void;
  setDueEnd: (date: string) => void;
  setFilters: (filters: Partial<FilterState>) => void;
  clearFilters: () => void;

  // [Task T081] Sort actions
  setSortBy: (sortBy: SortBy) => void;
  setSortOrder: (sortOrder: SortOrder) => void;
  setSort: (sortBy: SortBy, sortOrder: SortOrder) => void;

  // Computed
  hasActiveFilters: () => boolean;
}

const initialState: FilterState = {
  search: "",
  status: "all",
  priority: "all",
  tags: [],
  dueStart: "",
  dueEnd: "",
  // [Task T081] Sort defaults - newest first
  sortBy: "created",
  sortOrder: "desc",
};

export const useFilterStore = create<FilterStore>((set, get) => ({
  ...initialState,

  setSearch: (search) => set({ search }),
  setStatus: (status) => set({ status }),
  setPriority: (priority) => set({ priority }),
  setTags: (tags) => set({ tags }),
  setDueStart: (dueStart) => set({ dueStart }),
  setDueEnd: (dueEnd) => set({ dueEnd }),

  setFilters: (filters) => set((state) => ({ ...state, ...filters })),

  clearFilters: () => set(initialState),

  // [Task T081] Sort actions
  setSortBy: (sortBy) => set({ sortBy }),
  setSortOrder: (sortOrder) => set({ sortOrder }),
  setSort: (sortBy, sortOrder) => set({ sortBy, sortOrder }),

  hasActiveFilters: () => {
    const state = get();
    return (
      state.search !== "" ||
      state.status !== "all" ||
      state.priority !== "all" ||
      state.tags.length > 0 ||
      state.dueStart !== "" ||
      state.dueEnd !== ""
    );
  },
}));
