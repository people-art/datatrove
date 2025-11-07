"use client";

import { GradientCard } from '@/components/ui/gradient-card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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
  // In a real app, you'd aggregate data from multiple queries
  const stats = {
    total: mockTasks.length,
    running: mockTasks.filter(t => t.status === 'running' || t.status === 'processing').length,
    completed: mockTasks.filter(t => t.status === 'ready' || t.status === 'completed').length,
    failed: mockTasks.filter(t => t.status === 'failed').length
  };

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
                <p className="text-2xl font-bold text-primary">{stats.total}</p>
                <p className="text-sm text-foreground/70">Total Tasks</p>
              </div>
              <Database className="h-8 w-8 text-primary/70" />
            </div>
          </div>
        </GradientCard>

        <GradientCard>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-blue-600">{stats.running}</p>
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
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
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
                <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
                <p className="text-sm text-foreground/70">Failed</p>
              </div>
              <XCircle className="h-8 w-8 text-red-600/70" />
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
              {mockTasks.map((task) => (
                <tr key={task.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 text-sm font-mono">{task.id}</td>
                  <td className="px-4 py-3 text-sm capitalize">{task.type}</td>
                  <td className="px-4 py-3">
                    {getStatusBadge(task.status)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground">{task.progress}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">{task.domain}</td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {formatDate(task.createdAt)}
                  </td>
                  <td className="px-4 py-3">
                    <Button variant="ghost" size="sm">
                      View
                    </Button>
                  </td>
                </tr>
              ))}
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
