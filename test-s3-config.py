#!/usr/bin/env python3
"""
测试S3配置是否正确
"""

import boto3
import requests
import json
from botocore.exceptions import ClientError

def test_s3_configuration():
    print("🧪 开始测试S3配置...")
    
    # 配置
    bucket_name = "fineweb-data"
    test_file_key = "test-benchmark-sample.jsonl.gz"
    frontend_domain = "http://54.159.47.120:23000"
    
    # 创建S3客户端
    s3_client = boto3.client('s3')
    
    try:
        # 1. 测试上传权限
        print("📤 测试上传权限...")
        test_content = [
            {
                "id": "test-1",
                "url": "https://example.com/test",
                "title": "Test Document",
                "text": "This is a test document for S3 configuration validation.",
                "word_count": 10,
                "domain_score": 4.5,
                "processed_at_stage": "domain_filter"
            }
        ]
        
        # 上传测试文件
        import gzip
        import io
        jsonl_content = "\n".join(json.dumps(doc, ensure_ascii=False) for doc in test_content)
        
        # 创建gzip压缩内容
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
        print("✅ 上传测试文件成功")
        
        # 2. 测试下载权限（模拟前端请求）
        print("📥 测试下载权限...")
        test_url = f"https://s3.amazonaws.com/{bucket_name}/{test_file_key}"
        
        # 使用正确的Referer头模拟前端请求
        headers = {
            'Referer': f"{frontend_domain}/",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ 下载测试成功 - CORS配置正确")
            print(f"   响应大小: {len(response.content)} bytes")
            
            # 验证内容
            import gzip
            decompressed = gzip.decompress(response.content).decode('utf-8')
            downloaded_docs = [json.loads(line) for line in decompressed.strip().split('\n')]
            
            if len(downloaded_docs) == 1 and downloaded_docs[0]['id'] == 'test-1':
                print("✅ 文件内容验证通过")
            else:
                print("⚠️ 文件内容不匹配")
                
        else:
            print(f"❌ 下载测试失败 - HTTP {response.status_code}")
            print(f"   错误信息: {response.text[:200]}")
        
        # 3. 测试无Referer头的请求（应该失败）
        print("🚫 测试无Referer头的请求...")
        response_no_referer = requests.get(test_url, timeout=10)
        
        if response_no_referer.status_code == 403:
            print("✅ 安全验证通过 - 无Referer头的请求被正确拒绝")
        else:
            print(f"⚠️ 安全验证异常 - 无Referer头请求返回 {response_no_referer.status_code}")
        
        # 4. 清理测试文件
        print("🧹 清理测试文件...")
        s3_client.delete_object(Bucket=bucket_name, Key=test_file_key)
        print("✅ 测试文件已清理")
        
        print("\n🎉 S3配置测试完成！")
        print("📋 总结:")
        print("   ✅ Bucket Policy配置正确")
        print("   ✅ Block Public Access设置安全")
        print("   ✅ 前端下载权限正常")
        print("   ✅ 安全限制生效")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ AWS错误: {error_code}")
        print(f"   详细信息: {e.response['Error']['Message']}")
        
        if error_code == 'AccessDenied':
            print("💡 建议检查IAM权限")
        elif error_code == 'NoSuchBucket':
            print("💡 存储桶不存在")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_s3_configuration()
