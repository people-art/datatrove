import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import { v4 as uuidv4 } from 'uuid';

// API base URL
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18000/api/v1';

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    suggestion?: string;
  };
  timestamp: string;
  request_id?: string;
}

export interface ApiConfig extends AxiosRequestConfig<any> {
  idempotencyKey?: string;
}

// 创建 axios 实例
export const api = axios.create({
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config: ApiConfig) => {
    // 添加请求 ID
    config.headers['X-Request-ID'] = uuidv4();

    // 添加幂等性键（如果提供）
    if (config.idempotencyKey) {
      config.headers['X-Idempotency-Key'] = config.idempotencyKey;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const config = error.config as ApiConfig;

    // 网络错误重试逻辑
    if (!error.response && config && !config._retry) {
      config._retry = true;

      // 指数退避重试（最多6次）
      for (let attempt = 0; attempt < 6; attempt++) {
        try {
          await new Promise(resolve => setTimeout(resolve, 100 * Math.pow(1.6, attempt)));
          return await api(config);
        } catch (retryError) {
          if (attempt === 5) throw retryError;
        }
      }
    }

    // 速率限制处理
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || '300';
      error.rateLimited = true;
      error.retryAfter = parseInt(retryAfter);
    }

    // 解析 API 错误格式
    if (error.response?.data?.error) {
      const apiError: ApiError = error.response.data;
      error.apiError = apiError;
    }

    return Promise.reject(error);
  }
);

// 工具函数
export const isRetryableError = (error: any): boolean => {
  // 网络错误可以重试
  if (!error.response) return true;

  // 服务器错误可以重试（5xx）
  if (error.response.status >= 500) return true;

  // 速率限制可以重试
  if (error.response.status === 429) return true;

  // 业务错误不重试
  return false;
};

export const getErrorMessage = (error: any): string => {
  if (error.apiError?.error?.message) {
    return error.apiError.error.message;
  }

  if (error.response?.status === 429) {
    const retryAfter = error.retryAfter || 300;
    const minutes = Math.ceil(retryAfter / 60);
    return `Rate limited. Try again in ${minutes} minute${minutes > 1 ? 's' : ''}.`;
  }

  if (error.response?.status >= 500) {
    return 'Server error. Please try again later.';
  }

  if (!error.response) {
    return 'Network error. Please check your connection.';
  }

  return 'An unexpected error occurred.';
};

export const getErrorSuggestion = (error: any): string | undefined => {
  return error.apiError?.error?.suggestion;
};

export const getTraceId = (error: any): string | undefined => {
  return error.apiError?.request_id || error.apiError?.timestamp;
};
