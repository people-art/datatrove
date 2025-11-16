# S3 Bucket Policy 手动配置指南

## 问题分析
当前错误是因为存储桶启用了"Block public and cross-account access to buckets and objects through any public bucket or access point policies"设置，这阻止了设置任何公共bucket policy。

## 解决方案：分步手动配置

### 步骤1: 临时修改Block Public Access设置

1. **打开AWS S3控制台**
2. **选择存储桶** `fineweb-data`
3. **进入 "Permissions" 标签页**
4. **找到 "Block public access (bucket settings)" 部分**
5. **点击 "Edit"**
6. **临时取消勾选**: "Block public and cross-account access to buckets and objects through any public bucket or access point policies"
7. **保持其他设置不变**:
   - ✅ Block all public access: On
   - ✅ Block public access to buckets and objects granted through new access control lists (ACLs): On
   - ✅ Block public access to buckets and objects granted through any access control lists (ACLs): On
   - ✅ Block public access to buckets and objects granted through new public bucket or access point policies: On
   - ❌ Block public and cross-account access to buckets and objects through any public bucket or access point policies: **Off** (临时)
8. **点击 "Save changes"**

### 步骤2: 配置Bucket Policy

在同一个页面，找到"Bucket policy"部分：

1. **点击 "Edit"**
2. **粘贴以下policy**:

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
                    "aws:Referer": "http://54.159.47.120:23000/*"
                }
            }
        }
    ]
}
```

3. **点击 "Save changes"**

### 步骤3: 恢复Block Public Access设置

1. **回到 "Block public access" 部分**
2. **点击 "Edit"**
3. **重新勾选**: "Block public and cross-account access to buckets and objects through any public bucket or access point policies"
4. **点击 "Save changes"**

## 验证配置

### 方法1: 通过AWS CLI验证
```bash
# 检查Bucket Policy
aws s3api get-bucket-policy --bucket fineweb-data

# 检查Block Public Access设置
aws s3api get-public-access-block --bucket fineweb-data
```

### 方法2: 通过AWS控制台验证
1. 在S3控制台查看存储桶的Bucket Policy
2. 确认Block Public Access设置已恢复

### 方法3: 功能测试
1. 在应用中创建新的benchmark任务
2. 等待任务完成
3. 点击"Download Sample"按钮
4. 确认能正常下载样本文件

## 安全说明

- **临时措施**: 步骤1中的设置修改是临时的，只在配置policy期间需要
- **安全恢复**: 步骤3确保了安全设置的恢复
- **最小权限**: Policy只允许从指定域名下载特定文件类型
- **Referer保护**: 通过HTTP Referer头限制访问来源

## 故障排除

### 如果仍然失败
1. 检查IAM用户权限是否包含`s3:PutBucketPolicy`
2. 确认Block Public Access设置确实被临时修改
3. 等待几分钟让设置生效

### 如果需要生产环境配置
将policy中的域名替换为生产域名：
```json
"aws:Referer": "https://your-production-domain.com/*"
```
