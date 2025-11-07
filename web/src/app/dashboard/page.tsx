import { Metadata } from 'next';
import { useOrder, useBenchmarkJob } from '@/hooks/use-api';
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
  Play,
  Pause,
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
    createdAt: '2025-11-06T09:30:00Z',
    progress: 65,
    domain: 'climate change',
    estimatedTokens: 800000
  },
  {
    id: 'order_001',
    type: 'production',
    status: 'processing',
    createdAt: '2025-11-06T08:00:00Z',
    progress: 45,
    domain: 'medical research',
    estimatedTokens: 50000000
  }
];

export const metadata: Metadata = {
  title: 'Dashboard - FineData',
  description: 'Monitor your dataset processing tasks and view system status.',
};

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
      case 'running':
      case 'processing':
        return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
      case 'ready':
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
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
      running: 'secondary',
      processing: 'secondary',
      ready: 'default',
      completed: 'default',
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
                <Activity className="h-8 w-8 text-blue-500/70" />
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
                <CheckCircle className="h-8 w-8 text-green-500/70" />
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
                <XCircle className="h-8 w-8 text-red-500/70" />
              </div>
            </div>
          </GradientCard>
        </div>

        {/* Tasks Table */}
        <GradientCard>
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Recent Tasks</h2>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-medium">Task ID</th>
                    <th className="text-left py-3 px-4 font-medium">Type</th>
                    <th className="text-left py-3 px-4 font-medium">Status</th>
                    <th className="text-left py-3 px-4 font-medium">Progress</th>
                    <th className="text-left py-3 px-4 font-medium">Domain</th>
                    <th className="text-left py-3 px-4 font-medium">Created</th>
                    <th className="text-left py-3 px-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {mockTasks.map((task) => (
                    <tr key={task.id} className="border-b border-border/50 hover:bg-accent/5">
                      <td className="py-4 px-4">
                        <code className="text-sm bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                          {task.id}
                        </code>
                      </td>
                      <td className="py-4 px-4">
                        <Badge variant="outline">
                          {task.type === 'benchmark' ? 'Benchmark' : 'Production'}
                        </Badge>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(task.status)}
                          {getStatusBadge(task.status)}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full transition-all duration-300"
                              style={{ width: `${task.progress}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-foreground/70">
                            {task.progress}%
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className="text-sm">{task.domain}</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className="text-sm text-foreground/70">
                          {formatDate(task.createdAt)}
                        </span>
                      </td>
                      <td className="py-4 px-4">
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
        </GradientCard>

        {/* Activity Chart Placeholder */}
        <GradientCard className="mt-8">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-6">24h Activity</h2>
            <div className="h-64 flex items-center justify-center bg-slate-50 dark:bg-slate-900 rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-600">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-500">Activity chart will be implemented</p>
                <p className="text-sm text-slate-400 mt-1">
                  Shows task creation and completion trends
                </p>
              </div>
            </div>
          </div>
        </GradientCard>
      </div>
    </div>
  );
