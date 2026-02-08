// [Task T030] Root layout for Next.js 16 App Router with theme provider
// [Task T049] Add NotificationProvider for real-time WebSocket notifications

import type { Metadata } from "next";
import Link from "next/link";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { SessionProvider } from "@/components/providers/session-provider";
import { NotificationProvider } from "@/components/providers/notification-provider";
import { NotificationBell } from "@/components/notification-bell";
import { ThemeToggle } from "@/components/theme-toggle";
import "./globals.css";

export const metadata: Metadata = {
  title: "Todo App - AI-Powered Task Management",
  description: "Fullstack todo application with AI chat assistant, JWT auth, and event-driven architecture",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <SessionProvider>
            <NotificationProvider>
            <nav className="bg-background shadow-sm border-b border-border">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                  <div className="flex items-center space-x-8">
                    <Link href="/" className="text-xl font-bold text-primary">
                      Todo App
                    </Link>
                    <div className="hidden sm:flex sm:space-x-4">
                      <Link
                        href="/dashboard"
                        className="text-foreground/70 hover:text-foreground px-3 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        Dashboard
                      </Link>
                      <Link
                        href="/tasks"
                        className="text-foreground/70 hover:text-foreground px-3 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        Tasks
                      </Link>
                      <Link
                        href="/chat"
                        className="text-foreground/70 hover:text-foreground px-3 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        AI Chat
                      </Link>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <NotificationBell />
                    <ThemeToggle />
                  </div>
                </div>
              </div>
            </nav>
            {children}
            </NotificationProvider>
          </SessionProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
