// API Types
export interface DomainFormData {
  domain: string;
  keywords: string[];
  languages: string[];
  timeRange: {
    start: string;
    end: string;
  };
  qualityTier: 'basic' | 'standard' | 'premium';
  estimatedScale?: string;
  email: string;
}

export interface BenchmarkJob {
  id: string;
  domain: string;
  keywords: string[];
  languages: string[];
  time_range_start: string;
  time_range_end: string;
  quality_tier: string;
  email: string;
  estimated_scale?: {
    docs?: number;
    tokens?: number;
  };
  status: 'queued' | 'running' | 'ready' | 'failed';
  progress: {
    pct: number;
    docs_read: number;
    docs_kept: number;
    tokens: number;
    dedup_rate: number;
    coverage?: number;
    quality_rate?: number;
    pii_rate?: number;
    relevance_score?: number;
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
  suggested_params?: {
    thresholds: Record<string, any>;
    filters: Record<string, any>;
  };
  error?: string;
  error_message?: string;
  created_at: string;
}

export interface QuoteData {
  currency: string;
  estimated_tokens?: number;
  actual_tokens?: number;
  subtotal: number;
  tax: number;
  total: number;
  pricing_notes: string;
  breakdown?: {
    base_price_per_million: number;
    language_factor: number;
    domain_factor: number;
    time_factor: number;
    adjusted_price_per_million: number;
  };
  quality_adjustment?: number;
  benchmark_results?: any;
}

export interface Order {
  id: string;
  status: 'draft' | 'benchmarking' | 'preview_ready' | 'awaiting_payment' | 'paid' | 'cluster_queued' | 'running' | 'finalizing' | 'delivered' | 'failed';
  timeline: Array<{
    timestamp: string;
    label: string;
  }>;
  live?: {
    fetched: number;
    filtered: number;
    deduped: number;
    tokens: number;
  };
  delivery?: {
    hf_url?: string;
    dataset_card?: string;
    invoice_url?: string;
  };
  error?: string;
  last_logs?: string;
}

// Component Props Types
export interface ProgressBarProps {
  status: BenchmarkJob['status'];
  progress?: number;
}

export interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export interface SampleTableProps {
  samples: Array<{
    text: string;
    url: string;
    score?: number;
  }>;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Payment Types
export interface PaymentIntent {
  client_secret: string;
  orderId: string;
}
