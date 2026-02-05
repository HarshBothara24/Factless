#!/usr/bin/env python3
"""
Setup script for Gemini API integration.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with Gemini API key."""
    print("🔧 FACTLESS Gemini API Setup")
    print("=" * 40)
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        with open(env_file) as f:
            content = f.read()
            if "GEMINI_API_KEY" in content:
                print("✓ GEMINI_API_KEY already configured in .env")
                return True
    
    print("\nTo use FACTLESS with Gemini API for claim extraction:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Enter it below")
    print("\nNote: If you don't have an API key, the system will use fallback responses")
    
    api_key = input("\nEnter your Gemini API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⚠ No API key provided. System will use fallback responses.")
        api_key = ""
    
    # Create or update .env file
    env_content = []
    
    if env_file.exists():
        with open(env_file) as f:
            env_content = f.readlines()
    
    # Remove existing GEMINI_API_KEY line
    env_content = [line for line in env_content if not line.startswith("GEMINI_API_KEY=")]
    
    # Add new GEMINI_API_KEY line
    env_content.append(f"GEMINI_API_KEY={api_key}\n")
    
    # Add other default settings if not present
    defaults = [
        "FACTLESS_LOG_LEVEL=INFO",
        "PYTHONPATH=/app",
        "MAX_TEXT_LENGTH=10000",
        "ENABLE_DETAILED_LOGGING=true"
    ]
    
    existing_keys = set()
    for line in env_content:
        if '=' in line:
            key = line.split('=')[0]
            existing_keys.add(key)
    
    for default in defaults:
        key = default.split('=')[0]
        if key not in existing_keys:
            env_content.append(f"{default}\n")
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.writelines(env_content)
    
    print(f"✓ Configuration saved to {env_file}")
    
    if api_key:
        print("✓ Gemini API key configured")
    else:
        print("ℹ No API key configured - using fallback responses")
    
    return True

def test_gemini_connection():
    """Test Gemini API connection."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠ No API key found - skipping connection test")
            return False
        
        print("\n🧪 Testing Gemini API connection...")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Simple test
        response = model.generate_content("Hello")
        
        if response.text:
            print("✓ Gemini API connection successful")
            return True
        else:
            print("✗ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"✗ Gemini API connection failed: {str(e)}")
        return False

def main():
    """Main setup function."""
    # Load existing .env if present
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # Create/update .env file
    create_env_file()
    
    # Reload environment
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # Test connection
    test_gemini_connection()
    
    print("\n🚀 Setup complete!")
    print("Run 'python run_dev.py' to start the development server")

if __name__ == "__main__":
    main()