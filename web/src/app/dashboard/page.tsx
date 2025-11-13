"use client";

import { GradientCard } from '@/components/ui/gradient-card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useDashboardStats, useBenchmarkJobs, useSystemStats, useAuth } from '@/hooks/use-api';
import {
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  TrendingUp,
  Database,
  RefreshCw
} from 'lucide-react';

// Mock data for development - in real app, aggregate from API calls
const mockTasks = [
  {
    id: 'bench_001',
    type: 'benchmark',
    status: 'ready',
    createdAt: '2025-11-06T09:00:00Z',
    progress: 100,
    domain: 'artificial intelligence',
    estimatedTokens: 1000000
  },
  {
    id: 'bench_002',
    type: 'benchmark',
    status: 'running',
    createdAt: '2025-11-06T10:00:00Z',
    progress: 65,
    domain: 'climate change',
    estimatedTokens: 500000
  },
  {
    id: 'prod_001',
    type: 'production',
    status: 'processing',
    createdAt: '2025-11-06T08:00:00Z',
    progress: 30,
    domain: 'medical research',
    estimatedTokens: 5000000
  },
  {
    id: 'bench_003',
    type: 'benchmark',
    status: 'failed',
    createdAt: '2025-11-06T07:00:00Z',
    progress: 20,
    domain: 'financial markets',
    estimatedTokens: 200000
  }
];

export default function DashboardPage() {
  const { data: stats, isLoading } = useDashboardStats();
  const { data: jobs, isLoading: jobsLoading } = useBenchmarkJobs(50);
  const systemStats = useSystemStats();
  const { isAuthenticated, login } = useAuth();

  // Fallback stats while loading
  const displayStats = stats || {
    activeTasks: 0,
    runningTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    avgCompletionTime: '0h'
  };

  // Use system stats if available
  const systemDisplayStats = systemStats ? {
    activeTasks: systemStats.totalTasks,
    runningTasks: systemStats.activeBenchmarks + systemStats.activeOrders,
    completedTasks: systemStats.completedBenchmarks,
    failedTasks: 0, // TODO: Add failed tasks count
    avgCompletionTime: '2.5h' // Placeholder
  } : displayStats;

  // Display benchmark jobs
  const allTasks = jobs || [];

  if (!isAuthenticated) {
    return (
      <div className="text-center py-16">
        <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
        <p className="text-muted-foreground mb-8 max-w-md mx-auto">
          Please sign in to view your dataset processing tasks and system status.
        </p>
        <Button onClick={login} size="lg">
          Sign In to Continue
        </Button>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'running':
      case 'processing':
        return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'queued':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      ready: 'default',
      completed: 'default',
      running: 'secondary',
      processing: 'secondary',
      failed: 'destructive',
      queued: 'outline'
    } as const;

    return (
      <Badge variant={variants[status as keyof typeof variants] || 'outline'}>
        {status}
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-foreground/70">
          Monitor your dataset processing tasks and system status.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <GradientCard>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-primary">{systemDisplayStats.activeTasks}</p>
                <p className="text-sm text-foreground/70">Active Tasks</p>
              </div>
              <Database className="h-8 w-8 text-primary/70" />
            </div>
          </div>
        </GradientCard>

        <GradientCard>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-blue-600">{systemDisplayStats.runningTasks}</p>
                <p className="text-sm text-foreground/70">Running</p>
              </div>
              <Activity className="h-8 w-8 text-blue-600/70" />
            </div>
          </div>
        </GradientCard>

        <GradientCard>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-green-600">{systemDisplayStats.completedTasks}</p>
                <p className="text-sm text-foreground/70">Completed</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600/70" />
            </div>
          </div>
        </GradientCard>

        <GradientCard>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-amber-600">{systemDisplayStats.avgCompletionTime}</p>
                <p className="text-sm text-foreground/70">Avg. Completion</p>
              </div>
              <Clock className="h-8 w-8 text-amber-600/70" />
            </div>
          </div>
        </GradientCard>
      </div>

      {/* Tasks Table */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Recent Tasks</h2>
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">ID</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Type</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Progress</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Domain</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Created</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {jobsLoading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                    Loading tasks...
                  </td>
                </tr>
              ) : allTasks && allTasks.length > 0 ? (
                allTasks.map((job: any) => (
                  <tr key={job.id} className="hover:bg-muted/30">
                    <td className="px-4 py-3 text-sm font-mono">{job.id.slice(0, 16)}...</td>
                    <td className="px-4 py-3 text-sm capitalize">benchmark</td>
                    <td className="px-4 py-3">
                      {getStatusBadge(job.status)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress?.pct || 0}%` }}
                          />
                        </div>
                        <span className="text-sm text-muted-foreground">{job.progress?.pct || 0}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {job.domain || 'Unknown Domain'}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {job.created_at ? formatDate(job.created_at) : 'Unknown'}
                    </td>
                    <td className="px-4 py-3">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(`/preview/${job.id}`, '_blank')}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                    No tasks found. Create your first benchmark job to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Activity Chart Placeholder */}
      <div>
        <h2 className="text-xl font-semibold mb-6">24h Activity</h2>
        <GradientCard>
          <div className="p-8 text-center">
            <TrendingUp className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-500">Activity chart will be implemented</p>
            <p className="text-sm text-slate-400 mt-1">
              Shows task creation and completion trends
            </p>
          </div>
        </GradientCard>
      </div>
    </div>
  );
}
