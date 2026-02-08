// Session provider with caching to prevent excessive API calls

"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { getSession, SessionData } from "@/lib/session";

interface SessionContextType {
  session: SessionData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

const SessionContext = createContext<SessionContextType | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<number>(0);

  const fetchSession = useCallback(async (force = false) => {
    // Prevent fetching if we fetched within the last 5 seconds (unless forced)
    const now = Date.now();
    if (!force && lastFetch && (now - lastFetch) < 5000) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getSession();
      setSession(data);
      setLastFetch(now);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch session");
    } finally {
      setLoading(false);
    }
  }, [lastFetch]);

  // Initial fetch on mount
  useEffect(() => {
    fetchSession();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const refetch = useCallback(async () => {
    await fetchSession(true);
  }, [fetchSession]);

  return (
    <SessionContext.Provider
      value={{
        session,
        loading,
        error,
        refetch,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

/**
 * Hook to use session context with caching.
 */
export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error("useSession must be used within SessionProvider");
  }
  return context;
}
