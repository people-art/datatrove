import { useState, useMemo, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/fetcher';
import { getOrCreateIdemKey } from '@/lib/idempotency';

// Types
export interface QuoteRequest {
  domain: string;
  keywords: string[];
  languages: string[];
  startDate: string;
  endDate: string;
  qualityTier: string;
  estimatedScale?: { docs?: number; tokens?: number };
}

// Ontology Types
export interface Ontology {
  summary: string;                    // 对领域的简要说明（段落）
  concepts?: string[];                // 核心概念（简短短语）
  entities?: string[];                // 重要实体/机构/产品名
  intents?: string[];                 // 用户意图/任务类别
  positive_keywords?: string[];       // 建议的正向关键词（用于 pipeline）
  negative_keywords?: string[];       // 建议的排除词（黑名单）
  languages_suggested?: string[];     // 建议语言（如未在表单勾选）
  examples?: Array<{title: string; url?: string}>; // 示例页面或内容标题
  raw?: Record<string, unknown>;          // 原始LLM返回（调试/导出）
}

type GenerateOntologyParams = {
  domain: string;         // 用户输入的领域/主题
  locale?: 'en' | 'zh';   // 跟随 UI 语言
};

export interface QuoteResponse {
  quoteId: string;
  currency: string;
  estimate: { low: number; high: number };
  unit: { basis: string; amount: number };
  expiresAt: string;
}

export interface BenchmarkJobCreateRequest {
  domain: string;
  keywords: string[];
  languages: string[];
  time_range: { start: string; end: string };
  quality_tier: string;
  estimated_scale?: string | number;
  email: string;
}

export interface BenchmarkJobResponse {
  id: string;
  status: string;
  progress?: {
    pct: number;
    docs_read: number;
    docs_kept: number;
    tokens: number;
    dedup_rate: number;
  };
  metrics?: {
    coverage: number;
    quality_pass_rate: number;
    pii_rate: number;
    toxicity_rate: number;
    lang_dist: Record<string, number>;
    domain_dist: Record<string, number>;
  };
  sample_url?: string;
  suggested_params?: Record<string, unknown>;
  error?: string;
}

export interface OrderCreateRequest {
  quoteId: string;
  jobId: string;
  email: string;
}

export interface OrderCreateResponse {
  orderId: string;
  provider: string;
  clientSecret: string;
}

export interface OrderResponse {
  id: string;
  status: string;
  timeline: Array<{ timestamp: string; label: string }>;
  live?: Record<string, number>;
  delivery?: Record<string, string | null>;
  error?: string;
}

export interface ProductionStatusResponse {
  status: string;
  estCompleteAt?: string;
  logsUrl?: string;
  error?: string;
}

export interface OrderListResponse {
  id: string;
  status: string;
  domain?: string;
  created_at?: string;
  progress?: {
    fetched_docs: number;
    filtered_docs: number;
    deduped_docs: number;
    final_tokens: number;
  };
  error?: string;
}

export interface EmailValidationResponse {
  email: string;
  isValid: boolean;
  domain: string;
  checks: Record<string, boolean>;
}

// Quote API
export const useQuote = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (body: QuoteRequest) => api.post('/benchmark/quote', body).then(r => r.data),
    onSuccess: (data: QuoteResponse) => {
      qc.setQueryData(['quote', data.quoteId], data);
    },
  });
};

// Benchmark Job API
export const useCreateBenchmarkJob = () => {
  return useMutation({
    mutationFn: (body: BenchmarkJobCreateRequest) =>
      api.post('/benchmark/jobs', body).then(r => r.data),
  });
};

export const useBenchmarkJob = (jobId?: string) => {
  return useQuery({
    queryKey: ['benchmark', jobId],
    queryFn: () => api.get(`/benchmark/jobs/${jobId}`).then(r => r.data),
    enabled: !!jobId,
    refetchInterval: 5000, // Poll every 5 seconds while active
  });
};

// Orders API
export const useCreateOrder = () => {
  return useMutation({
    mutationFn: ({ quoteId, jobId, email }: OrderCreateRequest) => {
      const idempotencyKey = getOrCreateIdemKey('order', `${quoteId}:${jobId}:${email}`);
      return api.post('/orders', { quoteId, jobId, email }, {
        headers: { 'Idempotency-Key': idempotencyKey }
      }).then(r => r.data);
    },
  });
};

export const useOrder = (orderId?: string) => {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: () => api.get(`/orders/${orderId}`).then(r => r.data),
    enabled: !!orderId,
    refetchInterval: 10000, // Poll every 10 seconds for order updates
  });
};

export const useOrders = (limit: number = 50) => {
  return useQuery({
    queryKey: ['orders', limit],
    queryFn: () => api.get(`/orders?limit=${limit}`).then(r => r.data),
    refetchInterval: 5000, // Refresh every 5 seconds for active orders
  });
};

export const useProduction = (orderId?: string) => {
  return useQuery({
    queryKey: ['production', orderId],
    queryFn: () => api.get(`/orders/${orderId}/production`).then(r => r.data),
    enabled: !!orderId,
    refetchInterval: 8000, // Poll every 8 seconds for production updates
  });
};

// Payment API
export const useCreateCheckoutSession = () => {
  return useMutation({
    mutationFn: ({ jobId, plan }: { jobId: string; plan?: string }) =>
      api.post('/checkout/session', { jobId, plan }).then(r => r.data),
  });
};

// Email API
export const useEmailValidation = () => {
  return useMutation({
    mutationFn: (email: string) =>
      api.post('/email/validate', { email }).then(r => r.data),
  });
};

export const useSendVerificationEmail = () => {
  return useMutation({
    mutationFn: (email: string) =>
      api.post('/email/verify/send', { email }).then(r => r.data),
  });
};

export const useConfirmEmailVerification = () => {
  return useMutation({
    mutationFn: (token: string) =>
      api.post('/email/verify/confirm', { token }).then(r => r.data),
  });
};

// Health check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      // Use the API instance for health check - it will handle proxying correctly
      const response = await api.get('/health');
      return response.data;
    },
    refetchInterval: 30000, // Check every 30 seconds
  });
};

// Dashboard stats aggregation hook
export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      // Get benchmark jobs and orders, then aggregate stats
      const [jobsResponse, ordersResponse] = await Promise.all([
        api.get('/benchmark/jobs?limit=100'),
        api.get('/orders?limit=100')
      ]);

      const jobs = jobsResponse.data || [];
      const orders = ordersResponse.data || [];

      const stats = {
        activeTasks: jobs.length + orders.length,
        runningTasks: jobs.filter((job: BenchmarkJobResponse) => job.status === 'running').length +
                     orders.filter((order: OrderListResponse) => ['running', 'cluster_queued', 'finalizing'].includes(order.status)).length,
        completedTasks: jobs.filter((job: BenchmarkJobResponse) => job.status === 'ready').length +
                       orders.filter((order: OrderListResponse) => order.status === 'delivered').length,
        failedTasks: jobs.filter((job: BenchmarkJobResponse) => job.status === 'failed').length +
                    orders.filter((order: OrderListResponse) => order.status === 'failed').length,
        avgCompletionTime: '2.5h' // TODO: Calculate from actual data
      };

      return stats;
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });
};

// Get all benchmark jobs
export const useBenchmarkJobs = (limit: number = 50) => {
  return useQuery({
    queryKey: ['benchmark-jobs', limit],
    queryFn: () => api.get(`/benchmark/jobs?limit=${limit}`).then(r => r.data),
    refetchInterval: 5000, // Refresh every 5 seconds for active jobs
  });
};

// Simple auth hook (mock implementation)
export const useAuth = () => {
  // Mock auth state - in real app, this would integrate with your auth system
  // Start with false on both server and client to avoid hydration mismatch
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load auth state on client side only
  useEffect(() => {
    const stored = localStorage.getItem('fd_demo_user') === 'true';
    setIsAuthenticated(stored);
  }, []);

  return {
    isAuthenticated,
    user: isAuthenticated ? { name: 'Demo User' } : null,
    login: () => {
      localStorage.setItem('fd_demo_user', 'true');
      setIsAuthenticated(true);
    },
    logout: () => {
      localStorage.removeItem('fd_demo_user');
      setIsAuthenticated(false);
    }
  };
};

// System stats hook for homepage
export const useSystemStats = () => {
  // Load tracked job and order IDs from localStorage - use state to avoid hydration mismatch
  const [trackedData, setTrackedData] = useState({ jobIds: [], orderIds: [] });

  useEffect(() => {
    try {
      const jobs = JSON.parse(localStorage.getItem('tracked_jobs') || '[]');
      const orders = JSON.parse(localStorage.getItem('tracked_orders') || '[]');
      setTrackedData({ jobIds: jobs, orderIds: orders });
    } catch {
      setTrackedData({ jobIds: [], orderIds: [] });
    }
  }, []);

  const { jobIds, orderIds } = trackedData;

  const jobsQuery = useQuery({
    queryKey: ["stats", "jobs", jobIds],
    enabled: jobIds.length > 0,
    queryFn: async () => {
      const results = await Promise.all(
        jobIds.map((id: string) =>
          api.get(`/benchmark/jobs/${id}`).then(r => r.data).catch(() => null)
        )
      );
      return results.filter(Boolean);
    },
  });

  const ordersQuery = useQuery({
    queryKey: ["stats", "orders", orderIds],
    enabled: orderIds.length > 0,
    queryFn: async () => {
      const results = await Promise.all(
        orderIds.map((id: string) =>
          api.get(`/orders/${id}`).then(r => r.data).catch(() => null)
        )
      );
      return results.filter(Boolean);
    },
  });

  return useMemo(() => {
    const jobs = jobsQuery.data ?? [];
    const orders = ordersQuery.data ?? [];

    const activeBenchmarks = jobs.filter(j => j.status === "queued" || j.status === "running").length;
    const completedBenchmarks = jobs.filter(j => j.status === "ready").length;
    const activeOrders = orders.filter(o =>
      ["awaiting_payment", "processing"].includes(o.status)
    ).length;

    return {
      loading: jobsQuery.isLoading || ordersQuery.isLoading,
      activeBenchmarks,
      completedBenchmarks,
      activeOrders,
      totalTasks: jobs.length + orders.length,
    };
  }, [jobsQuery.data, ordersQuery.data, jobsQuery.isLoading, ordersQuery.isLoading]);
};

// ---------- Ontology ----------

export const useOntology = (params: GenerateOntologyParams | undefined) => {
  return useQuery({
    enabled: !!params?.domain && params.domain.trim().length >= 3,
    queryKey: params ? ['ontology', params.domain, params.locale] : ['ontology'],
    queryFn: async () => {
      const { data } = await api.post('/benchmark/ontology/generate', params);
      // 说明：如果后端已存在其它路径，请只改这里的路径；前端其它地方不感知。
      return data as Ontology;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};
