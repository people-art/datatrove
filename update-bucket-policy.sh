#!/bin/bash

# 更新Bucket Policy - 移除Referer条件限制
# 因为S3的CORS预检请求不包含Referer头

set -e

echo "🔄 更新fineweb-data存储桶的Bucket Policy..."

BUCKET_NAME="fineweb-data"

# 简化的Bucket Policy - 只基于路径限制
POLICY=$(cat <<EOF_POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowBenchmarkSampleDownloads",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/benchmark-*-sample.jsonl.gz"
        }
    ]
}
EOF_POLICY
)

echo "📋 应用简化的Bucket Policy..."
aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy "$POLICY"

echo "✅ Bucket Policy已更新！"
echo ""
echo "📝 说明："
echo "   - 移除了Referer条件限制"
echo "   - 仍然只允许下载benchmark样本文件"
echo "   - 依赖Block Public Access提供安全保护"
echo ""
echo "🧪 测试：现在可以测试benchmark样本下载功能"
