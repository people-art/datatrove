# FineData - Custom Domain Dataset Generation Service

一个完整的端到端数据处理服务，让用户能够定制化生成领域特定的高质量数据集。在AI智能体时代，部署智能体需要海量领域特定数据用于训练和微调。FineData 提供从需求收集到数据集交付的一站式服务，帮助您轻松构建专属数据集，支持未来AI智能体的实施和部署。

## 🎯 核心功能

FineData 的核心在于其智能、自动化的数据集生成管道，特别针对AI智能体部署的需求：

1. **需求表单** - 用户定义领域、关键词、语言和质量要求，支持复杂领域配置以匹配AI智能体的具体应用场景。
2. **快速预览** - 基于1M页样本生成质量指标、覆盖度分析和报价，帮助评估数据集对AI智能体训练的潜在价值。
3. **安全支付** - Stripe集成，支持多种支付方式，确保无缝过渡到生产级数据集生成。
4. **Slurm生产** - 大规模分布式数据处理，能够生成TB级领域数据，满足AI智能体大规模训练需求。
5. **交付通知** - Hugging Face私有数据集托管和邮件通知，便于集成到您的AI开发流程中。

这些功能确保您能快速获取高质量数据，支持从原型验证到生产部署的整个AI智能体生命周期。

## 🌟 项目亮点

- **LLM驱动的本体论生成**：自动构建领域知识体系，实现精确过滤和高质量数据提取 – 理想于创建AI智能体所需的语义丰富数据集。
- **多层次质量控制**：从URL过滤到PII移除的全链路处理，确保数据合规性，减少AI智能体训练中的噪声和偏见。
- **大规模可扩展性**：Slurm集群支持处理数亿网页，生成海量数据 – 直接响应未来AI智能体部署对大数据量的实际需求。
- **智能基准测试**：实时质量指标和样本预览，帮助优化数据集参数，提升AI智能体的性能和泛化能力。
- **隐私与安全优先**：内置PII检测和匿名化，符合数据保护法规，适合企业级AI智能体应用。
- **无缝集成**：输出兼容Hugging Face，支持直接用于模型训练，加速AI智能体从概念到部署的过程。

## 🚀 为什么选择FineData：AI智能体部署的实际数据需求

在未来AI智能体的部署和实施中，海量领域特定数据已成为核心瓶颈。通用数据集往往缺乏深度和相关性，导致智能体在特定场景下性能不佳。FineData 直接解决这一痛点：

- **训练需求**：AI智能体需要数百万到数十亿的领域特定样本进行预训练和微调，以实现上下文理解和决策能力。
- **领域适应**：通过自定义本体论，生成针对性数据，帮助智能体在教育、医疗、金融等垂直领域表现出色。
- **效率与成本**：自动化管道减少手动 curation 时间和成本，让您专注于智能体逻辑而非数据采集。
- **未来证明**：随着AI智能体向多模态和实时学习演进，FineData 的可扩展架构确保您始终拥有最新、高质量的数据供应。

使用FineData，您可以自信地构建和部署先进的AI智能体系统，推动创新边界。

## 🏗️ 系统架构

### 前端 (Next.js + TypeScript)
- **主页面** (`/`) - 功能介绍和导航，突出AI智能体用例。
- **需求表单** (`/new`) - 领域配置和即时报价，支持AI-specific参数如数据多样性要求。
- **预览页面** (`/preview/:jobId`) - 实时benchmark状态和指标展示，包括AI训练适用性评估。
- **结账页面** (`/checkout`) - Stripe支付集成。
- **订单状态** (`/order/:orderId`) - 生产进度和交付跟踪，包含数据统计摘要。

### 后端 (FastAPI + SQLAlchemy)
- **Benchmark API** - 本地预览任务管理和结果统计，优化为AI数据质量指标。
- **Payment API** - Stripe支付处理和订单管理。
- **Order API** - 状态查询和时间线跟踪。
- **异步任务** - Celery + Redis，用于处理大型AI数据集请求。

### 数据处理 (基于datatrove)
- **Ontology生成** - LLM驱动的领域知识体系构建，针对AI智能体优化。
- **质量过滤** - 多层次内容评估和PII移除，确保数据适合敏感应用。
- **分布式处理** - Slurm集群支持大规模数据处理。
- **存储集成** - S3 + Hugging Face数据集托管，便于AI框架集成。

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Slurm集群 (生产环境，用于大规模AI数据生成)

### 1. 后端设置

```bash
cd api
pip install -r requirements.txt

# 设置环境变量
cp env.example .env
# 编辑 .env 文件配置数据库、Stripe等

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
python main.py
```

### 2. 前端设置

```bash
cd web
npm install

# 设置环境变量
cp .env.example .env.local
# 配置 API_BASE_URL 等

# 启动开发服务器
npm run dev
```

### 3. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📊 其他核心功能

### 智能Benchmark
- 基于100万页样本的快速质量评估
- 多维度指标：覆盖度、质量通过率、PII风险等，特别包括AI训练相关指标如多样性和相关性
- 动态报价计算（基于实际数据统计）

### 安全支付流程
- Stripe Elements集成
- 3DS安全认证
- 完整的订单状态管理

### 大规模生产
- Slurm集群分布式处理
- 实时进度监控
- 自动质量控制和去重，优化为AI智能体数据需求

### 隐私保护
- PII自动检测和移除
- 数据匿名化处理
- 私有数据集托管

## 🔧 配置说明

### 环境变量

#### 后端 (.env)
```bash
# 数据库
POSTGRES_SERVER=localhost
POSTGRES_USER=finedata
POSTGRES_PASSWORD=password
POSTGRES_DB=finedata

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_DATASETS=finedata-datasets

# Hugging Face
HF_TOKEN=...
HF_ORG_NAME=...

# 应用
DEBUG=true
SECRET_KEY=your-secret-key
```

#### 前端 (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 🎨 UI组件

### 核心组件
- **DomainForm** - 智能领域配置表单，支持AI智能体特定设置
- **ProgressBar** - 多状态进度指示器
- **MetricCard** - 数据指标展示卡片，包括AI相关指标
- **QuoteCard** - 实时报价显示
- **SampleTable** - 数据样本预览表格

### 设计特色
- 响应式设计，支持移动端
- 骨架屏加载状态
- 实时数据轮询
- 渐进式指标展示

## 🔐 安全特性

- **支付安全** - Stripe托管，零卡号存储
- **数据保护** - PII自动检测和移除
- **访问控制** - 私有数据集，仅限授权用户
- **API安全** - JWT令牌验证和请求签名

## 📈 性能优化

- **异步处理** - Celery任务队列
- **缓存策略** - Redis缓存热点数据
- **数据库优化** - 连接池和查询优化
- **CDN集成** - 静态资源加速

## 🧪 测试

```bash
# 后端测试
cd api
pytest

# 前端测试
cd web
npm test
```

## 📦 部署

### 开发环境
```bash
# 使用Docker Compose
docker-compose up -d
```

### 生产环境
- 前端: Vercel/Netlify
- 后端: AWS/GCP/Azure
- 数据库: RDS/Cloud SQL
- 缓存: Redis Cloud/Elasticache

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [datatrove](https://github.com/huggingface/datatrove) - 核心数据处理引擎
- [Hugging Face](https://huggingface.co) - 数据集托管平台
- [Stripe](https://stripe.com) - 支付处理
- [Next.js](https://nextjs.org) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com) - 后端框架

---

**注意**: 这是一个概念验证实现。生产部署前需要完善错误处理、安全审计和性能优化，特别是针对大规模AI智能体数据生成。
