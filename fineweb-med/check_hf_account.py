#!/usr/bin/env python3
"""
Check HuggingFace Account Information

This script helps you verify your HuggingFace account details and token permissions.
"""

import argparse
import sys

try:
    from huggingface_hub import HfApi, login
except ImportError:
    print("❌ Missing huggingface_hub. Install with: pip install huggingface_hub")
    sys.exit(1)


def check_account(token=None):
    """Check HuggingFace account information."""
    if not token:
        print("❌ No token provided. Use --token to specify your HuggingFace token.")
        print("   Get your token from: https://huggingface.co/settings/tokens")
        return

    try:
        # Login and check authentication
        print("🔐 Authenticating with HuggingFace...")
        login(token=token)

        # Get user information
        api = HfApi()
        user_info = api.whoami(token=token)

        print("✅ Authentication successful!")
        print(f"👤 Username: {user_info['name']}")
        print(f"📧 Email: {user_info.get('email', 'Not provided')}")
        print(f"🔗 Profile: https://huggingface.co/{user_info['name']}")
        print(f"🏢 Organization: {user_info.get('type', 'User account')}")

        # Test repository creation permissions
        test_repo = f"{user_info['name']}/test-fineweb-med-upload"

        print(f"\n🔧 Testing repository creation permissions...")
        print(f"   Target repo: {test_repo}")

        try:
            from huggingface_hub import create_repo
            # Try to create a test repo (will be cleaned up)
            create_repo(test_repo, token=token, private=True, repo_type="dataset")

            # Clean up the test repo
            api.delete_repo(test_repo, token=token, repo_type="dataset")

            print("✅ Repository creation: PERMITTED")
            print("   You can create datasets under your namespace!")

        except Exception as e:
            error_str = str(e).lower()
            if "403" in error_str or "forbidden" in error_str:
                print("❌ Repository creation: FORBIDDEN")
                print("   You don't have permission to create datasets.")
                print("   Check your token permissions at: https://huggingface.co/settings/tokens")
            else:
                print(f"⚠️  Repository creation: UNKNOWN ERROR - {e}")

        # Show usage instructions
        print("
📝 For FineWeb-Med upload, use:"        print(f"   Username: {user_info['name']}")
        print(f"   Repository: {user_info['name']}/fineweb-med")
        print("   Token: [your token]"

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔍 Troubleshooting:")
        print("1. Check your token at: https://huggingface.co/settings/tokens")
        print("2. Make sure the token has 'Write' permissions")
        print("3. Verify the token is not expired")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description='Check HuggingFace account information')
    parser.add_argument('--token', help='HuggingFace API token to check')

    args = parser.parse_args()

    if not args.token:
        print("🔑 HuggingFace Account Checker")
        print("=" * 40)
        print()
        token = input("Enter your HuggingFace token: ").strip()
        if not token:
            print("❌ No token provided.")
            return
    else:
        token = args.token

    check_account(token)


if __name__ == "__main__":
    main()
