// [Task T087] Stat card component for dashboard statistics

import { Card } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  color?: "blue" | "green" | "yellow" | "red" | "gray";
}

const colorClasses = {
  blue: "text-blue-600 bg-blue-50",
  green: "text-green-600 bg-green-50",
  yellow: "text-yellow-600 bg-yellow-50",
  red: "text-red-600 bg-red-50",
  gray: "text-gray-600 bg-gray-50",
};

export function StatCard({ title, value, icon: Icon, color = "gray" }: StatCardProps) {
  const colorClass = colorClasses[color];

  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex flex-row items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        <div className={`p-2 rounded-lg ${colorClass}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
    </Card>
  );
}
