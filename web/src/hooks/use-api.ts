import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, API_BASE } from '@/lib/fetcher';
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
  estimated_scale?: any;
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
  suggested_params?: any;
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
  live?: any;
  delivery?: any;
  error?: string;
}

export interface ProductionStatusResponse {
  status: string;
  estCompleteAt?: string;
  logsUrl?: string;
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
    mutationFn: (body: QuoteRequest) => api.post(`${API_BASE}/benchmark/quote`, body).then(r => r.data),
    onSuccess: (data: QuoteResponse) => {
      qc.setQueryData(['quote', data.quoteId], data);
    },
  });
};

// Benchmark Job API
export const useCreateBenchmarkJob = () => {
  return useMutation({
    mutationFn: (body: BenchmarkJobCreateRequest) =>
      api.post(`${API_BASE}/benchmark/jobs`, body).then(r => r.data),
  });
};

export const useBenchmarkJob = (jobId?: string) => {
  return useQuery({
    queryKey: ['benchmark', jobId],
    queryFn: () => api.get(`${API_BASE}/benchmark/jobs/${jobId}`).then(r => r.data),
    enabled: !!jobId,
    refetchInterval: (last) => {
      const status = last?.status;
      return (!status || status === 'queued' || status === 'running') ? 3000 : false;
    },
  });
};

// Orders API
export const useCreateOrder = () => {
  return useMutation({
    mutationFn: ({ quoteId, jobId, email }: OrderCreateRequest) => {
      const idempotencyKey = getOrCreateIdemKey('order', `${quoteId}:${jobId}:${email}`);
      return api.post(`${API_BASE}/orders`, { quoteId, jobId, email }, {
        idempotencyKey
      }).then(r => r.data);
    },
  });
};

export const useOrder = (orderId?: string) => {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: () => api.get(`${API_BASE}/orders/${orderId}`).then(r => r.data),
    enabled: !!orderId,
    refetchInterval: (data) => {
      const doneStatuses = ['completed', 'failed', 'delivered'];
      return data && doneStatuses.includes(data.status) ? false : 5000;
    },
  });
};

export const useProduction = (orderId?: string) => {
  return useQuery({
    queryKey: ['production', orderId],
    queryFn: () => api.get(`${API_BASE}/orders/${orderId}/production`).then(r => r.data),
    enabled: !!orderId,
    refetchInterval: (data) => {
      return (data && ['delivered', 'failed'].includes(data.status)) ? false : 5000;
    },
  });
};

// Payment API
export const useCreateCheckoutSession = () => {
  return useMutation({
    mutationFn: ({ jobId, plan }: { jobId: string; plan?: string }) =>
      api.post(`${API_BASE}/checkout/session`, { jobId, plan }).then(r => r.data),
  });
};

// Email API
export const useEmailValidation = () => {
  return useMutation({
    mutationFn: (email: string) =>
      api.post(`${API_BASE}/email/validate`, { email }).then(r => r.data),
  });
};

export const useSendVerificationEmail = () => {
  return useMutation({
    mutationFn: (email: string) =>
      api.post(`${API_BASE}/email/verify/send`, { email }).then(r => r.data),
  });
};

export const useConfirmEmailVerification = () => {
  return useMutation({
    mutationFn: (token: string) =>
      api.post(`${API_BASE}/email/verify/confirm`, { token }).then(r => r.data),
  });
};

// Health check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.get(`${API_BASE.replace('/api/v1', '')}/health`).then(r => r.data),
    refetchInterval: 30000, // Check every 30 seconds
  });
};
