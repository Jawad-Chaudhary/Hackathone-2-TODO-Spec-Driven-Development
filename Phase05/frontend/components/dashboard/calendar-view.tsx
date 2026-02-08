// [Task T089] Calendar view component showing tasks on their due dates
// [Task T090] Fetch tasks for current month and render dots on dates with tasks
// [Task T091] Add date click handler to show tasks due on that date

"use client";

import { useState, useEffect } from "react";
import { Calendar } from "@/components/ui/calendar";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Task } from "@/lib/types";
import { format, isSameDay, startOfMonth, endOfMonth } from "date-fns";

interface CalendarViewProps {
  tasks: Task[];
}

export function CalendarView({ tasks }: CalendarViewProps) {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [showTasksDialog, setShowTasksDialog] = useState(false);
  const [tasksForSelectedDate, setTasksForSelectedDate] = useState<Task[]>([]);

  // Get tasks with due dates
  const tasksWithDueDates = tasks.filter((task) => task.due_date);

  // Get dates that have tasks
  const datesWithTasks = new Set(
    tasksWithDueDates.map((task) => format(new Date(task.due_date!), "yyyy-MM-dd"))
  );

  // Handle date selection
  const handleDateSelect = (date: Date | undefined) => {
    if (!date) return;

    setSelectedDate(date);

    // Find tasks for this date
    const tasksOnDate = tasksWithDueDates.filter((task) =>
      isSameDay(new Date(task.due_date!), date)
    );

    if (tasksOnDate.length > 0) {
      setTasksForSelectedDate(tasksOnDate);
      setShowTasksDialog(true);
    }
  };

  // Custom day content to show dots for tasks
  const modifiers = {
    hasTasks: (date: Date) => datesWithTasks.has(format(date, "yyyy-MM-dd")),
  };

  const modifiersStyles = {
    hasTasks: {
      fontWeight: "bold",
      position: "relative" as const,
    },
  };

  return (
    <Card>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Calendar</h3>

        <div className="flex justify-center">
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={handleDateSelect}
            modifiers={modifiers}
            modifiersStyles={modifiersStyles}
            className="rounded-md border"
          />
        </div>

        <div className="mt-4 text-sm text-gray-600">
          <p className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-full bg-indigo-500"></span>
            Dates with tasks are shown in bold
          </p>
        </div>
      </div>

      {/* Dialog to show tasks for selected date */}
      <Dialog open={showTasksDialog} onOpenChange={setShowTasksDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              Tasks for {selectedDate && format(selectedDate, "MMMM d, yyyy")}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {tasksForSelectedDate.length === 0 ? (
              <p className="text-sm text-gray-500">No tasks for this date</p>
            ) : (
              tasksForSelectedDate.map((task) => (
                <div
                  key={task.id}
                  className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{task.title}</h4>
                      {task.description && (
                        <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        {task.priority && (
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              task.priority === "high"
                                ? "bg-red-100 text-red-800"
                                : task.priority === "medium"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-blue-100 text-blue-800"
                            }`}
                          >
                            {task.priority}
                          </span>
                        )}
                        {task.completed && (
                          <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800">
                            Completed
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
