#!/bin/bash

# 修复S3 Bucket Policy配置脚本
# 处理Block Public Access设置冲突

set -e

echo "🔧 修复FineData S3存储桶配置..."

BUCKET_NAME="fineweb-data"
FRONTEND_DOMAIN="http://54.159.47.120:23000"

echo "📦 目标存储桶: $BUCKET_NAME"

# 步骤1: 首先获取当前的Block Public Access设置
echo "📋 检查当前Block Public Access设置..."
aws s3api get-public-access-block --bucket "$BUCKET_NAME" || echo "无法获取设置，可能没有权限"

# 步骤2: 临时修改Block Public Access设置
echo "⚠️  临时修改Block Public Access设置..."
aws s3api put-public-access-block --bucket "$BUCKET_NAME" --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": false,
    "RestrictPublicBuckets": false
}' || echo "修改Block Public Access失败，请在AWS控制台手动操作"

# 步骤3: 应用Bucket Policy
echo "📋 应用Bucket Policy..."
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

aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy "$POLICY"

# 步骤4: 恢复Block Public Access设置（保持安全）
echo "🔒 恢复Block Public Access设置..."
aws s3api put-public-access-block --bucket "$BUCKET_NAME" --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
}' || echo "恢复Block Public Access失败，请在AWS控制台手动恢复"

echo "✅ 配置完成！"
echo ""
echo "🔍 验证步骤："
echo "1. 在AWS控制台检查存储桶的Block Public Access设置"
echo "2. 确认Bucket Policy已应用"
echo "3. 测试benchmark样本下载功能"
