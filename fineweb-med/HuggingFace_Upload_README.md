# FineWeb-Med HuggingFace上传指南

这个指南将帮助你将处理好的FineWeb-Med数据集上传到HuggingFace Hub。

## 📋 前提条件

### 1. HuggingFace账户和Token
1. 访问 [HuggingFace](https://huggingface.co) 并创建账户
2. 进入 Settings → Access Tokens 创建新的Token
3. 复制Token（格式类似：`hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

### 2. 安装依赖
```bash
pip install huggingface_hub datasets pandas
```

### 3. 准备数据集
确保你的数据集文件位于：
```
data/fineweb-med/base_processing/output/CC-MAIN-2023-50/
├── 00000.jsonl.gz
├── 00001.jsonl.gz
└── 00003.jsonl.gz
```

## 🚀 上传步骤

### 方法1：使用上传脚本（推荐）

```bash
cd fineweb-med

# 基本用法
python upload_to_huggingface.py \
    --input-dir ../data/fineweb-med/base_processing/output/CC-MAIN-2023-50 \
    --repo-name your-username/fineweb-med \
    --token hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 私有仓库
python upload_to_huggingface.py \
    --input-dir ../data/fineweb-med/base_processing/output/CC-MAIN-2023-50 \
    --repo-name your-username/fineweb-med-private \
    --token hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
    --private

# 自定义dump ID
python upload_to_huggingface.py \
    --input-dir ../data/fineweb-med/base_processing/output/CC-MAIN-2023-50 \
    --repo-name your-username/fineweb-med \
    --token hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
    --dump-id CC-MAIN-2023-50
```

### 方法2：手动上传

如果你更喜欢手动控制上传过程：

```python
from huggingface_hub import HfApi
from datasets import load_dataset
import os

# 设置token
os.environ['HF_TOKEN'] = 'hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 加载数据集
dataset = load_dataset(
    "json",
    data_files="data/fineweb-med/base_processing/output/CC-MAIN-2023-50/*.jsonl.gz"
)

# 上传到Hub
dataset.push_to_hub("your-username/fineweb-med")
```

## 📊 上传脚本参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--input-dir` | ✅ | - | 包含JSONL文件的目录路径 |
| `--repo-name` | ✅ | - | HF仓库名称（格式：username/dataset-name） |
| `--token` | ❌ | - | HF API token（也可通过环境变量设置） |
| `--private` | ❌ | False | 创建私有仓库 |
| `--merge-files` | ❌ | True | 是否合并所有文件为单个数据集 |
| `--dump-id` | ❌ | CC-MAIN-2023-50 | 数据源的Common Crawl dump ID |

## 🔧 环境变量配置

你也可以通过环境变量设置token：

```bash
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
python upload_to_huggingface.py --input-dir ../data/fineweb-med/base_processing/output/CC-MAIN-2023-50 --repo-name your-username/fineweb-med
```

## 📈 上传后的数据集信息

上传完成后，你的数据集将包含：

### 数据集卡片（README.md）
- 详细的数据集描述
- 处理流程说明
- 使用示例
- 统计信息
- 引用信息

### 数据集结构
```
your-username/fineweb-med/
├── README.md          # 数据集描述
├── data/
│   └── train-00000-of-00001.parquet  # 实际数据文件
└── dataset_info.json  # 元数据
```

### 数据格式
每个样本包含：
- `text`: 医疗相关文本内容
- `id`: 唯一标识符
- `metadata`: 包含来源、语言、token数等信息

## 🔍 验证上传结果

### 在HuggingFace Web界面
1. 访问 `https://huggingface.co/datasets/your-username/fineweb-med`
2. 检查数据集卡片是否正确显示
3. 查看数据预览

### 使用Python验证
```python
from datasets import load_dataset

# 加载你的数据集
dataset = load_dataset("your-username/fineweb-med")

print(f"数据集大小: {len(dataset['train'])}")
print(f"样本示例: {dataset['train'][0]}")
```

## 🛠️ 故障排除

### 常见问题

1. **Token错误**
   ```
   Error: Invalid token
   ```
   解决方案：检查token是否正确，可以在 [HF Tokens页面](https://huggingface.co/settings/tokens) 重新生成

2. **权限错误**
   ```
   Error: Repository not found
   ```
   解决方案：确保仓库名称格式正确（username/dataset-name）

3. **网络错误**
   ```
   Error: Connection timeout
   ```
   解决方案：检查网络连接，重试上传

4. **文件过大**
   ```
   Error: File too large
   ```
   解决方案：HF对单个文件有大小限制，脚本会自动分片处理

### 调试模式

启用详细日志：
```bash
export HF_HUB_VERBOSITY=debug
python upload_to_huggingface.py [参数...]
```

## 📝 最佳实践

1. **仓库命名**: 使用描述性的名称，如 `medical-web-dataset` 或 `fineweb-med-2023`
2. **隐私设置**: 医疗数据可能需要设为私有仓库
3. **版本控制**: 定期更新数据集版本
4. **文档完善**: 在数据集卡片中详细描述数据来源和处理方法

## 🎯 下一步

上传完成后，你可以：

1. **分享数据集**: 在社交媒体或学术论坛分享
2. **创建模型**: 使用数据集训练医疗领域模型
3. **协作开发**: 邀请其他研究者贡献
4. **版本更新**: 定期添加新数据

## 📞 支持

如果遇到问题，请检查：
- [HuggingFace文档](https://huggingface.co/docs)
- [Datasets库文档](https://huggingface.co/docs/datasets)
- GitHub Issues（如果有相关问题）

---

**恭喜！你的FineWeb-Med数据集现在可以在HuggingFace Hub上使用了！** 🎉
