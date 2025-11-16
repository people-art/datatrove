#!/bin/bash

# FineData S3 配置脚本
# 用于快速配置AWS S3存储桶权限

set -e

echo "🚀 开始配置FineData S3存储桶..."

# 配置变量
BUCKET_NAME="fineweb-data"
FRONTEND_DOMAIN="http://54.159.47.120:23000"

echo "📦 配置存储桶: $BUCKET_NAME"
echo "🌐 前端域名: $FRONTEND_DOMAIN"

# Bucket Policy配置
POLICY=$(cat <<EOF_POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowBenchmarkSampleDownloads",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/benchmark-*-sample.jsonl.gz",
            "Condition": {
                "StringLike": {
                    "aws:Referer": "$FRONTEND_DOMAIN/*"
                }
            }
        }
    ]
}
EOF_POLICY
)

echo "📋 应用Bucket Policy..."
aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy "$POLICY"

echo "✅ 配置完成！"
echo ""
echo "🔍 验证配置："
echo "1. 在AWS控制台检查 $BUCKET_NAME 的Bucket Policy"
echo "2. 创建新的benchmark任务"
echo "3. 尝试下载样本文件"
echo ""
echo "📝 注意：如果有生产域名，请添加相应的policy规则"
