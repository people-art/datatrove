#!/usr/bin/env python3
"""
模拟前端实际的下载请求
"""

import requests

def test_frontend_request():
    print("🌐 模拟前端下载请求...")
    
    # 实际的benchmark文件URL（如果存在的话）
    actual_url = "https://s3.amazonaws.com/fineweb-data/benchmark-22221dd1-b459-49cd-8542-60736879e93e-sample.jsonl.gz"
    
    # 模拟浏览器发出的请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 's3.amazonaws.com',
        'Origin': 'http://54.159.47.120:23000',
        'Pragma': 'no-cache',
        'Referer': 'http://54.159.47.120:23000/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"📡 请求URL: {actual_url}")
    print(f"📋 Referer: {headers['Referer']}")
    print(f"🌐 Origin: {headers['Origin']}")
    
    try:
        # 先发送OPTIONS预检请求（CORS）
        print("\n🔍 发送CORS预检请求...")
        options_headers = {
            'Origin': headers['Origin'],
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'cache-control,pragma',
            'Host': 's3.amazonaws.com',
            'User-Agent': headers['User-Agent']
        }
        
        options_response = requests.options(actual_url, headers=options_headers, timeout=10)
        print(f"OPTIONS响应: {options_response.status_code}")
        
        if 'access-control-allow-origin' in options_response.headers:
            print(f"✅ CORS预检通过: {options_response.headers['access-control-allow-origin']}")
        else:
            print("❌ CORS预检失败 - 没有Access-Control-Allow-Origin头")
        
        # 发送实际的GET请求
        print("\n📥 发送实际下载请求...")
        response = requests.get(actual_url, headers=headers, timeout=10)
        
        print(f"GET响应状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 下载成功！")
            print(f"📏 文件大小: {len(response.content)} bytes")
            
            # 检查响应头
            cors_headers = ['access-control-allow-origin', 'access-control-allow-methods', 'access-control-allow-headers']
            print("\n🔍 CORS响应头:")
            for header in cors_headers:
                if header in response.headers:
                    print(f"   ✅ {header}: {response.headers[header]}")
                else:
                    print(f"   ❌ 缺少 {header}")
                    
        else:
            print(f"❌ 下载失败: {response.status_code}")
            print(f"错误内容: {response.text[:300]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        
        # 检查网络连接
        try:
            test_response = requests.get("https://s3.amazonaws.com", timeout=5)
            print("🌐 网络连接正常")
        except:
            print("❌ 网络连接异常")

if __name__ == "__main__":
    test_frontend_request()
