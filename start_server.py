#!/usr/bin/env python3
"""
Server startup script - Run from project root
Simple wrapper that just calls the backend server
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    print("🚀 Starting AI Model Benchmarking Tool")
    print("📍 Server will be available at: http://localhost:8000")
    print("📋 API docs at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/api/health")
    print("⏹️  Press CTRL+C to stop\n")
    
    # Change to backend directory and run the app
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        subprocess.run([
            sys.executable, "app.py"
        ], cwd=backend_dir, check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed with exit code {e.returncode}")
        sys.exit(e.returncode)
