# FineData - Custom Domain Dataset Generation Service

一个完整的端到端数据处理服务，让用户能够定制化生成领域特定的高质量数据集。

## 🎯 功能概述

FineData 提供了从用户需求收集到最终数据集交付的完整流程：

1. **需求表单** - 用户定义领域、关键词、语言和质量要求
2. **快速预览** - 基于1M页样本生成质量指标和报价
3. **安全支付** - Stripe集成，支持多种支付方式
4. **Slurm生产** - 大规模分布式数据处理
5. **交付通知** - Hugging Face私有数据集和邮件通知

## 🏗️ 系统架构

### 前端 (Next.js + TypeScript)
- **主页面** (`/`) - 功能介绍和导航
- **需求表单** (`/new`) - 领域配置和即时报价
- **预览页面** (`/preview/:jobId`) - 实时benchmark状态和指标展示
- **结账页面** (`/checkout`) - Stripe支付集成
- **订单状态** (`/order/:orderId`) - 生产进度和交付跟踪

### 后端 (FastAPI + SQLAlchemy)
- **Benchmark API** - 本地预览任务管理和结果统计
- **Payment API** - Stripe支付处理和订单管理
- **Order API** - 状态查询和时间线跟踪
- **异步任务** - Celery + Redis (待实现)

### 数据处理 (基于datatrove)
- **Ontology生成** - LLM驱动的领域知识体系构建
- **质量过滤** - 多层次内容评估和PII移除
- **分布式处理** - Slurm集群支持大规模数据处理
- **存储集成** - S3 + Hugging Face数据集托管

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Slurm集群 (生产环境)

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

## 📊 核心功能

### 智能Benchmark
- 基于100万页样本的快速质量评估
- 多维度指标：覆盖度、质量通过率、PII风险等
- 动态报价计算（基于实际数据统计）

### 安全支付流程
- Stripe Elements集成
- 3DS安全认证
- 完整的订单状态管理

### 大规模生产
- Slurm集群分布式处理
- 实时进度监控
- 自动质量控制和去重

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
- **DomainForm** - 智能领域配置表单
- **ProgressBar** - 多状态进度指示器
- **MetricCard** - 数据指标展示卡片
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

**注意**: 这是一个概念验证实现。生产部署前需要完善错误处理、安全审计和性能优化。
