"use client";

import { createContext, useContext, useEffect, useState } from 'react';

export type Language = 'en' | 'zh';

// Utility function to get nested object property by dot-notation path
function getByPath(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj);
}

export interface Translations {
  nav: {
  features: string;
  pricing: string;
  docs: string;
    dashboard: string;
    signin: string;
    signout: string;
    signedInAs: string;
  createDataset: string;
  };
  home: {
    hero: {
      eyebrow: string;
      title: string;
      subtitle: string;
      cta_primary: string;
      cta_secondary: string;
    };
    why: {
    title: string;
      ai_filtering_title: string;
      ai_filtering_desc: string;
      scale_title: string;
      scale_desc: string;
      privacy_title: string;
      privacy_desc: string;
    };
    workflow: {
    title: string;
      step1_title: string;
      step1_desc: string;
      step2_title: string;
      step2_desc: string;
      step3_title: string;
      step3_desc: string;
      step4_title: string;
      step4_desc: string;
    };
    system_status_overview: string;
    stats: {
      active_benchmarks: string;
      completed_benchmarks: string;
      active_orders: string;
      total_tasks: string;
    };
  };
  features: {
    title: string;
    subtitle: string;
  };
  pricing: {
    title: string;
    subtitle: string;
  };
  docs: {
    title: string;
    subtitle: string;
  };
  dashboard: {
    title: string;
    subtitle: string;
    cards: {
      active: string;
      running: string;
      completed: string;
      avgTime: string;
    };
    table: {
      jobId: string;
      type: string;
      status: string;
      createdAt: string;
      progress: string;
      actions: string;
    };
    signInMessage: string;
    signInButton: string;
    recentTasks: string;
    taskDomain: string;
    loadingTasks: string;
    noTasksFound: string;
    createFirstTask: string;
    activityChart: string;
  };
  new: {
    steps: {
      step1: string;
      step2: string;
      step3: string;
      step4: string;
    };
    ontology: {
    title: string;
      generating: string;
      generated: string;
      ready: string;
      ready_to_generate: string;
      enter_domain_first: string;
      generate_button: string;
      error_empty_domain: string;
      error_domain_too_short: string;
      error_generic: string;
      error_title: string;
      required: string;
      concepts: string;
      entities: string;
      intents: string;
      positive_keywords: string;
      negative_keywords: string;
      examples: string;
      advanced_edit: string;
      apply_changes: string;
      reset: string;
    };
    quote: {
      uses_ontology_hint: string;
    };
    errors: {
      createBenchmarkFailed: string;
    };
  };
  charts: {
    activity: {
      desc: string;
      note: string;
    };
  };
  order: {
    errors: {
      viewDetails: string;
      close: string;
    };
  };
  footer: {
    tagline: string;
    docs: string;
    pricing: string;
    status: string;
    security: string;
    apiDown: string;
    apiHealthy: string;
    apiDegraded: string;
  };
  common: {
    retry: string;
    loading: string;
    error: string;
    success: string;
    cancel: string;
    confirm: string;
  };
  // Additional keys can be added as needed
}

const translations: Record<Language, Translations> = {
  en: {
    nav: {
    features: 'Features',
    pricing: 'Pricing',
    docs: 'Docs',
      dashboard: 'Dashboard',
      signin: 'Sign in',
      signout: 'Sign out',
      signedInAs: 'Signed in as',
    createDataset: 'Create Dataset',
    },
    home: {
      hero: {
        eyebrow: 'Custom Domain Datasets',
        title: 'Custom Domain Datasets. Powered by AI.',
        subtitle: 'Generate high-quality, domain-specific datasets from billions of web pages—ready for training specialized AI models, research, and analytics.',
        cta_primary: 'Get Started',
        cta_secondary: 'Learn More',
      },
      why: {
        title: 'Why FineData',
        ai_filtering_title: 'AI-Powered Filtering',
        ai_filtering_desc: 'Ontology-driven keyword expansion, LLM-assisted scoring, and multi-stage quality filters ensure your dataset matches your exact domain and intent.',
        scale_title: 'Massive Web-Scale Coverage',
        scale_desc: 'Leverage Common Crawl and battle-tested pipelines to process billions of pages with deterministic, reproducible configurations.',
        privacy_title: 'Enterprise-Grade Privacy',
        privacy_desc: 'PII detection, HIPAA-ready patterns for medical content, and strict sanitization keep your datasets safe and compliant.',
      },
      workflow: {
        title: 'How It Works',
        step1_title: 'Submit Requirements',
        step1_desc: 'Define your domain, keywords, languages, time range, and quality tier via the web console or API.',
        step2_title: 'Run Benchmark (1M pages)',
        step2_desc: 'We execute a local preview run using the exact same pipeline configuration and return metrics plus a sample dataset.',
        step3_title: 'Approve & Pay',
        step3_desc: 'Once you\'re satisfied with the preview, confirm the quote and complete payment via secure card checkout.',
        step4_title: 'Cluster Production & Delivery',
        step4_desc: 'A Slurm-based cluster run processes full Common Crawl segments. When finished, you receive a private Hugging Face URL via email.',
      },
      system_status_overview: 'System Status Overview',
      stats: {
        active_benchmarks: 'Active Benchmarks',
        completed_benchmarks: 'Completed Benchmarks',
        active_orders: 'Active Orders',
        total_tasks: 'Total Tasks',
      },
    },
    features: {
      title: 'Features',
      subtitle: 'Powerful features for creating high-quality datasets',
    },
    pricing: {
      title: 'Pricing',
      subtitle: 'Choose the plan that fits your needs',
    },
    docs: {
      title: 'Documentation',
      subtitle: 'Learn how to use FineData effectively',
    },
    dashboard: {
      title: 'Dashboard',
      subtitle: 'Monitor your jobs and orders',
      cards: {
        active: 'Active Tasks',
        running: 'Running',
        completed: 'Completed',
        avgTime: 'Avg Time',
      },
      table: {
        jobId: 'Job ID',
        type: 'Type',
        status: 'Status',
        createdAt: 'Created',
        progress: 'Progress',
        actions: 'Actions',
      },
      signInMessage: 'Please sign in to view your tasks and orders.',
      signInButton: 'Sign In',
      recentTasks: 'Recent Tasks',
      taskDomain: 'Domain',
      loadingTasks: 'Loading tasks...',
      noTasksFound: 'No tasks found.',
      createFirstTask: 'Create your first dataset to get started.',
      activityChart: 'Activity Chart',
    },
    features: {
      title: '功能特性',
      subtitle: '强大的功能，帮助您创建高质量的数据集',
    },
    pricing: {
      title: '价格方案',
      subtitle: '选择适合您需求的价格方案',
    },
    docs: {
      title: '文档',
      subtitle: '了解如何有效使用FineData',
    },
    dashboard: {
      title: '控制台',
      subtitle: '监控您的任务和订单',
      cards: {
        active: '活跃任务',
        running: '运行中',
        completed: '已完成',
        avgTime: '平均时间',
      },
      table: {
        jobId: '任务ID',
        type: '类型',
        status: '状态',
        createdAt: '创建时间',
        progress: '进度',
        actions: '操作',
      },
    },
    charts: {
      activity: {
        desc: '最近7天的活动',
        note: '显示基准测试和生产任务完成情况',
      },
    },
    order: {
      errors: {
        viewDetails: '查看错误详情',
        close: '关闭',
      },
    },
    footer: {
      tagline: '为 AI 团队提供企业级数据集生成服务',
      docs: '文档',
      pricing: '定价',
      status: '状态',
      security: '安全',
      apiDown: 'API 离线',
      apiHealthy: 'API 正常',
      apiDegraded: 'API 降级',
    },
    new: {
      steps: {
        step1: '定义您的领域',
        step2: '生成本体',
        step3: '运行基准测试',
        step4: '创建生产数据集',
      },
      ontology: {
        title: 'Data Ontology',
        generating: 'Generating…',
        generated: 'Generated',
        ready: 'Ready to generate',
        ready_to_generate: 'Click the button below to generate data ontology for your domain.',
        enter_domain_first: 'Please enter a domain name first.',
        generate_button: 'Generate Ontology',
        error_empty_domain: 'Please enter a domain name.',
        error_domain_too_short: 'Domain name must be at least 3 characters.',
        error_generic: 'Failed to generate ontology. Please try again.',
        error_title: 'Generation Failed',
        required: 'Please generate ontology before proceeding.',
        concepts: 'Core Concepts',
        entities: 'Key Entities',
        intents: 'User Intents',
        positive_keywords: 'Recommended Keywords',
        negative_keywords: 'Excluded Terms',
        examples: 'Examples',
        advanced_edit: 'Advanced edit',
        apply_changes: 'Apply changes',
        reset: 'Reset to auto',
      },
      quote: {
        uses_ontology_hint: '已根据当前领域自动生成数据本体，将用于后续定价与预览。',
      },
      errors: {
        createBenchmarkFailed: '创建基准测试任务失败，请重试。',
      },
    },
    common: {
      retry: '重试',
      loading: '加载中...',
      error: '错误',
      success: '成功',
      cancel: '取消',
      confirm: '确认',
    },
  },

  zh: {
    nav: {
    features: '功能特性',
    pricing: '价格方案',
    docs: '文档',
      signin: '登录',
      signout: '登出',
      signedInAs: '已登录为',
    createDataset: '创建数据集',
    },
    home: {
      hero: {
        eyebrow: '定制领域数据集',
        title: '定制领域数据集。由 AI 驱动。',
        subtitle: '从数十亿网页中生成高质量、特定领域的训练数据集——为专业 AI 模型、研究和分析做好准备。',
        cta_primary: '开始使用',
        cta_secondary: '了解更多',
      },
      why: {
        title: '为什么选择 FineData',
        ai_filtering_title: 'AI 驱动过滤',
        ai_filtering_desc: '基于本体的关键词扩展、LLM 相关性打分、多阶段质量过滤，精准匹配你的细分领域和使用场景。',
        scale_title: '万亿级网页覆盖',
        scale_desc: '基于 Common Crawl 与工程化流水线，稳定处理数十亿网页，配置可追踪、结果可复现。',
        privacy_title: '企业级隐私与合规',
        privacy_desc: '内置 PII 检测、医疗场景 HIPAA 规则、脱敏与审计日志，确保数据安全合规。',
      },
      workflow: {
        title: '工作流程',
        step1_title: '提交需求',
        step1_desc: '通过控制台或 API 配置领域、关键词、语言、时间范围和质量档位。',
        step2_title: '运行 Benchmark',
        step2_desc: '使用真实流水线在本地环境运行预览任务，返回质量指标和可下载样本。',
        step3_title: '确认并支付',
        step3_desc: '确认预览效果与报价后，通过安全银行卡支付完成下单。',
        step4_title: '集群生产与交付',
        step4_desc: '在 Slurm 集群上执行全量生产，完成后通过邮件发送 Hugging Face 私有仓库链接。',
      },
      system_status_overview: '系统状态概览',
      stats: {
        active_benchmarks: '活跃基准测试',
        completed_benchmarks: '已完成基准测试',
        active_orders: '活跃订单',
        total_tasks: '总任务数',
      },
    },
    features: {
      title: '功能特性',
      subtitle: '强大的功能，帮助您创建高质量的数据集',
    },
    pricing: {
      title: '价格方案',
      subtitle: '选择适合您需求的价格方案',
    },
    docs: {
      title: '文档',
      subtitle: '了解如何有效使用FineData',
    },
    dashboard: {
      title: '控制台',
      subtitle: '监控您的任务和订单',
      cards: {
        active: '活跃任务',
        running: '运行中',
        completed: '已完成',
        avgTime: '平均时间',
      },
      table: {
        jobId: '任务ID',
        type: '类型',
        status: '状态',
        createdAt: '创建时间',
        progress: '进度',
        actions: '操作',
      },
      signInMessage: '请登录后查看您的任务和订单。',
      signInButton: '登录',
      recentTasks: '最近任务',
      taskDomain: '领域',
      loadingTasks: '正在加载任务...',
      noTasksFound: '未找到任务。',
      createFirstTask: '创建您的第一个数据集开始使用。',
      activityChart: '活动图表',
    },
    charts: {
      activity: {
        desc: '最近7天的活动',
        note: '显示基准测试和生产任务完成情况',
      },
    },
    order: {
      errors: {
        viewDetails: '查看错误详情',
        close: '关闭',
      },
    },
    footer: {
      tagline: '为 AI 团队提供企业级数据集生成服务',
      docs: '文档',
      pricing: '定价',
      status: '状态',
      security: '安全',
      apiDown: 'API 离线',
      apiHealthy: 'API 正常',
      apiDegraded: 'API 降级',
    },
    new: {
      ontology: {
        title: '数据本体',
        generating: '正在生成…',
        generated: '已生成',
        ready: '准备生成',
        ready_to_generate: '点击下方按钮为您的领域生成数据本体。',
        enter_domain_first: '请先输入领域名称。',
        generate_button: '生成数据本体',
        error_empty_domain: '请输入领域名称。',
        error_domain_too_short: '领域名称至少需要3个字符。',
        error_generic: '生成数据本体失败，请重试。',
        error_title: '生成失败',
        required: '请先生成数据本体再继续。',
        concepts: '核心概念',
        entities: '关键实体',
        intents: '用户意图',
        positive_keywords: '建议的正向关键词',
        negative_keywords: '建议排除词',
        examples: '示例',
        advanced_edit: '高级编辑',
        apply_changes: '应用修改',
        reset: '恢复自动结果',
      },
      quote: {
        uses_ontology_hint: '已根据当前领域自动生成数据本体，将用于后续定价与预览。',
      },
      steps: {
        step1: '定义您的领域',
        step2: '生成本体',
        step3: '运行基准测试',
        step4: '创建生产数据集',
      },
      errors: {
        createBenchmarkFailed: '创建基准测试任务失败，请重试。',
      },
    },
    common: {
      retry: '重试',
      loading: '加载中...',
      error: '错误',
      success: '成功',
      cancel: '取消',
      confirm: '确认',
    },
  }
};

interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>('en');

  useEffect(() => {
    // Load language from localStorage
    const saved = localStorage.getItem('fd.lang') as Language;
    if (saved && (saved === 'en' || saved === 'zh')) {
      setLanguageState(saved);
    } else {
      // Default to browser language
      const browserLang = navigator.language.startsWith('zh') ? 'zh' : 'en';
      setLanguageState(browserLang);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('fd.lang', lang);
  };

  const t = (key: string): string => {
    // Try current language first
    const value = getByPath(translations[language], key);
    if (value !== undefined) {
      return value;
    }

    // Fallback to English
    const englishValue = getByPath(translations.en, key);
    if (englishValue !== undefined) {
      return englishValue;
    }

    // Final fallback to the key itself
    return key;
  };

  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  );
};