"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { Activity, CheckCircle, Clock, XCircle, Eye, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GradientCard } from "@/components/ui/gradient-card";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

// Mock data - in real app, aggregate from React Query cache
const mockTasks = [
  {
    id: "job_001",
    type: "benchmark",
    status: "completed",
    createdAt: "2025-11-06T10:00:00Z",
    progress: 100,
    metrics: { coverage: 0.85, quality_pass_rate: 0.92 }
  },
  {
    id: "job_002",
    type: "benchmark",
    status: "running",
    createdAt: "2025-11-06T11:00:00Z",
    progress: 65,
  },
  {
    id: "order_001",
    type: "production",
    status: "processing",
    createdAt: "2025-11-06T09:00:00Z",
    progress: 30,
  }
];

export default function DashboardPage() {
  const { t } = useI18n();

  const stats = useMemo(() => {
    const running = mockTasks.filter(t => t.status === 'running').length;
    const queued = mockTasks.filter(t => t.status === 'queued').length;
    const completed = mockTasks.filter(t => t.status === 'completed').length;
    const failed = mockTasks.filter(t => t.status === 'failed').length;

    return { running, queued, completed, failed, total: mockTasks.length };
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Activity className="w-4 h-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      running: 'default',
      completed: 'default',
      failed: 'destructive',
      queued: 'secondary'
    } as const;

    return (
      <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>
        {status}
      </Badge>
    );
  };

  return (
    <div className="py-16 md:py-24">
      <div className="mb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            Dashboard
          </h1>
          <p className="text-xl text-foreground/70">
            Monitor your dataset creation tasks and production jobs
          </p>
        </motion.div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-12">
        {[
          { label: 'Running', value: stats.running, color: 'text-blue-600' },
          { label: 'Queued', value: stats.queued, color: 'text-yellow-600' },
          { label: 'Completed', value: stats.completed, color: 'text-green-600' },
          { label: 'Failed', value: stats.failed, color: 'text-red-600' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <GradientCard>
              <div className="text-center">
                <div className={`text-3xl font-bold mb-2 ${stat.color}`}>
                  {stat.value}
                </div>
                <div className="text-sm text-foreground/70">{stat.label}</div>
              </div>
            </GradientCard>
          </motion.div>
        ))}
      </div>

      {/* Tasks Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <GradientCard>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold">Recent Tasks</h2>
            <Button asChild variant="outline">
              <Link href="/new">
                New Task
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="text-left py-3 px-4 font-medium">Task ID</th>
                  <th className="text-left py-3 px-4 font-medium">Type</th>
                  <th className="text-left py-3 px-4 font-medium">Status</th>
                  <th className="text-left py-3 px-4 font-medium">Progress</th>
                  <th className="text-left py-3 px-4 font-medium">Created</th>
                  <th className="text-left py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mockTasks.map((task) => (
                  <tr key={task.id} className="border-b border-slate-100 dark:border-slate-800">
                    <td className="py-3 px-4 font-mono text-sm">{task.id}</td>
                    <td className="py-3 px-4">
                      <Badge variant="outline">
                        {task.type === 'benchmark' ? 'Benchmark' : 'Production'}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(task.status)}
                        {getStatusBadge(task.status)}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {task.progress !== undefined ? (
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full transition-all duration-300"
                              style={{ width: `${task.progress}%` }}
                            />
                          </div>
                          <span className="text-sm">{task.progress}%</span>
                        </div>
                      ) : (
                        <span className="text-sm text-foreground/50">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-sm text-foreground/70">
                      {new Date(task.createdAt).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <Button asChild variant="ghost" size="sm">
                        <Link href={task.type === 'benchmark' ? `/preview/${task.id}` : `/orders/${task.id}`}>
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Link>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GradientCard>
      </motion.div>

      {/* Empty State */}
      {mockTasks.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center py-12"
        >
          <div className="max-w-md mx-auto">
            <Activity className="w-16 h-16 text-foreground/30 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No tasks yet</h3>
            <p className="text-foreground/70 mb-6">
              Create your first dataset to see it appear here.
            </p>
            <Button asChild>
              <Link href="/new">
                Create Dataset
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
