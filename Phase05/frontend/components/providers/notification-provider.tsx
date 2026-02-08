// [Task T048] Notification provider for WebSocket real-time updates

"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { NotificationWebSocket, NotificationMessage } from "@/lib/websocket";

interface NotificationContextType {
  isConnected: boolean;
  notifications: NotificationMessage[];
  connect: (userId: string) => void;
  disconnect: () => void;
  clearNotifications: () => void;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [wsClient, setWsClient] = useState<NotificationWebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);

  const handleNotification = useCallback((message: NotificationMessage) => {
    console.log("Notification received:", message);

    // Add to notifications list (keep last 50)
    setNotifications((prev) => [message, ...prev].slice(0, 50));

    // Show browser notification for reminders
    if (message.type === "reminder" && "Notification" in window) {
      if (Notification.permission === "granted") {
        new Notification("Task Reminder", {
          body: message.message || `"${message.title}" is due soon!`,
          icon: "/favicon.ico",
          tag: `task-${message.task_id}`,
        });
      }
    }

    // Update connection status
    if (message.type === "connected") {
      setIsConnected(true);
    }
  }, []);

  const connect = useCallback(
    (userId: string) => {
      if (wsClient) {
        wsClient.disconnect();
      }

      try {
        const client = new NotificationWebSocket(userId);
        client.addHandler(handleNotification);
        client.connect();
        setWsClient(client);
      } catch (error) {
        // Silently fail - WebSocket is optional for development
        console.warn("WebSocket connection skipped:", error);
      }
    },
    [handleNotification]
  );

  const disconnect = useCallback(() => {
    if (wsClient) {
      wsClient.disconnect();
      setWsClient(null);
      setIsConnected(false);
    }
  }, [wsClient]);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Request notification permission on mount
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission().then((permission) => {
        console.log("Notification permission:", permission);
      });
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsClient) {
        wsClient.disconnect();
      }
    };
  }, [wsClient]);

  return (
    <NotificationContext.Provider
      value={{
        isConnected,
        notifications,
        connect,
        disconnect,
        clearNotifications,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

/**
 * Hook to use notifications context.
 */
export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotifications must be used within NotificationProvider");
  }
  return context;
}
