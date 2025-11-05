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
