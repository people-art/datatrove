# FineData S3 配置指南

## 存储桶结构

### 主要存储桶
- `fineweb-data`: 生产数据存储桶（数据集输出、benchmark中间文件）
- `finedata-dev-datasets`: 开发环境数据集存储桶
- `finedata-dev-samples`: 开发环境样本存储桶（已弃用，使用fineweb-data）

### 目录结构
```
fineweb-data/
├── base_processing/                    # 生产处理输出
│   ├── {domain}/output/               # 按领域组织的输出
│   └── logs/                          # 处理日志
├── benchmark-{job_id}-sample.jsonl.gz # benchmark样本文件
└── datasets/                          # 最终数据集文件

finedata-dev-datasets/
└── {order_id}/                        # 订单相关文件
    ├── dataset.jsonl.gz              # 数据集文件
    ├── metadata.json                 # 元数据
    └── invoice.pdf                   # 发票

## IAM 权限配置

### 应用程序需要的权限
创建IAM用户或角色，具有以下权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::fineweb-data/*",
                "arn:aws:s3:::finedata-dev-datasets/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::fineweb-data",
                "arn:aws:s3:::finedata-dev-datasets"
            ]
        }
    ]
}
```

### 开发环境权限
如果需要访问Common Crawl数据，添加：

```json
{
    "Effect": "Allow",
    "Action": [
        "s3:GetObject",
        "s3:ListBucket"
    ],
    "Resource": [
        "arn:aws:s3:::commoncrawl/*",
        "arn:aws:s3:::commoncrawl"
    ]
}
```

## Bucket Policy 配置

### fineweb-data 存储桶策略
由于启用了"Block all public access"，需要通过Bucket Policy控制访问：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowBenchmarkSampleDownloads",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::fineweb-data/benchmark-*-sample.jsonl.gz",
            "Condition": {
                "StringLike": {
                    "aws:Referer": [
                        "http://54.159.47.120:23000/*",
                        "https://your-production-domain.com/*"
                    ]
                }
            }
        },
        {
            "Sid": "AllowDatasetDelivery",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::fineweb-data/datasets/*",
            "Condition": {
                "StringLike": {
                    "aws:Referer": [
                        "https://your-production-domain.com/*"
                    ]
                }
            }
        }
    ]
}
```

### finedata-dev-datasets 存储桶策略
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowDevelopmentAccess",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::finedata-dev-datasets/*",
            "Condition": {
                "StringLike": {
                    "aws:Referer": "http://54.159.47.120:23000/*"
                }
            }
        }
    ]
}
```

## 环境变量配置

### .env 文件配置
```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_DATASETS=finedata-dev-datasets
S3_BUCKET_SAMPLES=fineweb-data
```

### Docker Compose 环境变量
```yaml
environment:
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
  - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
  - S3_BUCKET_DATASETS=finedata-dev-datasets
  - S3_BUCKET_SAMPLES=fineweb-data
```

## 存储桶设置

### Block Public Access 设置
对于生产环境，保持以下设置：
- ✅ Block all public access: **On**
- ✅ Block public access to buckets and objects granted through new access control lists (ACLs): **On**
- ✅ Block public access to buckets and objects granted through any access control lists (ACLs): **On**
- ✅ Block public access to buckets and objects granted through new public bucket or access point policies: **On**
- ✅ Block public and cross-account access to buckets and objects through any public bucket or access point policies: **On**

### Object Ownership
- Object Ownership: **Bucket owner enforced**
- ACLs: **Disabled**

## 验证配置

### 1. 测试S3连接
```python
import boto3
import os

# 测试连接
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
)

# 列出存储桶
response = s3.list_buckets()
print("Available buckets:")
for bucket in response['Buckets']:
    print(f"  - {bucket['Name']}")
```

### 2. 测试benchmark样本上传
```python
# 在应用中创建benchmark任务，检查：
# 1. 任务完成状态
# 2. S3中是否存在样本文件
# 3. 前端是否能下载样本文件
```

### 3. 测试数据集交付
```python
# 完成订单后检查：
# 1. 数据集文件是否上传到S3
# 2. HuggingFace链接是否正确生成
# 3. 发票是否能下载
```

## 故障排除

### 常见问题

1. **CORS错误**
   - 检查Bucket Policy中的Referer条件
   - 确认前端域名正确

2. **权限错误**
   - 验证IAM用户具有正确的权限
   - 检查存储桶策略

3. **文件不存在**
   - 检查benchmark任务是否成功完成
   - 验证S3上传代码是否正常执行

4. **网络连接问题**
   - 确认VPC配置允许S3访问
   - 检查安全组设置

## 成本优化

### 存储类
- **Standard**: 频繁访问的数据
- **Intelligent-Tiering**: 访问模式不确定的数据
- **Glacier**: 长期归档数据

### 生命周期规则
```json
{
    "Rules": [
        {
            "ID": "MoveOldBenchmarksToIA",
            "Status": "Enabled",
            "Prefix": "benchmark-",
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                }
            ]
        }
    ]
}
```
