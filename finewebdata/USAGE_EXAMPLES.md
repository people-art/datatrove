# FineWeb-Data 使用示例

## 完整工作流程

### 1. 生成领域本体和数据集

```bash
cd finewebdata

# 示例1: 生成教育领域数据集
python finewebdata.py --domain education --year 2024 --mode local

# 示例2: 生成环境科学数据集（使用LLM增强）
python finewebdata.py --domain environment --year 2024 --mode slurm --use-llm-scoring --gpu

# 示例3: 生成量子计算数据集
python finewebdata.py --domain "quantum computing" --year 2024 --mode local

# 示例4: 批量处理多个领域
for domain in "machine learning" "artificial intelligence" "data science"; do
    python finewebdata.py --domain "$domain" --year 2024 --mode local
done
```

### 2. 基准测试和验证

```bash
# 运行领域检测基准测试
python finewebdata.py --domain education --benchmark

# 测试本体生成功能
python test_ontology.py

# 测试OpenAI集成
python test_openai.py
```

### 3. 发布到HuggingFace

```bash
# 上传教育领域数据集
./publish_to_hf.sh --domain education --latest

# 上传所有可用数据集
./publish_to_hf.sh --all

# 上传特定dump
./publish_to_hf.sh --dump CC-MAIN-2024-18

# 使用自定义仓库名称
./publish_to_hf.sh --name my-fineweb-collection --latest
```

## 实际使用场景

### 场景1: 学术研究数据集

**目标**: 为NLP研究创建教育相关的训练数据

```bash
# 1. 生成教育数据集
python finewebdata.py --domain education --year 2024 --mode slurm --use-llm-scoring --gpu

# 2. 上传到HF
./publish_to_hf.sh --domain education --latest

# 3. 在研究中使用
from datasets import load_dataset
dataset = load_dataset("your_username/fineweb-data-education")
```

### 场景2: 领域特定模型训练

**目标**: 为医疗AI模型准备专业数据集

```bash
# 1. 生成多个相关领域的数据集
for domain in "healthcare" "medical" "biology" "pharmacy"; do
    python finewebdata.py --domain "$domain" --year 2024 --mode slurm
done

# 2. 批量上传
./publish_to_hf.sh --all

# 3. 合并多个领域的数据集用于训练
from datasets import load_dataset, concatenate_datasets

datasets = []
for domain in ["healthcare", "medical", "biology", "pharmacy"]:
    try:
        ds = load_dataset(f"your_username/fineweb-data-{domain}")
        datasets.append(ds)
    except:
        continue

combined_dataset = concatenate_datasets(datasets)
```

### 场景3: 内容分析和研究

**目标**: 分析特定领域的内容趋势

```bash
# 1. 生成时间序列数据集
for year in 2023 2024; do
    python finewebdata.py --domain "artificial intelligence" --year $year --mode slurm
done

# 2. 上传所有年份的数据
./publish_to_hf.sh --domain "artificial intelligence" --all

# 3. 进行内容分析
import pandas as pd
from datasets import load_dataset

# 加载数据进行趋势分析
datasets_2023 = load_dataset("your_username/fineweb-data-ai-cc2023*")
datasets_2024 = load_dataset("your_username/fineweb-data-ai-cc2024*")

# 分析AI领域内容随时间的变化
```

## 高级配置

### 自定义过滤参数

```bash
# 降低关键词阈值以提高召回率
python finewebdata.py --domain "renewable energy" --domain-threshold 1 --year 2024

# 增加最小词数要求
python finewebdata.py --domain "academic research" --min-words 300 --year 2024

# 使用自定义输出桶
python finewebdata.py --domain "finance" --output-bucket my-custom-bucket --year 2024
```

### 集群部署

```bash
# 使用Slurm集群进行大规模处理
python finewebdata.py \
    --domain "machine learning" \
    --year 2024 \
    --mode slurm \
    --use-llm-scoring \
    --gpu \
    --cluster-name my-cluster
```

### 环境配置

```bash
# 创建.env文件
cat > .env << EOF
# OpenAI配置
OPENAI_API_KEY=sk-your-key-here

# HuggingFace配置
HF_TOKEN=hf_your-token-here
HF_USERNAME=your-username-here

# AWS配置（如果需要）
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
EOF
```

## 性能优化

### 大规模处理

```bash
# 处理多个年份的数据
for year in {2022..2024}; do
    python finewebdata.py --domain "climate science" --year $year --mode slurm &
done
wait

# 批量上传
./publish_to_hf.sh --domain "climate science" --all
```

### 内存优化

```bash
# 减少并行任务数以节省内存
export CUDA_VISIBLE_DEVICES=0,1  # 只使用2个GPU
python finewebdata.py --domain "large corpus" --mode slurm --gpu
```

## 监控和调试

### 检查处理状态

```bash
# 查看S3中的处理结果
aws s3 ls s3://fineweb-data/base_processing/output/ --recursive

# 检查日志
tail -f finewebdata/logs/base_processing/*/logs/task_*.log
```

### 验证数据质量

```bash
# 运行基准测试
python finewebdata.py --domain "your domain" --benchmark

# 手动检查样本数据
python3 -c "
import json
import boto3
s3 = boto3.client('s3')
obj = s3.get_object(Bucket='fineweb-data', Key='base_processing/output/CC-MAIN-2024-18/part-00000.jsonl.gz')
# 检查数据质量...
"
```

## 集成到现有工作流

### CI/CD集成

```yaml
# .github/workflows/fineweb-data.yml
name: Generate FineWeb-Data
on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日运行
  workflow_dispatch:

jobs:
  generate-dataset:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate dataset
        run: |
          cd finewebdata
          python finewebdata.py --domain education --year 2024 --mode local
      - name: Upload to HF
        run: |
          cd finewebdata
          ./publish_to_hf.sh --domain education --latest
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
          HF_USERNAME: ${{ secrets.HF_USERNAME }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

这个完整的示例展示了如何使用 FineWeb-Data 系统从原始网页数据生成高质量的领域特定数据集，并发布到 HuggingFace Hub 供研究和应用使用。
