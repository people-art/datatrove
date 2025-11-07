# FineData: Universal Domain-Specific Dataset Build Pipeline

FineWeb-Data 是一个通用的领域特定数据集处理管道，基于 FineWeb 方法论构建。该管道可以根据用户输入的主题词或领域动态生成本体论驱动的关键词，并从中创建高质量的领域数据集。

## 🚀 核心特性

### 🎯 动态领域生成
- **LLM驱动的本体论构建**：使用 GPT-5 为任何领域自动生成结构化的知识体系
- **多层次关键词体系**：核心概念、子领域、关键词、技术术语、上下文指标
- **智能质量过滤**：基于领域本体论的正则表达式模式匹配

### 📊 支持的领域
- **教育**：教学法、课程、学习理论
- **环境**：可持续性、气候变化、保护生物学
- **量子计算**：量子比特、叠加、纠缠
- **金融**：投资、市场、风险管理
- **医疗保健**：临床、患者护理、医学研究
- **人工智能**：算法、训练、神经网络
- **以及任何其他领域**！

### 🔧 技术架构

#### 本体论体系结构
```python
@dataclass
class DomainOntology:
    domain: str                           # 领域名称
    core_concepts: List[str]             # 核心概念 (权重最高)
    subdomains: List[str]               # 子领域
    keywords: List[str]                 # 通用关键词 (中等权重)
    technical_terms: List[str]          # 技术术语 (高权重)
    context_indicators: List[str]       # 上下文指标 (基础权重)
    quality_patterns: List[str]         # 质量过滤正则表达式
```

#### 多层过滤管道
1. **URL过滤**：移除不相关的网站
2. **内容提取**：使用 Trafilatura 提取正文
3. **语言过滤**：仅保留英文内容
4. **领域内容过滤**：基于本体论的智能过滤
5. **长度过滤**：确保内容充足
6. **质量过滤**：多重质量评估
7. **LLM评分**（可选）：高级语义评估
8. **PII移除**：隐私保护
9. **去重**：移除重复内容

## 📖 使用方法

### 基本用法

```bash
# 创建教育领域数据集
python finewebdata.py --domain education --mode local

# 创建环境科学数据集
python finewebdata.py --domain environment --mode slurm --use-llm-scoring --gpu

# 创建量子计算数据集
python finewebdata.py --domain "quantum computing" --year 2024

# 基准测试领域检测性能
python finewebdata.py --domain education --benchmark
```

### Slurm 集群模式使用

FineWeb-Data 支持在 Slurm 集群上进行大规模分布式处理，能够处理完整的 Common Crawl dumps (数亿网页)。

#### 基本 Slurm 用法

```bash
# 基本 Slurm 处理
python finewebdata.py --domain "data law" --mode slurm --year 2025

# 指定集群名称
python finewebdata.py \
    --domain education \
    --mode slurm \
    --cluster-name my-slurm-cluster \
    --year 2024
```

#### 高级 Slurm 配置

```bash
# 生产级环境科学数据集 (推荐配置)
python finewebdata.py \
    --domain environment \
    --mode slurm \
    --year 2025 \
    --output-bucket fineweb-environment \
    --min-words 250 \
    --domain-threshold 3 \
    --compression gzip \
    --non-interactive \
    --use-llm-scoring \
    --gpu \
    --domain-threshold-llm 3.5
```

#### Slurm 模式特性

- **自动资源分配**: 根据数据大小自动分配 CPU/内存/GPU
- **分布式处理**: 多节点并行处理数亿网页
- **容错机制**: 单任务失败不影响整体作业
- **监控日志**: 详细的处理统计和进度跟踪
- **GPU 支持**: 可选 GPU 加速 LLM 评分

#### Slurm 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--mode slurm` | 使用 Slurm 集群模式 | `--mode slurm` |
| `--cluster-name` | Slurm 集群名称 | `--cluster-name production-cluster` |
| `--gpu` | 使用 GPU 分区 | `--gpu` (需要 LLM 支持) |
| `--non-interactive` | 自动选择最新 dump | `--non-interactive` |
| `--output-bucket` | S3 输出桶 | `--output-bucket my-bucket` |

#### Slurm vs 本地模式对比

| 特性 | 本地模式 | Slurm 模式 |
|------|---------|------------|
| **数据规模** | 40K 文档采样 | 全量处理 (数亿网页) |
| **处理速度** | 分钟级 | 小时到天级 |
| **资源需求** | 基本 CPU/内存 | 集群资源 |
| **适用场景** | 测试/开发 | 生产数据集生成 |
| **输出质量** | 采样评估 | 完整高质量数据集 |

#### Slurm 作业监控

```bash
# 查看作业状态
squeue -u $USER

# 查看作业详情
sacct -j <job_id>

# 查看日志
tail -f logs/base_processing/*/slurm_logs/slurm-<job_id>.out
```

### 命令行参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--domain` | string | **必需** | 目标领域 (如: education, environment, "quantum computing") |
| `--mode` | choice | local | 执行模式: local 或 slurm |
| `--year` | int | - | 处理指定年份的 dumps |
| `--dumps` | list | - | 具体要处理的 Common Crawl dumps |
| `--output-bucket` | string | fineweb-data | S3 输出桶名称 |
| `--min-words` | int | 200 | 文档最小字数 |
| `--domain-threshold` | int | 2 | 领域关键词最小数量 |
| `--compression` | choice | gzip | 输出压缩格式 |
| `--benchmark` | flag | - | 运行基准测试 |
| `--use-llm-scoring` | flag | - | 使用 LLM 领域相关性评分 |
| `--gpu` | flag | - | 在 Slurm 中使用 GPU 分区 |

## 🧠 本体论生成流程

### 1. LLM 分析阶段
当用户指定新领域时，系统会：
1. 向 GPT-4 发送详细提示，要求生成结构化本体
2. 分析领域的多个维度：学术、实践、产业、技术
3. 生成 5 个 JSON 类别的内容

### 2. 本体构建示例 (教育领域)

```json
{
  "core_concepts": ["learning", "teaching", "curriculum", "assessment", "pedagogy"],
  "subdomains": ["k-12 education", "higher education", "special education"],
  "keywords": ["student", "teacher", "classroom", "lesson", "curriculum"],
  "technical_terms": ["bloom's taxonomy", "constructivism", "scaffolding"],
  "context_indicators": ["educational research", "teaching methods", "learning outcomes"],
  "quality_patterns": ["\\b(phd|masters|bachelors)\\b", "\\b(curriculum|pedagogy)\\b"]
}
```

### 3. 评分算法

领域相关性评分采用加权算法：
- **核心概念**：权重 3.0 (最高优先级)
- **技术术语**：权重 2.0 (专业术语)
- **关键词**：权重 1.5 (通用术语)
- **上下文指标**：权重 1.0 (基础指标)

## 📊 基准测试结果

运行 `--benchmark` 标志可获得详细的领域检测性能分析：

```
🏆 FineWeb-Data Benchmark Suite for Domain: education
📊 Benchmark Results Summary:
  Total samples: 8 (5 education + 3 non-education)

🎯 Domain Content Detection:
  Quality filter: 5/5 (100.0%) true positive rate
  Content filter: 5/5 (100.0%) true positive rate

🚫 False Positive Detection:
  Quality filter: 0/3 (0.0%) false positive rate
  Content filter: 0/3 (0.0%) false positive rate
```

## 🔧 系统要求

### 软件依赖
- Python 3.8+
- datatrove
- openai (可选，用于本体生成)
- requests
- dotenv

### 硬件要求
- **本地模式**：4GB RAM，基本 CPU
- **Slurm 模式**：集群环境，视数据集大小而定
- **LLM 增强模式**：GPU 支持 (推荐 A100/H100)

## 🏗️ 架构优势

### 对比传统方法
| 传统关键词过滤 | FineWeb-Data 本体论方法 |
|----------------|-------------------------|
| 静态关键词列表 | 动态 LLM 生成本体 |
| 单层过滤 | 多层级过滤体系 |
| 通用质量评估 | 领域特定质量模式 |
| 手动调整 | 自动优化 |

### 扩展性
- **新领域**：只需指定领域名称，系统自动生成本体
- **自定义调整**：可覆盖生成的关键词和模式
- **多语言支持**：可扩展到其他语言
- **集成能力**：可与现有 ML 管道无缝集成

## 📚 数据源选择：为什么从 Common Crawl 开始？

在 FineData 项目中，我们选择 Common Crawl 作为数据集生成的起点，这是基于其独特优势和实际需求做出的战略决策。下面详细说明原因，这些考虑直接支持了项目在构建领域特定数据集（尤其是针对 AI 智能体训练的海量数据需求）时的效率、可靠性和可扩展性。

### 1. **海量规模和覆盖范围**
- Common Crawl 是全球最大的公开网页存档，每月爬取数十亿网页，累计数据量超过数百 PB。这为 FineWeb-Data 提供了几乎无限的原始数据源，能够轻松生成 TB 级领域特定数据集。

- **为什么重要？** AI 智能体部署需要数百万到数十亿的样本进行预训练和微调。Common Crawl 的规模直接响应了这一需求，避免了从小规模或单一来源开始的局限性。例如，在处理如“教育”或“量子计算”等领域时，我们可以从数亿网页中过滤出高相关内容，确保数据集的深度和多样性。
- 如果从零开始爬取数据，不仅资源消耗巨大，还可能面临爬取频率限制或网站封禁的问题。Common Crawl 作为起点，让我们跳过这些障碍，直奔高质量过滤。

### 2. **免费、开放和合规性**
- Common Crawl 数据是公开免费的，由非营利组织维护，并以标准 WARC 格式存储。这意味着 FineWeb-Data 无需支付高额数据获取费用，也避免了知识产权纠纷。
- **为什么重要？** 项目强调隐私保护（如 PII 移除）和合规性。Common Crawl 的数据已预先处理为可重用格式，符合开源精神，便于集成如 datatrove 库的多层次过滤管道。同时，它支持 FineWeb-Data 的端到端服务模式，从需求表单到 Hugging Face 交付，都能保持低成本和高效率。
- 相比商业数据提供商（如付费 API 或专有爬虫），Common Crawl 降低了进入门槛，让用户（尤其是研究者和中小企业）更容易访问海量数据，支持 AI 智能体的民主化部署。

### 3. **多样性和实时性**
- Common Crawl 覆盖全球网站，包括学术、新闻、博客和技术论坛，主题多样性极高。这为 FineWeb-Data 的 LLM 驱动本体论生成提供了丰富原料，能动态过滤出特定领域（如医疗或金融）的语义相关内容。
- 它定期更新（每月一个 dump），允许 FineWeb-Data 指定年份或特定 dump（如 `--year 2025`），确保数据新鲜度。这对 AI 智能体训练至关重要，因为过时数据可能导致模型偏差。
- **为什么重要？** 通用数据集往往缺乏领域深度，而 Common Crawl 的多样性结合 FineWeb-Data 的智能过滤（如质量阈值和 LLM 评分），能产生高度针对性的输出，减少噪声并提升智能体的泛化能力。

### 4. **技术兼容性和效率**
- Common Crawl 与现有工具生态高度兼容：FineWeb-Data 基于 datatrove 管道，能无缝处理 WARC 文件，进行 URL 过滤、内容提取（使用 Trafilatura）和去重。
- 在 Slurm 集群模式下，Common Crawl 的分布式存储（S3）允许高效并行处理数亿网页，生成压缩 JSONL 输出。这直接支持项目的生产级扩展，满足 AI 智能体对大数据量的实际需求。
- **为什么重要？** 如果使用其他起点（如自定义爬虫），需要额外处理数据清洗和标准化。Common Crawl 简化了这一步，让 FineWeb-Data 专注于亮点功能，如基准测试和实时预览，加速从需求到交付的周期。

### 5. **实际风险缓解和未来证明**
- 爬取数据涉及法律风险（如 GDPR 合规或 robots.txt 违反），Common Crawl 已处理这些问题，提供干净起点。
- 随着 AI 智能体向多模态演进，Common Crawl 的文本+元数据格式易于扩展（未来可整合图像或多语言）。这确保 FineWeb-Data 的架构在数据需求爆炸式增长时保持领先。

总之，选择 Common Crawl 作为起点让 FineWeb-Data 成为高效、可靠的 AI 数据服务，完美匹配项目中强调的“大规模可扩展性”和“实际数据需求”。它将海量公开数据转化为定制化资产，帮助用户快速构建和部署 AI 智能体。

## 🚨 注意事项

1. **API 密钥**：如使用 LLM 功能，需要有效的 OpenAI API 密钥
2. **成本考虑**：LLM 调用会产生费用，建议缓存本体
3. **数据量**：大型数据集需要集群环境
4. **质量保证**：建议对新领域运行基准测试


---

**示例输出数据集结构：**
```
s3://finedata/base_processing/output/CC-MAIN-2025-01/
├── _SUCCESS
├── part-00000.jsonl.gz
├── part-00001.jsonl.gz
└── ...

# 每行 JSON 格式:
{
  "text": "Full article text...",
  "url": "https://example.com/article",
  "dump": "CC-MAIN-2025-01",
  "dataset": "finedata-education",
  "llm_domain_score": 4.2
}
```
