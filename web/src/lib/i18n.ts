import { createContext, useContext, useEffect, useState } from 'react';

export type Language = 'en' | 'zh';

export interface Translations {
  // Navigation
  'nav.features': string;
  'nav.pricing': string;
  'nav.docs': string;
  'nav.dashboard': string;
  'nav.signin': string;
  'nav.createDataset': string;

  // Home page - Hero
  'home.hero.eyebrow': string;
  'home.hero.title': string;
  'home.hero.subtitle': string;
  'home.hero.cta_primary': string;
  'home.hero.cta_secondary': string;

  // Home page - Why
  'home.why.title': string;
  'home.why.ai_filtering_title': string;
  'home.why.ai_filtering_desc': string;
  'home.why.scale_title': string;
  'home.why.scale_desc': string;
  'home.why.privacy_title': string;
  'home.why.privacy_desc': string;

  // Home page - Workflow
  'home.workflow.title': string;
  'home.workflow.step1_title': string;
  'home.workflow.step1_desc': string;
  'home.workflow.step2_title': string;
  'home.workflow.step2_desc': string;
  'home.workflow.step3_title': string;
  'home.workflow.step3_desc': string;
  'home.workflow.step4_title': string;
  'home.workflow.step4_desc': string;

  // Home page - System status
  'home.system_status_overview': string;
  'home.stats.active_benchmarks': string;
  'home.stats.completed_benchmarks': string;
  'home.stats.active_orders': string;
  'home.stats.total_tasks': string;

  // Footer
  'footer.tagline': string;
  'footer.docs': string;
  'footer.pricing': string;
  'footer.status': string;
  'footer.security': string;
  'footer.apiHealthy': string;
  'footer.apiDegraded': string;
  'footer.apiDown': string;

  // Legacy keys (for backward compatibility)
  features: string;
  pricing: string;
  docs: string;
  createDataset: string;
  dashboard: string;
  heroTitle: string;
  heroSubtitle: string;
  getStarted: string;
  learnMore: string;

  // Form
  domain: string;
  keywords: string;
  languages: string;
  timeRange: string;
  qualityTier: string;
  estimatedScale: string;
  email: string;
  generatePreview: string;
  estimatedPrice: string;

  // Processing
  localPreview: string;
  slurmProduction: string;
  activeNodes: string;
  throughput: string;
  queueDepth: string;
  progress: string;

  // Errors
  rateLimited: string;
  tryAgainAfter: string;
  traceId: string;
  contactSupport: string;

  // Email validation
  formatOK: string;
  mxChecking: string;
  mxOK: string;
  smtpChecking: string;
  smtpOK: string;
  disposableBlocked: string;

  // Orders/Payment
  confirmOrder: string;
  payNow: string;
  awaitingPayment: string;
  processing: string;
  completed: string;
  failed: string;

  // Footer legacy
  privacy: string;
  terms: string;
  contact: string;

  // Features page
  features_title: string;
  features_subtitle: string;
  features_blocks: Array<{
    title: string;
    body: string;
  }>;

  // Pricing page
  pricing_title: string;
  pricing_subtitle: string;
  pricing_cards: Array<{
    name: string;
    price: string;
    unit: string;
    desc: string;
    items: string[];
  }>;
  pricing_notes: string[];

  // Docs page
  docs_title: string;
  docs_subtitle: string;
  docs_flow: Array<{
    step: number;
    title: string;
    body: string;
  }>;
  docs_api_title: string;
  docs_api_items: string[];
  docs_notes: string[];
}

// Tool function: get value by dot path from nested object
function getByPath(obj: any, path: string): any {
  return path.split('.').reduce((acc, part) => {
    if (acc && typeof acc === 'object' && part in acc) {
      return acc[part];
    }
    return undefined;
  }, obj);
}

const translations: Record<Language, any> = {
  en: {
    // Navigation
    'nav.features': 'Features',
    'nav.pricing': 'Pricing',
    'nav.docs': 'Docs',
    'nav.dashboard': 'Dashboard',
    'nav.signin': 'Sign in',
    'nav.createDataset': 'Create Dataset',

    // Home page - Hero
    'home.hero.eyebrow': 'Custom Domain Datasets Powered by AI',
    'home.hero.title': 'Custom Domain Datasets for AI Teams',
    'home.hero.subtitle': 'From billions of web pages to curated, domain-specific datasets — ready for specialized models and RAG systems.',
    'home.hero.cta_primary': 'Create Dataset',
    'home.hero.cta_secondary': 'View Docs',

    // Home page - Why
    'home.why.title': 'Why FineData',
    'home.why.ai_filtering_title': 'AI-Powered Filtering',
    'home.why.ai_filtering_desc': 'Ontology-based keyword expansion, LLM relevance scoring, multi-stage quality filtering for precise domain matching.',
    'home.why.scale_title': 'Trillion-Scale Coverage',
    'home.why.scale_desc': 'Built on Common Crawl with engineered pipelines, processing billions of pages with traceable configs and reproducible results.',
    'home.why.privacy_title': 'Enterprise Privacy & Compliance',
    'home.why.privacy_desc': 'Built-in PII detection, HIPAA rules for healthcare, anonymization and audit logs ensuring data security and compliance.',

    // Home page - Workflow
    'home.workflow.title': 'How It Works',
    'home.workflow.step1_title': 'Submit Requirements',
    'home.workflow.step1_desc': 'Define domain, keywords, languages, time range, and quality tier.',
    'home.workflow.step2_title': 'Run Benchmark (1M pages)',
    'home.workflow.step2_desc': 'We run a local single-node benchmark and return metrics plus samples.',
    'home.workflow.step3_title': 'Approve & Pay',
    'home.workflow.step3_desc': 'Confirm the quote and pay via secure card checkout.',
    'home.workflow.step4_title': 'Cluster Production',
    'home.workflow.step4_desc': 'A Slurm cluster runs the full job and delivers a private Hugging Face dataset URL.',

    // Home page - System status
    'home.system_status_overview': 'System Status Overview',
    'home.stats.active_benchmarks': 'Active Benchmarks',
    'home.stats.completed_benchmarks': 'Completed Benchmarks',
    'home.stats.active_orders': 'Active Orders',
    'home.stats.total_tasks': 'Total Tasks',

    // Footer
    'footer.tagline': 'Custom domain datasets for AI teams.',
    'footer.docs': 'Docs',
    'footer.pricing': 'Pricing',
    'footer.status': 'Status',
    'footer.security': 'Security',
    'footer.apiHealthy': 'API: Healthy',
    'footer.apiDegraded': 'API: Degraded',
    'footer.apiDown': 'API: Down',

    // Legacy keys (for backward compatibility)
    features: 'Features',
    pricing: 'Pricing',
    docs: 'Docs',
    createDataset: 'Create Dataset',
    dashboard: 'Dashboard',
    heroTitle: 'Custom Domain Datasets. Powered by AI.',
    heroSubtitle: 'Generate high-quality, domain-specific datasets from billions of web pages—ready for training specialized AI models, research, and analytics.',
    getStarted: 'Get Started',
    learnMore: 'Learn More',

    // Form
    domain: 'Domain/Topic',
    keywords: 'Keywords',
    languages: 'Languages',
    timeRange: 'Time Range',
    qualityTier: 'Quality Tier',
    estimatedScale: 'Estimated Scale',
    email: 'Email Address',
    generatePreview: 'Generate Preview (1M pages)',
    estimatedPrice: 'Estimated Price',

    // Processing
    localPreview: 'Local Preview',
    slurmProduction: 'Slurm Production',
    activeNodes: 'Active Nodes',
    throughput: 'Throughput',
    queueDepth: 'Queue Depth',
    progress: 'Progress',

    // Errors
    rateLimited: 'Rate Limited',
    tryAgainAfter: 'Try again after',
    traceId: 'Trace ID',
    contactSupport: 'Contact Support',

    // Email validation
    formatOK: 'Format OK',
    mxChecking: 'Checking MX records...',
    mxOK: 'MX records OK',
    smtpChecking: 'Checking SMTP connection...',
    smtpOK: 'SMTP connection OK',
    disposableBlocked: 'Disposable email addresses not allowed',

    // Orders/Payment
    confirmOrder: 'Confirm Order',
    payNow: 'Pay Now',
    awaitingPayment: 'Awaiting Payment',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed',

  // Footer
  privacy: 'Privacy',
  terms: 'Terms',
  contact: 'Contact',

  // Features page
  features_title: "Why FineData",
  features_subtitle: "Purpose-built for AI teams, researchers, and enterprises that demand clean, controllable, and scalable training data.",
  features_blocks: [
    {
      title: "AI-Powered Filtering",
      body: "Ontology-driven keyword expansion, LLM-assisted scoring, and multi-stage quality filters ensure your dataset matches your exact domain and intent."
    },
    {
      title: "Massive Web-Scale Coverage",
      body: "Leverage Common Crawl and battle-tested pipelines to process billions of pages with deterministic, reproducible configurations."
    },
    {
      title: "Enterprise-Grade Privacy",
      body: "PII detection, HIPAA-ready patterns for medical content, and strict sanitization keep your datasets safe and compliant."
    },
    {
      title: "Custom Domains in Days",
      body: "Support any niche domain: finance, medical, robotics, law, education, energy, security, and internal ontologies."
    },
    {
      title: "Transparent Metrics",
      body: "Every run ships with coverage, dedup ratio, language mix, toxicity and PII rates, plus domain relevance reports."
    },
    {
      title: "Private Delivery on Hugging Face",
      body: "Datasets are delivered as private Hugging Face repositories or S3 buckets with fine-grained access control."
    }
  ],

  // Pricing page
  pricing_title: "Simple, Transparent Pricing",
  pricing_subtitle: "Pay for high-quality, domain-specific data — no lock-in, no hidden fees.",
  pricing_cards: [
    {
      name: "Preview Benchmark",
      price: "Free",
      unit: "",
      desc: "1M-page local benchmark to validate quality before you commit.",
      items: [
        "Custom domain & keywords",
        "End-to-end pipeline simulation",
        "Quality and coverage report",
        "Sample dataset download"
      ]
    },
    {
      name: "Standard Production",
      price: "From $50",
      unit: "per million tokens",
      desc: "Balanced quality for most fine-tuning and RAG workloads.",
      items: [
        "Common Crawl based sourcing",
        "Multi-stage quality & PII filters",
        "Minhash deduplication",
        "Private Hugging Face delivery"
      ]
    },
    {
      name: "Premium Curated",
      price: "Custom",
      unit: "",
      desc: "For regulated industries and mission-critical models.",
      items: [
        "Stricter filters and LLM scoring",
        "Domain expert review options",
        "Custom ontologies & constraints",
        "SLA, support, and governance"
      ]
    }
  ],
  pricing_notes: [
    "Final pricing is computed from your quote: domain complexity, time range, target size, and quality tier.",
    "You always see an estimated range before payment, based on the benchmark run.",
    "Enterprise and multi-run commitments can be discounted."
  ],

  // Docs page
  docs_title: "How FineData Works",
  docs_subtitle: "From request to private dataset in four predictable steps.",
  docs_flow: [
    {
      step: 1,
      title: "Submit Requirements",
      body: "Define your domain, keywords, languages, time range, and quality tier via the web console or API."
    },
    {
      step: 2,
      title: "Run Benchmark (1M pages)",
      body: "We execute a local preview run using the exact same pipeline configuration and return metrics plus a sample dataset."
    },
    {
      step: 3,
      title: "Approve & Pay",
      body: "Once you're satisfied with the preview, confirm the quote and complete payment via secure card checkout."
    },
    {
      step: 4,
      title: "Cluster Production & Delivery",
      body: "A Slurm-based cluster run processes full Common Crawl segments. When finished, you receive a private Hugging Face URL via email."
    }
  ],
  docs_api_title: "API Overview",
  docs_api_items: [
    "POST /benchmark/quote – Get an estimated price for your config.",
    "POST /benchmark/jobs – Start a 1M-page benchmark job.",
    "GET /benchmark/jobs/{id} – Poll benchmark status and metrics.",
    "POST /orders – Create an order from a quote and job.",
    "GET /orders/{id} – Track order and payment status.",
    "GET /orders/{id}/production – View production pipeline progress.",
    "POST /email/validate – Validate email format/MX/SMTP/disposable.",
    "POST /checkout/session – Create payment session (Stripe compatible)."
  ],
  docs_notes: [
    "All responses follow a unified error schema with code, message, suggestion, and timestamp.",
    "Idempotency keys are supported on all create operations to keep retries safe.",
    "Production runs are isolated per customer and delivered via private repositories."
    ],

    // Pricing page
    pricing_title: '清晰透明的定价方式',
    pricing_subtitle: '按照真实工作量和数据质量计费，没有绑定合同，没有隐藏费用。',
    pricing_cards: [
      {
        name: '预览 Benchmark',
        price: '免费',
        unit: '',
        desc: '本地 100 万页基准运行，先看效果再决策。',
        items: [
          '自定义领域与关键词',
          '端到端流水线模拟',
          '质量与覆盖率报告',
          '可下载样本数据集',
        ],
      },
      {
        name: '标准生产版',
        price: '50 美元起',
        unit: '每百万 tokens',
        desc: '适用于绝大多数微调与 RAG 场景的高性价比方案。',
        items: [
          '基于 Common Crawl 的数据源',
          '多阶段质量与隐私过滤',
          'Minhash 去重与统计报告',
          'Hugging Face 私有仓交付',
        ],
      },
      {
        name: '高端定制版',
        price: '定制报价',
        unit: '',
        desc: '面向金融、医疗、政企等高敏感场景的严选数据。',
        items: [
          '更严格的过滤与 LLM 打分',
          '可选专家审核与黑白名单',
          '支持自定义本体与合规策略',
          'SLA、专属支持与治理方案',
        ],
      },
    ],
    pricing_notes: [
      '最终价格由领域难度、时间范围、目标规模、质量档位等综合计算。',
      '在支付前，你将基于 Benchmark 结果看到真实区间报价。',
      '长期合作与多批次任务可提供折扣与专属方案。',
    ],

    // Docs page
    docs_title: 'FineData 工作原理',
    docs_subtitle: '从需求提交到私有数据集交付，仅需四个可预测步骤。',
    docs_flow: [
      {
        step: 1,
        title: '提交数据需求',
        body: '通过控制台或 API 配置领域、关键词、语言、时间范围和质量档位。',
      },
      {
        step: 2,
        title: '运行 100 万页 Benchmark',
        body: '使用真实流水线在本地环境运行预览任务，返回质量指标和可下载样本。',
      },
      {
        step: 3,
        title: '确认方案并支付',
        body: '确认预览效果与报价后，通过安全银行卡支付完成下单。',
      },
      {
        step: 4,
        title: '集群生产与私有交付',
        body: '在 Slurm 集群上执行全量生产，完成后通过邮件发送 Hugging Face 私有仓库链接。',
      },
    ],
    docs_api_title: 'API 概览',
    docs_api_items: [
      'POST /benchmark/quote —— 根据配置生成价格预估。',
      'POST /benchmark/jobs —— 创建 100 万页 Benchmark 任务。',
      'GET /benchmark/jobs/{id} —— 轮询任务状态与质量指标。',
      'POST /orders —— 基于 quote 和 job 创建订单（支持幂等键）。',
      'GET /orders/{id} —— 查询订单与支付状态。',
      'GET /orders/{id}/production —— 查看生产流水线进度。',
      'POST /email/validate —— 校验邮箱格式/MX/SMTP/一次性域名。',
      'POST /checkout/session —— 创建支付会话（兼容 Stripe）。',
    ],
    docs_notes: [
      '所有错误均使用统一结构：错误码、信息、建议和时间戳，便于排查。',
      '所有创建类接口建议携带幂等键，确保网络重试是安全的。',
      '生产任务彼此隔离，交付通过私有仓库或安全存储完成。',
    ],
  },

  zh: {
    // Navigation
    'nav.features': '特性',
    'nav.pricing': '定价',
    'nav.docs': '文档',
    'nav.dashboard': '控制台',
    'nav.signin': '登录',
    'nav.createDataset': '创建数据集',

    // Home page - Hero
    'home.hero.eyebrow': 'Custom Domain Datasets Powered by AI',
    'home.hero.title': '为 AI 团队定制的领域数据集',
    'home.hero.subtitle': '从海量网页中抽取高质量、特定领域的数据，为专用模型与检索系统提供可靠语料。',
    'home.hero.cta_primary': '创建数据集',
    'home.hero.cta_secondary': '查看文档',

    // Home page - Why
    'home.why.title': '为什么选择 FineData',
    'home.why.ai_filtering_title': 'AI 驱动过滤',
    'home.why.ai_filtering_desc': '基于本体的关键词扩展、多级质量过滤与 LLM 评分，精准匹配你的领域与意图。',
    'home.why.scale_title': '万亿级网页覆盖',
    'home.why.scale_desc': '直接处理 Common Crawl 数据，稳定扩展到数十亿网页。',
    'home.why.privacy_title': '企业级隐私与合规',
    'home.why.privacy_desc': 'PII 清理、合规审计与私有交付，确保数据安全可控。',

    // Home page - Workflow
    'home.workflow.title': '工作流程',
    'home.workflow.step1_title': '提交需求',
    'home.workflow.step1_desc': '配置领域、关键词、语言、时间范围和质量等级。',
    'home.workflow.step2_title': '运行 100 万页 Benchmark',
    'home.workflow.step2_desc': '在本地单机模拟完整流程，返回指标和样本。',
    'home.workflow.step3_title': '确认并支付',
    'home.workflow.step3_desc': '根据 Benchmark 结果确认配置，通过银行卡支付。',
    'home.workflow.step4_title': '集群生产与交付',
    'home.workflow.step4_desc': '在 Slurm 集群上完成全量处理，通过私有 Hugging Face 仓库交付。',

    // Home page - System status
    'home.system_status_overview': '系统状态概览',
    'home.stats.active_benchmarks': '活跃基准任务',
    'home.stats.completed_benchmarks': '已完成基准',
    'home.stats.active_orders': '活跃订单',
    'home.stats.total_tasks': '总任务数',

    // Footer
    'footer.tagline': '为 AI 团队提供高质量领域数据集。',
    'footer.docs': '文档',
    'footer.pricing': '定价',
    'footer.status': '状态',
    'footer.security': '安全',
    'footer.apiHealthy': 'API：正常',
    'footer.apiDegraded': 'API：受限',
    'footer.apiDown': 'API：故障',

    // Legacy keys (for backward compatibility)
    features: '功能特性',
    pricing: '价格方案',
    docs: '文档',
    createDataset: '创建数据集',
    dashboard: '控制台',
    heroTitle: '定制领域数据集。由 AI 驱动。',
    heroSubtitle: '从数十亿网页中生成高质量、特定领域的训练数据集——为专业 AI 模型、研究和分析做好准备。',
    getStarted: '开始使用',
    learnMore: '了解更多',

    // Form
    domain: '领域/主题',
    keywords: '关键词',
    languages: '语言',
    timeRange: '时间范围',
    qualityTier: '质量等级',
    estimatedScale: '预估规模',
    email: '邮箱地址',
    generatePreview: '生成预览（100万页）',
    estimatedPrice: '预估价格',

    // Processing
    localPreview: '本地预览',
    slurmProduction: 'Slurm 生产',
    activeNodes: '活跃节点',
    throughput: '吞吐量',
    queueDepth: '队列深度',
    progress: '进度',

    // Errors
    rateLimited: '请求频率限制',
    tryAgainAfter: '请在',
    traceId: '追踪 ID',
    contactSupport: '联系支持',

    // Email validation
    formatOK: '格式正确',
    mxChecking: '检查 MX 记录中...',
    mxOK: 'MX 记录正确',
    smtpChecking: '检查 SMTP 连接中...',
    smtpOK: 'SMTP 连接正常',
    disposableBlocked: '不支持一次性邮箱地址',

    // Orders/Payment
    confirmOrder: '确认订单',
    payNow: '立即支付',
    awaitingPayment: '等待支付',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',

    // Footer
    privacy: '隐私政策',
    terms: '服务条款',
    contact: '联系我们',

    // Features page
    features_title: '为什么选择 FineData',
    features_subtitle: '为 AI 团队、研究机构和企业打造的专业级数据工厂，提供可控、可审计、可扩展的训练数据。',
    features_blocks: [
      {
        title: 'AI 驱动过滤',
        body: '基于本体的关键词扩展、LLM 相关性打分、多阶段质量过滤，精准匹配你的细分领域和使用场景。'
      },
      {
        title: '万亿级网页覆盖',
        body: '基于 Common Crawl 与工程化流水线，稳定处理数十亿网页，配置可追踪、结果可复现。'
      },
      {
        title: '企业级隐私与合规',
        body: '内置 PII 检测、医疗场景 HIPAA 规则、脱敏与审计日志，确保数据安全合规。'
      },
      {
        title: '任意垂直领域定制',
        body: '支持金融、医疗、法律、教育、能源、安全、机器人等高价值领域，以及自定义业务本体。'
      },
      {
        title: '完整质量度量',
        body: '每次运行提供覆盖率、去重率、语言分布、毒性和隐私指标，以及领域相关性报告。'
      },
      {
        title: '私有交付与权限控制',
        body: '通过 Hugging Face 私有仓库或 S3 等方式交付，支持精细化访问控制和审计。'
      }
    ],

    // Pricing page
    pricing_title: '清晰透明的定价方式',
    pricing_subtitle: '按照真实工作量和数据质量计费，没有绑定合同，没有隐藏费用。',
    pricing_cards: [
      {
        name: '预览 Benchmark',
        price: '免费',
        unit: '',
        desc: '本地 100 万页基准运行，先看效果再决策。',
        items: [
          '自定义领域与关键词',
          '端到端流水线模拟',
          '质量与覆盖率报告',
          '可下载样本数据集'
        ]
      },
      {
        name: '标准生产版',
        price: '50 美元起',
        unit: '每百万 tokens',
        desc: '适用于绝大多数微调与 RAG 场景的高性价比方案。',
        items: [
          '基于 Common Crawl 的数据源',
          '多阶段质量与隐私过滤',
          'Minhash 去重与统计报告',
          'Hugging Face 私有仓交付'
        ]
      },
      {
        name: '高端定制版',
        price: '定制报价',
        unit: '',
        desc: '面向金融、医疗、政企等高敏感场景的严选数据。',
        items: [
          '更严格的过滤与 LLM 打分',
          '可选专家审核与黑白名单',
          '支持自定义本体与合规策略',
          'SLA、专属支持与治理方案'
        ]
      }
    ],
    pricing_notes: [
      '最终价格由领域难度、时间范围、目标规模、质量档位等综合计算。',
      '在支付前，你将基于 Benchmark 结果看到真实区间报价。',
      '长期合作与多批次任务可提供折扣与专属方案。'
    ],

    // Docs page
    docs_title: 'FineData 工作原理',
    docs_subtitle: '从需求提交到私有数据集交付，仅需四个可预测步骤。',
    docs_flow: [
      {
        step: 1,
        title: '提交数据需求',
        body: '通过控制台或 API 配置领域、关键词、语言、时间范围和质量档位。'
      },
      {
        step: 2,
        title: '运行 100 万页 Benchmark',
        body: '使用真实流水线在本地环境运行预览任务，返回质量指标和可下载样本。'
      },
      {
        step: 3,
        title: '确认方案并支付',
        body: '确认预览效果与报价后，通过安全银行卡支付完成下单。'
      },
      {
        step: 4,
        title: '集群生产与私有交付',
        body: '在 Slurm 集群上执行全量生产，完成后通过邮件发送 Hugging Face 私有仓库链接。'
      }
    ],
    docs_api_title: 'API 概览',
    docs_api_items: [
      'POST /benchmark/quote —— 根据配置生成价格预估。',
      'POST /benchmark/jobs —— 创建 100 万页 Benchmark 任务。',
      'GET /benchmark/jobs/{id} —— 轮询任务状态与质量指标。',
      'POST /orders —— 基于 quote 和 job 创建订单（支持幂等键）。',
      'GET /orders/{id} —— 查询订单与支付状态。',
      'GET /orders/{id}/production —— 查看生产流水线进度。',
      'POST /email/validate —— 校验邮箱格式/MX/SMTP/一次性域名。',
      'POST /checkout/session —— 创建支付会话（兼容 Stripe）。'
    ],
    docs_notes: [
      '所有错误均使用统一结构：错误码、信息、建议和时间戳，便于排查。',
      '所有创建类接口建议携带幂等键，确保网络重试是安全的。',
      '生产任务彼此隔离，交付通过私有仓库或安全存储完成。'
    ]
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
    // First try current language with nested path
    let value = getByPath(translations[language], key);
    if (value === undefined) {
      // Then try English fallback with nested path
      value = getByPath(translations.en, key);
    }
    if (typeof value === 'string') return value;
    return key; // Final fallback to show the key for debugging
  };

  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  );
};