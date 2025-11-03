#!/usr/bin/env python3
"""
Quick test for OpenAI integration
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openai_setup():
    print("🔍 Testing OpenAI Setup...")

    # Check if .env exists
    env_paths = ['../.env', './.env', '.env']
    env_found = False
    for path in env_paths:
        if os.path.exists(path):
            print(f"📄 Found .env file at: {path}")
            env_found = True
            break

    if not env_found:
        print("❌ No .env file found. Please create one with OPENAI_API_KEY")
        return False

    # Try to load dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv loaded successfully")
    except ImportError:
        print("❌ python-dotenv not available")
        return False

    # Check OpenAI package
    try:
        from openai import OpenAI
        print("✅ OpenAI package available")

        # Check API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and len(api_key.strip()) > 10:
            print(f"✅ OPENAI_API_KEY is set (length: {len(api_key)})")

            # Test API connection
            try:
                client = OpenAI(api_key=api_key)
                # Simple test call
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello, test message"}],
                    max_tokens=10
                )
                print("✅ OpenAI API connection successful")
                return True
            except Exception as e:
                print(f"❌ OpenAI API test failed: {e}")
                return False
        else:
            print("❌ OPENAI_API_KEY not set or too short")
            return False

    except ImportError:
        print("❌ OpenAI package not available")
        print("   Installing...")

        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', 'openai'])
            print("✅ OpenAI package installed")

            # Try again
            from openai import OpenAI
            print("✅ OpenAI package available after installation")
            return True
        except Exception as e:
            print(f"❌ Failed to install OpenAI: {e}")
            return False

if __name__ == '__main__':
    success = test_openai_setup()
    if success:
        print("\n🎉 OpenAI setup is working correctly!")
    else:
        print("\n❌ OpenAI setup needs fixing. Please check the instructions above.")
