#!/usr/bin/env python3
"""
调试S3 Bucket Policy配置
"""

import boto3
import requests
import json

def debug_s3_policy():
    print("🔍 调试S3 Bucket Policy...")
    
    bucket_name = "fineweb-data"
    test_file_key = "debug-benchmark-sample.jsonl.gz"
    
    # 创建S3客户端
    s3_client = boto3.client('s3')
    
    # 1. 上传测试文件
    print("📤 上传测试文件...")
    test_content = [
        {
            "id": "debug-1",
            "url": "https://example.com/debug",
            "title": "Debug Document",
            "text": "This is a debug document for S3 policy testing.",
            "word_count": 8,
            "domain_score": 4.0,
            "processed_at_stage": "domain_filter"
        }
    ]
    
    import gzip
    import io
    jsonl_content = "\n".join(json.dumps(doc, ensure_ascii=False) for doc in test_content)
    
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as gz_file:
        gz_file.write(jsonl_content.encode('utf-8'))
    
    s3_client.put_object(
        Bucket=bucket_name,
        Key=test_file_key,
        Body=buffer.getvalue(),
        ContentType='application/json',
        ContentEncoding='gzip'
    )
    print("✅ 测试文件已上传")
    
    # 2. 测试不同的Referer头格式
    test_url = f"https://s3.amazonaws.com/{bucket_name}/{test_file_key}"
    
    referer_tests = [
        ("http://54.159.47.120:23000/", "完整域名+路径"),
        ("http://54.159.47.120:23000", "域名+端口"),
        ("54.159.47.120:23000", "IP+端口"),
        ("http://54.159.47.120:23000/preview", "实际预览页面路径"),
    ]
    
    print("\n📋 测试不同Referer头格式:")
    for referer, description in referer_tests:
        headers = {
            'Referer': referer,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            status = f"✅ {response.status_code}" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {status} - {description}: {referer}")
        except Exception as e:
            print(f"   ❌ 错误 - {description}: {str(e)}")
    
    # 3. 测试policy条件
    print("\n🔍 检查Policy条件匹配:")
    print("   Policy条件: aws:Referer = http://54.159.47.120:23000/*")
    print("   测试URL模式: benchmark-*-sample.jsonl.gz")
    print(f"   测试文件名: {test_file_key}")
    print("   匹配结果: ", "✅ 匹配" if "benchmark-" in test_file_key and test_file_key.endswith(".jsonl.gz") else "❌ 不匹配")
    
    # 4. 清理
    print("\n🧹 清理测试文件...")
    s3_client.delete_object(Bucket=bucket_name, Key=test_file_key)
    print("✅ 清理完成")

if __name__ == "__main__":
    debug_s3_policy()
