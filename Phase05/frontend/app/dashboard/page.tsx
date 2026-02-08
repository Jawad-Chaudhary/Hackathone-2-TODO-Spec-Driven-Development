// [Task T088] Dashboard page with stats grid
// [Task T089-T091] Calendar view with task integration
// [Task T094] Framer Motion page transitions

"use client";

import { useEffect, useState } from "react";
import { useSession } from "@/components/providers/session-provider";
import { StatCard } from "@/components/dashboard/stat-card";
import { CalendarView } from "@/components/dashboard/calendar-view";
import { PageTransition } from "@/components/page-transition";
import { CheckCircle2, Circle, ListTodo, AlertCircle } from "lucide-react";
import { getDashboardStats, DashboardStats, getTasks } from "@/lib/api";
import { Task } from "@/lib/types";

export default function DashboardPage() {
  const { session, loading: sessionLoading } = useSession();
  const [stats, setStats] = useState<DashboardStats>({
    total: 0,
    completed: 0,
    pending: 0,
    overdue: 0,
  });
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      const userId = session?.user?.id;

      if (!userId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        // Fetch stats and tasks in parallel
        const [statsData, tasksData] = await Promise.all([
          getDashboardStats(userId),
          getTasks(userId),
        ]);

        setStats(statsData);
        setTasks(tasksData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    }

    if (!sessionLoading && session) {
      fetchDashboardData();
    }
  }, [session, sessionLoading]);

  if (sessionLoading || loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          <p className="font-medium">Error loading dashboard</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Tasks"
          value={stats.total}
          icon={ListTodo}
          color="gray"
        />
        <StatCard
          title="Completed"
          value={stats.completed}
          icon={CheckCircle2}
          color="green"
        />
        <StatCard
          title="Pending"
          value={stats.pending}
          icon={Circle}
          color="blue"
        />
        <StatCard
          title="Overdue"
          value={stats.overdue}
          icon={AlertCircle}
          color="red"
        />
      </div>

      {/* Calendar View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CalendarView tasks={tasks} />
        </div>
      </div>
    </PageTransition>
  );
}
