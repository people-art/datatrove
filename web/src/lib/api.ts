import axios from 'axios';
import type { DomainFormData, BenchmarkJob, QuoteData, Order, PaymentIntent, ApiResponse } from '@/types';

// New types for updated APIs
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

export interface ProductionStatusResponse {
  status: string;
  estCompleteAt?: string;
  logsUrl?: string;
  error?: string;
}

// Dynamic API base URL for different environments
const getApiBaseUrl = () => {
  // Always use relative paths so Next.js rewrites can proxy to backend
  // This ensures consistent behavior in both development and production
  if (typeof window !== 'undefined') {
    return '/api';
  }

  // Server-side: use NEXT_PUBLIC_API_URL for docker internal network
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18000/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth if needed
api.interceptors.request.use((config) => {
  // Add auth headers if needed
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Benchmark APIs
export const benchmarkApi = {
  createJob: async (data: DomainFormData): Promise<{ jobId: string }> => {
    const response = await api.post('/benchmark/jobs', data);
    return response.data;
  },

  getJob: async (jobId: string): Promise<BenchmarkJob> => {
    const response = await api.get(`/benchmark/jobs/${jobId}`);
    return response.data;
  },

  createQuote: async (data: QuoteRequest): Promise<QuoteResponse> => {
    const response = await api.post('/benchmark/quote', data);
    return response.data;
  },

  getQuote: async (jobId: string): Promise<QuoteData> => {
    // Legacy method - kept for backward compatibility
    const response = await api.post('/quote', { jobId });
    return response.data;
  },
};

// Payment APIs
export const paymentApi = {
  createSession: async (jobId: string): Promise<PaymentIntent> => {
    const response = await api.post('/payments/session', { jobId, plan: 'one-off' });
    return response.data;
  },
};

// Order APIs
export const orderApi = {
  createOrder: async (data: OrderCreateRequest, idempotencyKey?: string): Promise<OrderCreateResponse> => {
    const headers = idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {};
    const response = await api.post('/orders', data, { headers });
    return response.data;
  },

  getOrder: async (orderId: string): Promise<Order> => {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  getProductionStatus: async (orderId: string): Promise<ProductionStatusResponse> => {
    const response = await api.get(`/orders/${orderId}/production`);
    return response.data;
  },
};

// Email APIs
export const emailApi = {
  validateEmail: async (email: string): Promise<{
    email: string;
    isValid: boolean;
    domain: string;
    checks: Record<string, boolean>;
  }> => {
    const response = await api.post('/email/validate', { email });
    return response.data;
  },

  sendVerification: async (email: string): Promise<{
    success: boolean;
    message: string;
  }> => {
    const response = await api.post('/email/verify/send', { email });
    return response.data;
  },

  confirmVerification: async (token: string): Promise<{
    success: boolean;
    email: string;
    message: string;
  }> => {
    const response = await api.post('/email/verify/confirm', { token });
    return response.data;
  },
};

// Utility functions
export const downloadFile = async (url: string, filename: string) => {
  try {
    const response = await fetch(url);
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};

export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};
