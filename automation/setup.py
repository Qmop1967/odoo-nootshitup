#!/usr/bin/env python3
"""
TSH Salesperson App - Automation Setup Script
This script helps set up the automated CI/CD error handling system.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_requirements():
    """Check if all required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        "python3": "python3 --version",
        "git": "git --version",
        "pip": "pip --version"
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            subprocess.run(command.split(), capture_output=True, check=True)
            print(f"  ✅ {tool}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {tool}")
            missing.append(tool)
    
    if missing:
        print(f"\n❌ Missing requirements: {', '.join(missing)}")
        return False
    
    print("✅ All requirements satisfied")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment configuration"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_template = """# TSH Salesperson App - Automation Configuration
# Copy this file to .env and fill in your actual values

# CodeMagic API Configuration
CODEMAGIC_API_TOKEN=your_codemagic_api_token_here
CODEMAGIC_APP_ID=your_codemagic_app_id_here

# GitHub Configuration  
GITHUB_TOKEN=your_github_token_here

# Webhook Configuration (optional)
WEBHOOK_SECRET=your_webhook_secret_here
PORT=5000
DEBUG=false

# Notification Configuration (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_TO=kha89ahm@gmail.com
"""
    
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_template)
        print(f"✅ Created {env_file}")
        print("📝 Please edit .env file with your actual credentials")
    else:
        print(f"⚠️ {env_file} already exists")
    
    return True

def setup_github_secrets():
    """Guide user through GitHub secrets setup"""
    print("\n🔐 GitHub Secrets Setup Guide")
    print("You need to add these secrets to your GitHub repository:")
    print("Go to: Settings > Secrets and variables > Actions")
    print()
    
    secrets = [
        ("CODEMAGIC_API_TOKEN", "Your CodeMagic API token"),
        ("CODEMAGIC_APP_ID", "Your CodeMagic app ID"),
        ("GITHUB_TOKEN", "GitHub token with repo access (usually auto-provided)")
    ]
    
    for secret, description in secrets:
        print(f"  🔑 {secret}")
        print(f"     {description}")
        print()
    
    return True

def setup_codemagic_webhook():
    """Guide user through CodeMagic webhook setup"""
    print("\n🪝 CodeMagic Webhook Setup Guide")
    print("To enable automatic error handling:")
    print()
    print("1. Go to your CodeMagic app settings")
    print("2. Navigate to 'Webhooks' section")
    print("3. Add a new webhook with:")
    print("   - URL: https://your-server.com/webhook/codemagic")
    print("   - Events: Build finished")
    print("   - Secret: (optional, set in .env file)")
    print()
    print("Alternative: Use GitHub Actions scheduled runs (already configured)")
    print()
    
    return True

def test_configuration():
    """Test the configuration"""
    print("\n🧪 Testing configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ["CODEMAGIC_API_TOKEN", "CODEMAGIC_APP_ID"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing or placeholder values: {', '.join(missing_vars)}")
            print("Please update your .env file with actual values")
            return False
        
        print("✅ Configuration looks good")
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

def main():
    """Main setup process"""
    print("🚀 TSH Salesperson App - Automation Setup")
    print("=" * 50)
    
    steps = [
        ("Check Requirements", check_requirements),
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("GitHub Secrets Guide", setup_github_secrets),
        ("CodeMagic Webhook Guide", setup_codemagic_webhook),
        ("Test Configuration", test_configuration)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Update .env file with your actual credentials")
    print("2. Add GitHub secrets to your repository")
    print("3. Configure CodeMagic webhook (optional)")
    print("4. Test the automation:")
    print("   python error_handler.py")
    print("\n🔗 Useful Links:")
    print("- CodeMagic API: https://docs.codemagic.io/rest-api/overview/")
    print("- GitHub Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets")
    print("- Project Repository: https://github.com/Qmop1967/TSH-Salesperson-App")

if __name__ == "__main__":
    main()