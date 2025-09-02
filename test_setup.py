#!/usr/bin/env python3
"""
Quick setup test for AI Model Benchmarking Tool
Verifies configuration and basic functionality
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    from backend.config import get_enabled_models, OPENAI_API_KEY, ANTHROPIC_API_KEY
    from backend.services.benchmark_service import BenchmarkService
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


async def test_setup():
    """Test basic setup and configuration"""
    
    print("🧪 AI Model Benchmarking Tool - Setup Test")
    print("=" * 50)
    
    # Test 1: Environment variables
    print("\n1. Testing environment configuration...")
    
    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY not found in environment")
        print("   Create a .env file with your OpenAI API key")
    else:
        print(f"✅ OpenAI API key configured (length: {len(OPENAI_API_KEY)})")
    
    if not ANTHROPIC_API_KEY:
        print("⚠️  ANTHROPIC_API_KEY not found in environment")
        print("   Create a .env file with your Anthropic API key")
    else:
        print(f"✅ Anthropic API key configured (length: {len(ANTHROPIC_API_KEY)})")
    
    # Test 2: Model configuration
    print("\n2. Testing model configuration...")
    
    enabled_models = get_enabled_models()
    print(f"✅ {len(enabled_models)} models enabled")
    
    for model_id, model_config in enabled_models.items():
        provider = model_config.get('provider', 'unknown')
        category = model_config.get('category', 'unknown')
        print(f"   📋 {model_config['name']} ({provider}, {category})")
    
    # Test 3: API connectivity
    print("\n3. Testing API connectivity...")
    
    if OPENAI_API_KEY and ANTHROPIC_API_KEY:
        try:
            benchmark_service = BenchmarkService()
            api_status = await benchmark_service.test_api_connections()
            
            if api_status.get('openai'):
                print("✅ OpenAI API connection successful")
            else:
                print("❌ OpenAI API connection failed")
            
            if api_status.get('anthropic'):
                print("✅ Anthropic API connection successful")
            else:
                print("❌ Anthropic API connection failed")
                
        except Exception as e:
            print(f"❌ API test error: {e}")
    else:
        print("⚠️  Skipping API tests (missing keys)")
    
    # Test 4: Directory structure
    print("\n4. Testing directory structure...")
    
    required_dirs = [
        "backend",
        "frontend", 
        "outputs",
        "docs"
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
    
    # Test 5: Required files
    print("\n5. Testing required files...")
    
    required_files = [
        "backend/app.py",
        "backend/config.py",
        "frontend/index.html",
        "frontend/style.css",
        "frontend/script.js",
        "requirements.txt",
        "README.md"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    print("\n🎯 Setup test complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Create .env file with your API keys")
    print("3. Run the server: cd backend && python app.py")
    print("4. Open http://localhost:8000 in your browser")


if __name__ == "__main__":
    asyncio.run(test_setup())
