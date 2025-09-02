"""
FastAPI Main Application - AI Model Benchmarking Tool
Main entry point with REST API endpoints and WebSocket support
"""

import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from config import get_enabled_models, get_all_models, MODELS
from services.benchmark_service import BenchmarkService
from services.storage_service import StorageService


# Pydantic models for request/response
class BenchmarkRequest(BaseModel):
    prompt: str
    selected_models: List[str]
    content_level: str = "none"  # Default to no content

class BenchmarkResponse(BaseModel):
    session_id: str
    status: str
    message: str

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    category: str
    enabled: bool
    cost_per_million_tokens: Dict[str, float]
    max_tokens: int
    context_window: int

# Initialize FastAPI app
app = FastAPI(
    title="AI Model Benchmarking Tool",
    description="Compare HTML/CSS generation speed across AI models",
    version="1.0.0"
)

# Initialize services
benchmark_service = BenchmarkService()
storage_service = StorageService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_update(self, session_id: str, model_id: str, status: str, result: Dict = None):
        if session_id in self.active_connections:
            try:
                update_data = {
                    "session_id": session_id,
                    "model_id": model_id,
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                }
                await self.active_connections[session_id].send_text(json.dumps(update_data))
            except Exception as e:
                print(f"Error sending WebSocket update: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()


# API Endpoints

@app.get("/")
async def root():
    """Serve the main frontend page"""
    return FileResponse("../frontend/index.html")

@app.get("/api/models", response_model=Dict[str, List[ModelInfo]])
async def get_models():
    """Get all available models grouped by category"""
    models_by_category = {}
    
    for category, models in MODELS.items():
        models_by_category[category] = [
            ModelInfo(
                id=model["id"],
                name=model["name"],
                provider=model["provider"],
                category=category,
                enabled=model["enabled"],
                cost_per_million_tokens=model["cost_per_million_tokens"],
                max_tokens=model.get("max_tokens", 4096),
                context_window=model.get("context_window", 128000)
            )
            for model in models
        ]
    
    return models_by_category

@app.get("/api/models/enabled")
async def get_enabled_models_endpoint():
    """Get only enabled models"""
    enabled = get_enabled_models()
    return {"models": list(enabled.keys()), "count": len(enabled)}

@app.get("/api/content/{level}")
async def get_content(level: str):
    """Get content data by level"""
    try:
        content_files = {
            "basic": "../content/data/basic/tokyo-neighborhoods.md",
            "medium": "../content/data/intermediate/tokyo-detailed-guide.md", 
            "complex": "../content/data/complex/tokyo-comprehensive-analysis.md"
        }
        
        if level not in content_files:
            raise HTTPException(status_code=404, detail="Content level not found")
        
        file_path = Path(content_files[level])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Content file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "level": level,
            "content": content,
            "length": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load content: {str(e)}")

@app.post("/api/benchmark", response_model=BenchmarkResponse)
async def start_benchmark(request: BenchmarkRequest):
    """Start a new benchmark session"""
    try:
        # Validate input
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if not request.selected_models:
            raise HTTPException(status_code=400, detail="At least one model must be selected")
        
        # Validate selected models
        enabled_models = get_enabled_models()
        invalid_models = [m for m in request.selected_models if m not in enabled_models]
        if invalid_models:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid or disabled models: {', '.join(invalid_models)}"
            )
        
        # Prepare prompt with content if specified
        final_prompt = request.prompt
        if request.content_level and request.content_level != "none":
            try:
                content_files = {
                    "basic": "../content/data/basic/tokyo-neighborhoods.md",
                    "medium": "../content/data/intermediate/tokyo-detailed-guide.md", 
                    "complex": "../content/data/complex/tokyo-comprehensive-analysis.md"
                }
                
                if request.content_level in content_files:
                    file_path = Path(content_files[request.content_level])
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content_data = f.read()
                        
                        final_prompt = f"{request.prompt}\n\nUse this data for your response:\n\n{content_data}"
            except Exception as e:
                print(f"Warning: Could not load content {request.content_level}: {e}")
                # Continue with original prompt if content loading fails
        
        # Create progress callback for WebSocket updates
        async def progress_callback(session_id: str, model_id: str, status: str, result: Dict = None):
            await manager.send_update(session_id, model_id, status, result)
        
        # Start benchmark and get session info immediately
        session_task = asyncio.create_task(
            benchmark_service.run_benchmark(
                final_prompt, 
                request.selected_models, 
                progress_callback
            )
        )
        
        # Give the task a moment to initialize and get session_id
        await asyncio.sleep(0.05)
        
        # Try to get session_id from active sessions
        active_sessions = benchmark_service.get_all_sessions()
        session_id = list(active_sessions.keys())[-1] if active_sessions else "benchmark_session"
        
        return BenchmarkResponse(
            session_id=session_id,
            status="started",
            message=f"Benchmark started with {len(request.selected_models)} models"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start benchmark: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session_results(session_id: str):
    """Get results for a specific session"""
    session_data = benchmark_service.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data

@app.get("/api/sessions")
async def list_sessions(limit: int = 20):
    """List recent benchmark sessions"""
    try:
        sessions = await storage_service.list_sessions(limit)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.get("/api/sessions/{session_id}/html/{model_id}")
async def get_generated_html(session_id: str, model_id: str):
    """Get generated HTML for a specific model in a session"""
    try:
        session_data = benchmark_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if model_id not in session_data["results"]:
            raise HTTPException(status_code=404, detail="Model result not found")
        
        result = session_data["results"][model_id]
        if result["status"] != "success" or not result.get("html_content"):
            raise HTTPException(status_code=404, detail="HTML content not available")
        
        return HTMLResponse(content=result["html_content"])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get HTML: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test API connections
        api_status = await benchmark_service.test_api_connections()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "api_connections": api_status,
            "available_models": len(get_enabled_models())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# WebSocket endpoint for real-time updates
@app.websocket("/ws/benchmark/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket connection for real-time benchmark updates"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            
            # Handle client messages (like ping/pong)
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Serve HTML files from outputs directory
@app.get("/outputs/{path:path}")
async def serve_output_files(path: str):
    """Serve files from the outputs directory"""
    file_path = Path("../outputs") / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AI Model Benchmarking Tool")
    print("📊 Available models:")
    
    enabled = get_enabled_models()
    for category, models in MODELS.items():
        enabled_in_category = [m for m in models if m["enabled"]]
        if enabled_in_category:
            print(f"  {category.title()}: {len(enabled_in_category)} models")
    
    print(f"\n🌐 Server starting at: http://localhost:8000")
    print("📋 API docs available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/api/health")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
