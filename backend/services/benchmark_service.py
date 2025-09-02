"""
Benchmark Service - Core business logic for AI model benchmarking
Handles parallel execution, result aggregation, and performance monitoring
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from config import get_model_by_id, get_enabled_models
from models.openai_client import OpenAIClient
from models.anthropic_client import AnthropicClient
from services.storage_service import StorageService


class BenchmarkService:
    """Service for running AI model benchmarks"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.anthropic_client = AnthropicClient()
        self.storage_service = StorageService()
        self.active_sessions: Dict[str, Dict] = {}
    
    async def run_benchmark(
        self, 
        prompt: str, 
        selected_models: List[str],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run benchmark across selected models in parallel
        
        Args:
            prompt: User description of UI pattern to generate
            selected_models: List of model IDs to test
            progress_callback: Optional callback for real-time updates
            
        Returns:
            Dictionary with session_id and initial results
        """
        session_id = str(uuid.uuid4())
        session_start = datetime.now()
        
        # Validate selected models
        valid_models = []
        enabled_models = get_enabled_models()
        
        for model_id in selected_models:
            if model_id in enabled_models:
                valid_models.append(model_id)
            else:
                print(f"Warning: Model {model_id} is not available or enabled")
        
        if not valid_models:
            raise ValueError("No valid models selected")
        
        # Initialize session
        session_data = {
            "session_id": session_id,
            "prompt": prompt,
            "selected_models": valid_models,
            "start_time": session_start.isoformat(),
            "status": "running",
            "results": {},
            "summary": {
                "total_models": len(valid_models),
                "completed": 0,
                "failed": 0,
                "total_cost": 0.0,
                "fastest_model": None,
                "slowest_model": None
            }
        }
        
        self.active_sessions[session_id] = session_data
        
        # Create tasks for parallel execution
        tasks = []
        for model_id in valid_models:
            model_config = get_model_by_id(model_id)
            task = asyncio.create_task(
                self._benchmark_single_model(
                    prompt, model_config, session_id, progress_callback
                )
            )
            tasks.append(task)
        
        # Execute all models in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            session_end = datetime.now()
            session_duration = (session_end - session_start).total_seconds()
            
            # Update session data
            session_data["end_time"] = session_end.isoformat()
            session_data["duration_seconds"] = round(session_duration, 3)
            session_data["status"] = "completed"
            
            # Calculate summary statistics
            self._calculate_summary_stats(session_data)
            
            # Save results to storage
            await self.storage_service.save_session_results(session_data)
            
            return session_data
            
        except Exception as e:
            session_data["status"] = "error"
            session_data["error_message"] = str(e)
            return session_data
    
    async def _benchmark_single_model(
        self, 
        prompt: str, 
        model_config: Dict[str, Any], 
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Benchmark a single model and update session results
        
        Args:
            prompt: User prompt
            model_config: Model configuration
            session_id: Session identifier
            progress_callback: Progress update callback
            
        Returns:
            Benchmark result for the model
        """
        model_id = model_config["id"]
        
        try:
            # Send progress update - starting
            if progress_callback:
                await progress_callback(session_id, model_id, "running", None)
            
            # Choose appropriate client based on provider
            if model_config["provider"] == "openai":
                # Use retry logic for OpenAI models (especially GPT-5)
                result = await self.openai_client.generate_html_with_retry(prompt, model_config)
            elif model_config["provider"] == "anthropic":
                result = await self.anthropic_client.generate_html(prompt, model_config)
            else:
                raise ValueError(f"Unknown provider: {model_config['provider']}")
            
            # Update session results
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["results"][model_id] = result
                
                # Update summary counters
                summary = self.active_sessions[session_id]["summary"]
                if result["status"] == "success":
                    summary["completed"] += 1
                    summary["total_cost"] += result.get("cost_usd", 0)
                else:
                    summary["failed"] += 1
            
            # Send progress update - completed
            if progress_callback:
                await progress_callback(session_id, model_id, result["status"], result)
            
            return result
            
        except Exception as e:
            error_result = {
                "model_id": model_id,
                "model_name": model_config["name"],
                "provider": model_config["provider"],
                "status": "error",
                "error_message": str(e),
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": 0,
                "cost_usd": 0
            }
            
            # Update session results
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["results"][model_id] = error_result
                self.active_sessions[session_id]["summary"]["failed"] += 1
            
            # Send progress update - error
            if progress_callback:
                await progress_callback(session_id, model_id, "error", error_result)
            
            return error_result
    
    def _calculate_summary_stats(self, session_data: Dict[str, Any]):
        """Calculate summary statistics for the benchmark session"""
        results = session_data["results"]
        summary = session_data["summary"]
        
        if not results:
            return
        
        # Find fastest and slowest successful models
        successful_results = [
            (model_id, result) for model_id, result in results.items()
            if result["status"] == "success" and result.get("duration_seconds")
        ]
        
        if successful_results:
            # Sort by duration
            successful_results.sort(key=lambda x: x[1]["duration_seconds"])
            
            fastest = successful_results[0]
            slowest = successful_results[-1]
            
            summary["fastest_model"] = {
                "model_id": fastest[0],
                "model_name": fastest[1]["model_name"],
                "duration_seconds": fastest[1]["duration_seconds"],
                "cost_usd": fastest[1].get("cost_usd", 0)
            }
            
            summary["slowest_model"] = {
                "model_id": slowest[0],
                "model_name": slowest[1]["model_name"],
                "duration_seconds": slowest[1]["duration_seconds"],
                "cost_usd": slowest[1].get("cost_usd", 0)
            }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions"""
        return self.active_sessions.copy()
    
    async def test_api_connections(self) -> Dict[str, bool]:
        """Test connectivity to all AI APIs"""
        results = {}
        
        try:
            results["openai"] = await self.openai_client.test_connection()
        except Exception:
            results["openai"] = False
        
        try:
            results["anthropic"] = await self.anthropic_client.test_connection()
        except Exception:
            results["anthropic"] = False
        
        return results
