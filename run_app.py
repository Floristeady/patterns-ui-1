#!/usr/bin/env python3
"""
Alternative startup script with proper imports
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    from backend.app import app
    
    print("🚀 AI Model Benchmarking Tool")
    print("🌐 Starting server at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/api/health")
    print("\n⏹️  Press CTRL+C to stop server")
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
