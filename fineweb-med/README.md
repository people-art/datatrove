# FineWeb-Med

基于FineWeb方法论的医疗数据集处理管道，用于从Common Crawl中提取高质量的医疗相关文本数据。

## 主要改进

相比原有的 `fineweb-med.py`，新版本 `fineweb-med-new.py` 包含以下重大改进：

### 1. 增强的医疗过滤系统
- **扩展医疗关键词**: 120+ 个专业医疗术语，包括MeSH主题词表
- **智能内容检测**: 多重验证（关键词密度 + 上下文分析 + 质量启发式）
- **MeSH术语集成**: 使用医学主题词表进行精确分类
- **LLM相关性评分**: 可选的LLM-based评分系统（阈值≥3.0）

### 2. 多层质量保证
- **困惑度过滤**: 确保内容质量（PerplexityFilter）
- **单字概率过滤**: 基于语言模型的概率评分
- **医疗启发式**: ICD编码、临床试验模式、证据等级检测
- **多级过滤**: URL → 语言 → 重复 → 质量 → 医疗相关性 → PII

### 3. 高级隐私与合规
- **增强PII移除**: HIPAA合规的个人身份信息处理
- **多遍处理**: 确保彻底移除敏感信息
- **医疗数据保护**: 专门针对医疗记录的隐私保护

### 4. 智能数据源管理
- **年份选择**: 只需指定年份，自动发现可用dumps
- **交互式选择**: 支持all/ranges/specific dump选择
- **非交互模式**: 适合自动化脚本
- **多dump支持**: 可同时处理多个Common Crawl dumps

### 5. 基准测试与验证
- **医疗LLM评估**: 内置基准测试套件
- **过滤器性能分析**: 精确度、召回率和F1分数
- **质量指标**: 医疗相关性评分分布
- **自动化报告**: 生成详细的质量报告

### 6. 生产级架构
- **参数化配置**: 所有过滤器阈值可配置
- **资源优化**: 针对医疗数据规模优化的Slurm配置
- **错误处理**: 优雅的失败处理和恢复机制
- **监控与日志**: 详细的处理统计和排除原因

## 医疗关键词过滤

脚本使用扩展的医疗关键词列表进行内容过滤：

```python
MEDICAL_KEYWORDS = [
    "medical", "diagnosis", "treatment", "patient", "doctor", "symptom", "therapy",
    "prescription", "clinical", "healthcare", "medicine", "pharmaceutical",
    "hospital", "clinic", "nurse", "surgery", "disease", "disorder", "condition",
    "medication", "drug", "vaccine", "epidemic", "pandemic", "health", "wellness"
]
```

## 使用方法

### 本地测试模式

默认情况下，脚本配置为本地测试模式，使用 `LocalPipelineExecutor`：

1. 配置环境变量：
   ```bash
   # 在 .env 文件中设置
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   AWS_DEFAULT_REGION=us-east-1
   ```

2. 修改配置参数：
   ```python
   DUMP_TO_PROCESS = "CC-MAIN-2023-50"  # 指定要处理的Common Crawl dump
   MAIN_OUTPUT_PATH = "s3://your-bucket"  # 设置输出路径
   ```

3. 运行脚本：
   ```bash
   python fineweb-med-new.py
   ```

**注意**:
- 本地模式会限制处理文档数量（`limit=100`），适合测试和开发
- 脚本使用了 `if __name__ == '__main__':` 保护，确保多进程正确工作

### 命令行参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--mode` | `local` \| `slurm` | `local` | 执行模式：本地测试或Slurm集群 |
| `--cluster-name` | string | `fineweb-med-slurm-cluster` | Slurm集群名称（仅在slurm模式使用） |
| `--dump` | string | `CC-MAIN-2023-50` | 要处理的Common Crawl dump |
| `--output-bucket` | string | `fineweb-med` | 输出数据的S3存储桶名称 |

### 生产模式（集群处理）

要进行完整的生产级处理，需要：

#### 1. 设置AWS Slurm集群

使用提供的自动化脚本设置Slurm集群：

```bash
cd fineweb-med

# 创建Slurm集群（需要AWS凭据和配额）
./setup_slurm_cluster.sh --create

# 等待集群创建完成（约30分钟）
# 脚本会显示集群状态和SSH访问信息
```

#### 2. 配置和运行生产脚本

**推荐方法：使用自动化脚本**

```bash
cd fineweb-med

# 一键运行完整的Slurm作业（推荐）
./run_on_slurm.sh

# 这会自动：
# 1. 检查集群状态
# 2. 复制文件到集群
# 3. 提交Slurm作业
# 4. 开始监控
```

**手动运行方法：**

```bash
# 本地测试模式（默认）
conda activate datatrove
python fineweb-med-new.py

# 指定年份进行本地测试
python fineweb-med-new.py --year 2024 --non-interactive

# 直接在集群head节点上运行
ssh -i ~/.ssh/AWS-Keys ec2-user@<HEAD_NODE_IP>
cd /shared/fineweb-med
python fineweb-med-new.py --mode slurm --year 2024 --output-bucket fineweb-med --non-interactive

# 使用sbatch提交作业
sbatch slurm_job.sh
```

#### 3. 监控作业进度

```bash
# 在集群head节点上监控
squeue                    # 查看作业队列
sinfo                     # 查看集群状态
tail -f logs/base_processing/CC-MAIN-2023-50/slurm_logs/*.out  # 查看作业日志
```

#### 4. 清理资源

处理完成后清理集群：

```bash
# 删除集群和所有相关资源
./setup_slurm_cluster.sh --cleanup
```

### 生产模式配置详情

当前生产配置包括：
- **4000个并行任务**用于基础处理
- **完整的去重pipeline**（4阶段）
- **S3存储**用于大数据集
- **多阶段依赖**确保顺序执行
- **优化的资源分配**（内存、时间、CPU）

### 预期处理时间

- **基础处理**: 15-20小时（4000任务并行）
- **去重阶段1**: 8小时（签名生成）
- **去重阶段2**: 4小时（分桶）
- **去重阶段3**: 20小时（聚类分析）
- **去重阶段4**: 8小时（最终过滤）
- **总计**: 55-60小时

### 成本估算

- **EC2实例**: c5.large head节点 + 最多10个c5.xlarge计算节点
- **存储**: S3存储（处理期间约500GB）
- **网络**: 数据传输费用
- **预估成本**: $200-500（取决于实际运行时间和实例使用率）

## 处理流程

### 第一阶段：基础处理
1. 从Common Crawl读取WARC文件
2. URL过滤
3. 文本提取（Trafilatura，2秒超时）
4. 语言过滤（只保留英文）
5. 医疗内容过滤
6. 长度过滤（≥200单词）
7. 质量过滤（重复、C4、FineWeb）
8. 保存过滤后的数据

### 第二阶段：去重处理
1. 生成Minhash签名
2. 分桶处理
3. 聚类分析找出重复文档
4. 过滤重复内容
5. PII移除
6. 生成最终数据集

## 输出结构

```
s3://your-bucket/
├── base_processing/
│   ├── output/                    # 过滤后的原始数据
│   ├── removed/                   # 被过滤掉的数据
│   └── logs/                      # 处理日志
├── minhash/
│   ├── signatures/                # Minhash签名
│   ├── buckets/                   # 分桶数据
│   ├── remove_ids/                # 要移除的文档ID
│   └── deduped_output/            # 去重后的最终数据
└── logs/
    └── minhash/                   # 去重日志
```

## 📤 HuggingFace上传

### 上传功能特性

- **🏥 专业数据集卡片**: 参考FineWeb样式，包含完整的元数据和使用说明
- **📊 详细统计分析**: 自动分析文档数量、token分布、内容来源等
- **🌐 域名分析**: 识别主要内容来源网站
- **📈 Token统计**: 完整的token分布分析（最小值、最大值、中位数等）
- **🏷️ 自动标签**: 支持多任务类别标注
- **📝 专业文档**: 包含使用示例、引用信息和最佳实践

### 第一步：设置环境变量

1. **复制环境变量模板**：
   ```bash
   cp env.example .env
   ```

2. **编辑.env文件**：
   ```bash
   vim .env  # 或使用你喜欢的编辑器
   ```

3. **设置HuggingFace配置**：
   ```bash
   # 在.env文件中设置：
   HF_USERNAME=your_actual_huggingface_username  # 从 https://huggingface.co/settings/profile 获取
   HF_TOKEN=hf_your_token_here                   # 从 https://huggingface.co/settings/tokens 获取
   ```

### 第二步：验证账户配置

```bash
cd fineweb-med

# 检查账户信息和权限（自动从.env读取）
python check_hf_account.py

# 或者手动指定token
python check_hf_account.py --token your_token_here
```

这个脚本会：
- ✅ 验证token是否有效
- 👤 显示你的真实用户名
- 🔧 测试仓库创建权限
- 📝 提供正确的配置信息

### 第三步：运行上传

现在.env文件已经配置好，直接运行上传脚本：

```bash
# 运行上传脚本
./example_upload.sh

# 或者手动运行
python upload_to_huggingface.py \
  --input-dir ../data/fineweb-med/base_processing/output/CC-MAIN-2023-50 \
  --repo-name your-username/fineweb-med \
  --token $HF_TOKEN
```

### 生成的数据集卡片包含

1. **数据集概述** - 规模、内容类型、创建方法
2. **详细统计** - 文档数、token数、分布分析、主要来源
3. **处理流程** - 完整的8步处理pipeline说明
4. **数据格式** - 字段定义和类型说明
5. **使用示例** - 加载和过滤代码示例
6. **创建信息** - 基本原理、来源数据、标注方法
7. **使用考虑** - 社会影响、偏见讨论、局限性
8. **引用信息** - BibTeX格式引用

## 参数优化

针对医疗数据集的特点，脚本进行了以下优化：

- **超时时间**: Trafilatura超时从1秒增加到2秒（医疗页面可能更复杂）
- **任务数量**: 从8000减少到4000（医疗数据量相对较少）
- **Minhash配置**: 桶数量从14减少到10，适应医疗数据集规模
- **内存配置**: 增加内存分配以处理更复杂的医疗文本
- **处理时间**: 相应调整了Slurm作业时间限制

## 技术说明

### 多进程处理

脚本使用Python的 `multiprocessing` 模块进行并行处理。为了避免子进程重新执行整个脚本，采用了标准的Python多进程模式：

```python
if __name__ == '__main__':
    main_processing_executor.run()
```

这种模式确保：
- 主进程正确启动子进程
- 子进程不会重新执行脚本初始化代码
- 多进程环境正确设置

### 错误处理

如果遇到类似错误：
```
RuntimeError: An attempt has been made to start a new process before the current process has finished its bootstrapping phase.
```

这通常表示多进程代码没有正确保护在 `if __name__ == '__main__':` 块中。

## 前提条件

### AWS配置
1. **AWS CLI**: 已安装并配置凭据
2. **EC2配额**: 至少10个c5.xlarge实例的配额
3. **SSH密钥对**: 在AWS中创建密钥对（如"AWS-Keys"）
4. **IAM权限**: 包括EC2、EFS、S3、CloudFormation的完整权限

### 环境要求
- **Python 3.10+**
- **Conda环境**: `datatrove`环境已激活
- **AWS ParallelCluster**: 脚本会自动安装

## 注意事项

1. **依赖安装**: 确保安装了所有必要的依赖，包括datatrove及其依赖项
2. **存储空间**: 处理大型Common Crawl dump需要大量S3存储空间
3. **计算资源**: 需要足够的Slurm集群资源进行分布式处理
4. **成本考虑**: S3存储和传输成本，以及计算资源成本
5. **多进程**: 本地模式使用2个worker进程，避免系统资源过度使用
6. **网络安全**: 确保防火墙规则允许必要的AWS服务通信

## 故障排除

### 常见问题

1. **Slurm命令未找到**: 确认在集群head节点上运行，而非本地机器
2. **AWS配额不足**: 检查EC2实例配额，可能需要申请增加
3. **SSH连接失败**: 确认密钥对名称和文件路径正确
4. **集群创建失败**: 检查CloudFormation权限和网络配置

### 监控和调试

```bash
# 查看集群状态
pcluster describe-cluster --cluster-name fineweb-med-slurm-cluster --region us-east-1

# 查看集群日志
pcluster get-cluster-log-events --cluster-name fineweb-med-slurm-cluster --region us-east-1

# SSH到head节点
ssh -i ~/.ssh/AWS-Keys ec2-user@<HEAD_NODE_IP>

# 在head节点上查看作业
squeue -u $USER
sacct -j <JOB_ID>  # 查看作业详情
```

### 清理和重置

如果遇到问题，可以完全清理并重新开始：

```bash
# 删除集群
./setup_slurm_cluster.sh --cleanup

# 等待清理完成（约15分钟）
# 然后重新创建
./setup_slurm_cluster.sh --create
```

## 比较

| 特性 | fineweb-med.py | fineweb-med-new.py (本地模式) | fineweb-med-new.py (生产模式) |
|------|---------------|------------------------------|------------------------------|
| 执行器 | LocalPipelineExecutor | LocalPipelineExecutor | SlurmPipelineExecutor |
| 质量过滤 | 基础过滤 | 完整的FineWeb过滤管道 | 完整的FineWeb过滤管道 |
| 去重 | 无 | 无（注释掉） | Minhash去重 |
| PII处理 | 无 | 无 | PII格式化 |
| 分布式处理 | 单机 | 单机 | 集群分布式 |
| 容错性 | 基础 | 基础 | 高级容错和监控 |
| 扩展性 | 有限 | 有限 | 高度可扩展 |
| 文档限制 | 无 | limit=100（测试用） | 无限制 |
| 适用场景 | 快速原型 | 开发测试 | 大规模生产 |
