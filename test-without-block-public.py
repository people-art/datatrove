#!/usr/bin/env python3
"""
在临时禁用Block Public Access的情况下测试下载
"""

import boto3
import requests
import time

def test_without_block_public():
    print("🧪 测试临时禁用Block Public Access后的下载...")
    
    bucket_name = "fineweb-data"
    test_file_key = "test-no-block-public-sample.jsonl.gz"
    
    s3_client = boto3.client('s3')
    
    # 1. 临时禁用Block Public Access
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
    print("✅ Block Public Access已临时禁用")
    
    # 等待设置生效
    time.sleep(5)
    
    try:
        # 2. 上传测试文件
        import gzip
        import json
        import io
        
        sample_data = [{
            "id": "test-public",
            "url": "https://example.com/test",
            "title": "Test Document",
            "text": "This is a test document for public access.",
            "word_count": 8,
            "domain_score": 4.0,
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
        print(f"✅ 测试文件已上传: {test_file_key}")
        
        # 3. 测试下载
        test_url = f"https://s3.amazonaws.com/{bucket_name}/{test_file_key}"
        
        headers = {
            'Referer': 'http://54.159.47.120:23000/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ 禁用Block Public Access后下载成功！")
            print(f"📏 文件大小: {len(response.content)} bytes")
            
            # 验证内容
            try:
                decompressed = gzip.decompress(response.content).decode('utf-8')
                doc = json.loads(decompressed)
                print(f"📝 文档标题: {doc.get('title')}")
            except Exception as e:
                print(f"⚠️ 内容解析失败: {e}")
                
        else:
            print(f"❌ 仍然下载失败: HTTP {response.status_code}")
            print(f"错误: {response.text[:200]}")
            
    finally:
        # 4. 恢复Block Public Access设置
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
        except:
            pass

if __name__ == "__main__":
    test_without_block_public()
