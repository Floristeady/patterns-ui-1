"""
Agent Benchmark Service - Separate content generation from UI layout generation
Implements Responder (content) + Materializer (layout) architecture
"""

import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from config import get_model_by_id, get_enabled_models
from models.openai_client import OpenAIClient
from models.anthropic_client import AnthropicClient
from services.storage_service import StorageService


class AgentBenchmarkService:
    """Service for running separated agent benchmarks"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.anthropic_client = AnthropicClient()
        self.storage_service = StorageService()
        self.active_sessions: Dict[str, Dict] = {}
    
    def generate_responder_prompt(self, user_input: str) -> str:
        """Generate prompt for content generation agent"""
        return f"""
Generate structured JSON data based on this request: {user_input}

Analyze the request and create appropriate data structure. Examples:
- If cards/grid requested: array of items with title, description, etc.
- If timeline requested: array of events with dates, descriptions
- If dashboard requested: metrics, charts data, KPIs
- If table requested: rows and columns with relevant data

Requirements:
- Return ONLY valid JSON
- Use realistic, relevant data (no Lorem Ipsum)
- Structure data logically for the requested layout
- Include 6-12 items/entries typically
- No explanations, just JSON

JSON Response:"""

    def generate_materializer_prompt(self, user_input: str) -> str:
        """Generate prompt for UI layout generation agent"""
        return f"""
Create ONLY HTML/CSS template based on this request: {user_input}

Requirements:
- Generate complete HTML document with inline CSS
- Create template structure for the requested layout type
- Use placeholder variables in {{{{variable}}}} format for dynamic content
- Responsive design with modern CSS
- NO actual data - only structure and styling
- Include proper semantic HTML elements
- Ensure accessibility with ARIA labels

Focus on creating the UI/layout structure, not the content.
RESPOND with HTML template only, no explanations."""

    async def run_agent_benchmark(
        self, 
        user_input: str,
        mode: str,
        selected_models: List[str],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run benchmark with agent separation
        
        Args:
            user_input: User's description of what to create
            mode: 'responder', 'materializer', or 'chain'
            selected_models: List of model IDs to test
            progress_callback: Optional callback for real-time updates
        """
        session_id = str(uuid.uuid4())
        session_start = datetime.now()
        
        # Validate models
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
            "user_input": user_input,
            "mode": mode,
            "selected_models": valid_models,
            "start_time": session_start.isoformat(),
            "status": "running",
            "results": {},
            "summary": {
                "total_models": len(valid_models),
                "completed": 0,
                "failed": 0,
                "total_cost": 0.0
            }
        }
        
        self.active_sessions[session_id] = session_data
        
        try:
            if mode == "responder":
                results = await self._benchmark_responder_only(user_input, valid_models, session_id, progress_callback)
            elif mode == "materializer":
                results = await self._benchmark_materializer_only(user_input, valid_models, session_id, progress_callback)
            elif mode == "chain":
                results = await self._benchmark_chain(user_input, valid_models, session_id, progress_callback)
            else:
                raise ValueError(f"Unknown benchmark mode: {mode}")
            
            # Update session
            session_end = datetime.now()
            session_duration = (session_end - session_start).total_seconds()
            
            session_data["end_time"] = session_end.isoformat()
            session_data["duration_seconds"] = round(session_duration, 3)
            session_data["status"] = "completed"
            session_data["results"] = results
            
            # Calculate summary
            self._calculate_summary_stats(session_data)
            
            # Save results
            await self.storage_service.save_session_results(session_data)
            
            return session_data
            
        except Exception as e:
            import traceback
            error_details = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(f"Agent benchmark error: {error_details}")
            session_data["status"] = "error"
            session_data["error_message"] = str(e)
            
            # Try to save results even with errors, if we have valid data
            try:
                if session_data.get("results") and any(isinstance(v, dict) for v in session_data["results"].values()):
                    print("Attempting to save results despite error...")
                    await self.storage_service.save_session_results(session_data)
            except Exception as save_error:
                print(f"Failed to save results: {save_error}")
            
            return session_data
    
    async def _benchmark_responder_only(
        self, 
        user_input: str, 
        models: List[str], 
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Benchmark only content generation (Responder agent)"""
        prompt = self.generate_responder_prompt(user_input)
        
        tasks = []
        for model_id in models:
            model_config = get_model_by_id(model_id)
            task = asyncio.create_task(
                self._benchmark_single_agent(
                    prompt, model_config, "responder", session_id, progress_callback
                )
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert list to dict keyed by model_id
        results_dict = {}
        for i, result in enumerate(results):
            if isinstance(result, dict):
                results_dict[models[i]] = result
            else:
                # Handle exception
                results_dict[models[i]] = {
                    "model_id": models[i],
                    "status": "error",
                    "error_message": str(result),
                    "duration_seconds": 0,
                    "cost_usd": 0
                }
        
        return results_dict
    
    async def _benchmark_materializer_only(
        self, 
        user_input: str, 
        models: List[str], 
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Benchmark only UI layout generation (Materializer agent)"""
        prompt = self.generate_materializer_prompt(user_input)
        
        tasks = []
        for model_id in models:
            model_config = get_model_by_id(model_id)
            task = asyncio.create_task(
                self._benchmark_single_agent(
                    prompt, model_config, "materializer", session_id, progress_callback
                )
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert list to dict keyed by model_id
        results_dict = {}
        for i, result in enumerate(results):
            if isinstance(result, dict):
                results_dict[models[i]] = result
            else:
                results_dict[models[i]] = {
                    "model_id": models[i],
                    "status": "error", 
                    "error_message": str(result),
                    "duration_seconds": 0,
                    "cost_usd": 0
                }
        
        return results_dict
    
    async def _benchmark_chain(
        self, 
        user_input: str, 
        models: List[str], 
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Benchmark both agents in sequence - INDIVIDUAL MODEL PROCESSING"""
        if progress_callback:
            await progress_callback(session_id, "system", "chain_start", {"phase": "Starting Chain Mode - Individual Model Processing"})
        
        # Create tasks for each model to run BOTH phases individually
        tasks = []
        for model_id in models:
            task = asyncio.create_task(
                self._benchmark_single_model_chain(
                    user_input, model_id, session_id, progress_callback
                )
            )
            tasks.append(task)
        
        # Execute all model chains in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results into expected structure
        responder_results = {}
        materializer_results = {}
        
        for i, result in enumerate(results):
            model_id = models[i]
            if isinstance(result, dict) and "responder_result" in result and "materializer_result" in result:
                responder_results[model_id] = result["responder_result"]
                materializer_results[model_id] = result["materializer_result"]
            else:
                # Handle errors
                error_result = {
                    "model_id": model_id,
                    "status": "error",
                    "error_message": str(result) if not isinstance(result, dict) else "Unknown error",
                    "duration_seconds": 0,
                    "cost_usd": 0
                }
                responder_results[model_id] = error_result
                materializer_results[model_id] = error_result
        
        # Combine results
        combined_results = {
            "responder_phase": responder_results,
            "materializer_phase": materializer_results,
            "timing_analysis": self._analyze_chain_timings(responder_results, materializer_results)
        }
        
        return combined_results
    
    async def _benchmark_single_model_chain(
        self,
        user_input: str,
        model_id: str,
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Run complete chain (responder + materializer) for a single model"""
        model_config = get_model_by_id(model_id)
        if not model_config:
            raise ValueError(f"Model {model_id} not found")
        
        try:
            # Phase 1: Responder (Content Generation)
            if progress_callback:
                await progress_callback(session_id, model_id, "responder_start", {"phase": "Content Generation", "model": model_id})
            
            responder_prompt = self.generate_responder_prompt(user_input)
            responder_result = await self._benchmark_single_agent(
                responder_prompt, model_config, "responder", session_id, progress_callback
            )
            
            # Phase 2: Materializer (Layout Generation) 
            if progress_callback:
                await progress_callback(session_id, model_id, "materializer_start", {"phase": "Layout Generation", "model": model_id})
            
            materializer_prompt = self.generate_materializer_prompt(user_input)
            materializer_result = await self._benchmark_single_agent(
                materializer_prompt, model_config, "materializer", session_id, progress_callback
            )
            
            # Send chain completion immediately when THIS model finishes
            if progress_callback and responder_result.get("status") == "success" and materializer_result.get("status") == "success":
                chain_completion_result = {
                    "model_id": model_id,
                    "status": "success",
                    "responder_phase": {model_id: responder_result},
                    "materializer_phase": {model_id: materializer_result},
                    "timing_analysis": {
                        "total_time": (responder_result.get("duration_seconds", 0) + materializer_result.get("duration_seconds", 0)),
                        "responder_time": responder_result.get("duration_seconds", 0),
                        "materializer_time": materializer_result.get("duration_seconds", 0)
                    }
                }
                await progress_callback(session_id, model_id, "chain_completed", chain_completion_result)
            
            return {
                "responder_result": responder_result,
                "materializer_result": materializer_result
            }
            
        except Exception as e:
            error_result = {
                "model_id": model_id,
                "model_name": model_config.get("name", model_id),
                "status": "error",
                "error_message": str(e),
                "duration_seconds": 0,
                "cost_usd": 0
            }
            
            if progress_callback:
                await progress_callback(session_id, model_id, "error", error_result)
            
            return {
                "responder_result": error_result,
                "materializer_result": error_result
            }
    
    async def _benchmark_single_agent(
        self, 
        prompt: str, 
        model_config: Dict[str, Any], 
        agent_type: str,
        session_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Benchmark a single agent with a specific model"""
        model_id = model_config["id"]
        
        try:
            # Send progress update
            if progress_callback:
                await progress_callback(session_id, model_id, "running", {"agent": agent_type})
            
            # Choose client and method based on agent type
            if model_config["provider"] == "openai":
                if agent_type == "responder":
                    # Use content generation (no HTML template) for responder
                    result = await self.openai_client.generate_content(prompt, model_config)
                else:
                    # Use HTML generation for materializer
                    result = await self.openai_client.generate_html_with_retry(prompt, model_config)
            elif model_config["provider"] == "anthropic":
                if agent_type == "responder":
                    # Use content generation (no HTML template) for responder
                    result = await self.anthropic_client.generate_content(prompt, model_config)
                else:
                    # Use HTML generation for materializer
                    result = await self.anthropic_client.generate_html(prompt, model_config)
            else:
                raise ValueError(f"Unknown provider: {model_config['provider']}")
            
            # Add agent metadata
            result["agent_type"] = agent_type
            result["prompt_tokens"] = len(prompt.split()) * 1.3  # Rough estimation
            
            # Send completion update
            if progress_callback:
                await progress_callback(session_id, model_id, result["status"], result)
            
            return result
            
        except Exception as e:
            error_result = {
                "model_id": model_id,
                "model_name": model_config["name"],
                "provider": model_config["provider"],
                "agent_type": agent_type,
                "status": "error",
                "error_message": str(e),
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": 0,
                "cost_usd": 0
            }
            
            if progress_callback:
                await progress_callback(session_id, model_id, "error", error_result)
            
            return error_result
    
    def _analyze_chain_timings(self, responder_results: Dict, materializer_results: Dict) -> Dict[str, Any]:
        """Analyze timing differences between phases"""
        analysis = {
            "models_compared": [],
            "responder_fastest": None,
            "materializer_fastest": None,
            "total_time_by_model": {},
            "time_breakdown": {}
        }
        
        # Compare timings for each model
        for model_id in responder_results.keys():
            if model_id in materializer_results:
                resp_time = responder_results[model_id].get("duration_seconds", 0)
                mat_time = materializer_results[model_id].get("duration_seconds", 0)
                total_time = resp_time + mat_time
                
                analysis["models_compared"].append(model_id)
                analysis["total_time_by_model"][model_id] = total_time
                analysis["time_breakdown"][model_id] = {
                    "responder_time": resp_time,
                    "materializer_time": mat_time,
                    "total_time": total_time,
                    "responder_percentage": (resp_time / total_time * 100) if total_time > 0 else 0,
                    "materializer_percentage": (mat_time / total_time * 100) if total_time > 0 else 0
                }
        
        # Find fastest in each phase
        if analysis["models_compared"]:
            # Fastest responder
            fastest_resp = min(analysis["models_compared"], 
                             key=lambda x: responder_results[x].get("duration_seconds", float('inf')))
            analysis["responder_fastest"] = {
                "model_id": fastest_resp,
                "time": responder_results[fastest_resp].get("duration_seconds", 0)
            }
            
            # Fastest materializer
            fastest_mat = min(analysis["models_compared"],
                            key=lambda x: materializer_results[x].get("duration_seconds", float('inf')))
            analysis["materializer_fastest"] = {
                "model_id": fastest_mat,
                "time": materializer_results[fastest_mat].get("duration_seconds", 0)
            }
        
        return analysis
    
    def _calculate_summary_stats(self, session_data: Dict[str, Any]):
        """Calculate summary statistics for the session"""
        results = session_data.get("results", {})
        summary = session_data["summary"]
        
        if not results:
            return
        
        # Handle different result structures based on mode
        try:
            if session_data["mode"] == "chain":
                # Chain mode has nested structure
                all_results = {}
                if "responder_phase" in results and isinstance(results["responder_phase"], dict):
                    all_results.update(results["responder_phase"])
                if "materializer_phase" in results and isinstance(results["materializer_phase"], dict):
                    all_results.update({f"{k}_materializer": v for k, v in results["materializer_phase"].items()})
            else:
                # Single phase modes
                all_results = results if isinstance(results, dict) else {}
            
            # Count successes and failures
            for key, result in all_results.items():
                if isinstance(result, dict) and "status" in result:
                    try:
                        if result.get("status") == "success":
                            summary["completed"] += 1
                            summary["total_cost"] += result.get("cost_usd", 0)
                        else:
                            summary["failed"] += 1
                    except Exception as inner_e:
                        print(f"Error processing result for {key}: {inner_e}")
                        summary["failed"] += 1
        except Exception as e:
            print(f"Error in _calculate_summary_stats: {e}")
            # Set default values if calculation fails
            summary["completed"] = 0
            summary["failed"] = 1
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions"""
        return self.active_sessions.copy()
