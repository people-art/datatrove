# FineWeb-Data HuggingFace Upload Guide

## 概述

FineWeb-Data 提供了便捷的脚本将处理后的数据集上传到 HuggingFace Hub。

## 使用方法

### 基本用法

```bash
cd finewebdata

# 交互模式（推荐）
./publish_to_hf.sh

# 非交互模式
./publish_to_hf.sh --latest          # 上传最新dump
./publish_to_hf.sh --all            # 上传所有可用dumps
./publish_to_hf.sh --dump CC-MAIN-2024-18  # 上传指定dump

# 自定义数据集名称
./publish_to_hf.sh --name my-fineweb-data

# 按领域过滤
./publish_to_hf.sh --domain education --latest
```

### 环境配置

确保在项目根目录有 `.env` 文件：

```env
# HuggingFace 配置
HF_TOKEN=hf_your_token_here
HF_USERNAME=your_username_here

# OpenAI 配置（用于本体生成）
OPENAI_API_KEY=sk-your_openai_key_here
```

### 仓库命名规则

#### 单领域数据集
```bash
# 上传教育领域数据
./publish_to_hf.sh --domain education --latest

# 结果：https://huggingface.co/datasets/YOUR_USERNAME/fineweb-data-education
```

#### 多dump数据集
```bash
# 上传所有可用dumps
./publish_to_hf.sh --all

# 结果：每个dump创建单独仓库
# https://huggingface.co/datasets/YOUR_USERNAME/fineweb-data-cc202422
# https://huggingface.co/datasets/YOUR_USERNAME/fineweb-data-cc202418
```

#### 自定义命名
```bash
# 使用自定义名称
./publish_to_hf.sh --name my-custom-dataset --latest

# 结果：https://huggingface.co/datasets/YOUR_USERNAME/my-custom-dataset
```

## 脚本选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--latest` | 上传最新的dump | `./publish_to_hf.sh --latest` |
| `--all` | 上传所有可用dumps | `./publish_to_hf.sh --all` |
| `--dump ID` | 上传指定dump | `./publish_to_hf.sh --dump CC-MAIN-2024-18` |
| `--name NAME` | 自定义数据集名称 | `./publish_to_hf.sh --name my-data` |
| `--domain NAME` | 按领域过滤 | `./publish_to_hf.sh --domain education` |
| `--help` | 显示帮助信息 | `./publish_to_hf.sh --help` |

## 数据集结构

上传后的数据集包含以下信息：

```json
{
  "text": "处理后的文本内容...",
  "url": "https://原始网页URL",
  "dump": "CC-MAIN-2024-18",
  "dataset": "fineweb-education"
}
```

## 依赖要求

- AWS CLI 或 boto3（用于访问S3）
- HuggingFace 账户和 API token
- 有效的 `.env` 配置文件

## 故障排除

### 常见问题

1. **No dumps found in S3**
   ```
   原因：数据集还未处理完成
   解决：先运行 python finewebdata.py --domain <domain> --year <year>
   ```

2. **HF_TOKEN not found**
   ```
   原因：.env文件缺失或配置错误
   解决：检查项目根目录的.env文件
   ```

3. **Permission denied**
   ```
   原因：HF_TOKEN权限不足
   解决：确保token有write权限
   ```

### 调试模式

```bash
# 查看可用dumps
aws s3 ls s3://fineweb-data/base_processing/output/

# 检查.env配置
cat ../.env
```

## 批量上传

对于大规模数据上传，推荐使用 `--all` 选项：

```bash
# 上传所有可用dumps（会自动添加延迟避免限速）
./publish_to_hf.sh --all
```

脚本会在每次上传之间自动等待30秒以避免 HuggingFace 的速率限制。

## 自定义配置

可以修改脚本中的以下变量：

```bash
# 修改默认仓库名称
REPO_BASE_NAME="your-custom-name"

# 修改S3基础路径
BASE_DIR="s3://your-bucket/path"
```

## 集成到CI/CD

可以将上传脚本集成到自动化流程：

```yaml
# GitHub Actions 示例
- name: Upload to HuggingFace
  run: |
    cd finewebdata
    ./publish_to_hf.sh --latest
  env:
    HF_TOKEN: ${{ secrets.HF_TOKEN }}
    HF_USERNAME: ${{ secrets.HF_USERNAME }}
```
