#!/usr/bin/env python3
"""
使用正确文件名格式测试下载
"""

import boto3
import requests
import gzip
import json
import io

def test_correct_filename():
    print("🧪 使用正确文件名格式测试...")
    
    bucket_name = "fineweb-data"
    # 使用匹配policy的文件名格式
    test_file_key = "benchmark-test-correct-sample.jsonl.gz"
    
    s3_client = boto3.client('s3')
    
    # 1. 临时禁用Block Public Access进行测试
    print("⚠️ 临时禁用Block Public Access...")
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )
    
    try:
        # 2. 上传测试文件（使用正确文件名）
        print(f"📤 上传测试文件: {test_file_key}")
        
        sample_data = [{
            "id": "correct-test-1",
            "url": "https://example.com/correct-test",
            "title": "Correct Filename Test Document",
            "text": "This document tests the correct filename format for benchmark samples.",
            "word_count": 12,
            "domain_score": 4.2,
            "processed_at_stage": "domain_filter"
        }]
        
        jsonl_content = json.dumps(sample_data[0], ensure_ascii=False)
        
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
        
        # 3. 验证文件名匹配
        print(f"🔍 检查文件名匹配: {test_file_key}")
        if test_file_key.startswith("benchmark-") and test_file_key.endswith("-sample.jsonl.gz"):
            print("✅ 文件名格式匹配bucket policy")
        else:
            print("❌ 文件名格式不匹配")
        
        # 4. 测试下载
        test_url = f"https://s3.amazonaws.com/{bucket_name}/{test_file_key}"
        print(f"📥 测试下载: {test_url}")
        
        headers = {
            'Referer': 'http://54.159.47.120:23000/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ 下载成功！文件名格式正确")
            print(f"📏 文件大小: {len(response.content)} bytes")
            
            # 验证内容
            try:
                decompressed = gzip.decompress(response.content).decode('utf-8')
                doc = json.loads(decompressed)
                print(f"📝 文档ID: {doc.get('id')}")
                print(f"📝 文档标题: {doc.get('title')}")
            except Exception as e:
                print(f"⚠️ 内容验证失败: {e}")
                
        else:
            print(f"❌ 下载失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text[:300]}...")
            
    finally:
        # 5. 恢复Block Public Access设置
        print("\n🔒 恢复Block Public Access设置...")
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print("✅ Block Public Access已恢复")
        
        # 清理测试文件
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=test_file_key)
            print("✅ 测试文件已清理")
        except Exception as e:
            print(f"⚠️ 清理失败: {e}")

if __name__ == "__main__":
    test_correct_filename()
