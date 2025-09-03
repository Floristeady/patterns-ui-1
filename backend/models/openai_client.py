"""
OpenAI API Client for benchmarking
Handles communication with OpenAI models including GPT-5, GPT-4.1, and o1 series
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
import tiktoken
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, API_TIMEOUT, GPT5_TIMEOUT, PROMPT_TEMPLATE


class OpenAIClient:
    """Async client for OpenAI API with benchmarking capabilities"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Fallback to rough estimation if tiktoken fails
            return len(text.split()) * 1.3
    
    def clean_html_content(self, content: str) -> str:
        """Clean HTML content by removing markdown code blocks and extra formatting"""
        if not content:
            return content
        
        # Remove markdown code block markers
        content = content.strip()
        
        # Remove ```html at the beginning
        if content.startswith('```html'):
            content = content[7:].strip()
        elif content.startswith('```'):
            content = content[3:].strip()
        
        # Remove ``` at the end
        if content.endswith('```'):
            content = content[:-3].strip()
        
        # Remove any other common markdown artifacts
        content = content.replace('```html\n', '').replace('\n```', '')
        
        return content.strip()
    
    def get_model_timeout(self, model_config: Dict[str, Any]) -> int:
        """Get appropriate timeout for the model"""
        # Use custom timeout if specified in model config
        if "timeout" in model_config:
            return model_config["timeout"]
        
        # Use GPT5_TIMEOUT for GPT-5 models
        model_id = model_config["model_id"]
        if model_id.startswith("gpt-5"):
            return GPT5_TIMEOUT
        
        # Default timeout for other models
        return API_TIMEOUT
    
    async def generate_content(self, prompt: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content using OpenAI model without HTML template
        Used for content generation (JSON) in agent benchmarks
        """
        model_id = model_config["model_id"]
        start_time = datetime.now()
        timeout = self.get_model_timeout(model_config)
        
        # Use prompt directly without HTML template
        input_tokens = self.count_tokens(prompt)
        
        result = {
            "model_id": model_config["id"],
            "model_name": model_config["name"],
            "provider": "openai",
            "start_time": start_time.isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "input_tokens": input_tokens,
            "output_tokens": None,
            "total_tokens": None,
            "cost_usd": None,
            "status": "running",
            "html_content": None,  # Will contain JSON content for responder
            "error_message": None
        }
        
        try:
            # Special handling for o1 models (they don't support system messages)
            if model_id.startswith("o1-"):
                messages = [
                    {"role": "user", "content": prompt}
                ]
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=model_id,
                        messages=messages
                    ),
                    timeout=timeout
                )
            else:
                # Standard models with system/user pattern
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that generates structured data as requested."},
                    {"role": "user", "content": prompt}
                ]
                
                completion_params = {
                    "model": model_id,
                    "messages": messages
                }
                
                # Add parameters based on model type
                if model_id.startswith("gpt-5"):
                    # GPT-5 models - minimal parameters only
                    pass  # No additional parameters for GPT-5 models
                elif model_id.startswith("o3-"):
                    # o3 models - support reasoning_effort parameter
                    if "reasoning_effort" in model_config:
                        completion_params["reasoning_effort"] = model_config["reasoning_effort"]
                else:
                    completion_params["temperature"] = 0.3
                    completion_params["max_tokens"] = model_config.get("max_tokens", 4096)
                
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(**completion_params),
                    timeout=timeout
                )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract response content (no cleaning for JSON)
            raw_content = response.choices[0].message.content.strip()
            
            # Token usage
            usage = response.usage
            output_tokens = usage.completion_tokens if usage else self.count_tokens(raw_content)
            total_tokens = usage.total_tokens if usage else (input_tokens + output_tokens)
            
            # Calculate cost
            cost_config = model_config["cost_per_million_tokens"]
            input_cost = (input_tokens / 1_000_000) * cost_config["input"]
            output_cost = (output_tokens / 1_000_000) * cost_config["output"]
            total_cost = input_cost + output_cost
            
            # Update result
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost_usd": round(total_cost, 6),
                "status": "success",
                "html_content": raw_content  # Contains JSON for responder
            })
            
        except asyncio.TimeoutError:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "status": "timeout",
                "error_message": f"Request timed out after {timeout} seconds"
            })
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "status": "error",
                "error_message": str(e)
            })
        
        return result

    async def generate_html_with_retry(self, prompt: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HTML with retry logic for timeout issues"""
        retry_attempts = model_config.get("retry_attempts", 1)
        
        for attempt in range(retry_attempts):
            try:
                result = await self.generate_html(prompt, model_config)
                
                # If successful or not a timeout, return result
                if result["status"] != "timeout":
                    return result
                
                # If timeout and we have more attempts, continue
                if attempt < retry_attempts - 1:
                    print(f"Timeout on attempt {attempt + 1} for {model_config['name']}, retrying...")
                    continue
                
                # Last attempt failed, return the timeout result
                return result
                
            except Exception as e:
                # If not timeout error or last attempt, raise
                if attempt == retry_attempts - 1:
                    raise e
                continue
        
        # This shouldn't be reached, but just in case
        return await self.generate_html(prompt, model_config)
    
    async def generate_html(self, prompt: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate HTML using OpenAI model and return benchmarking results
        
        Args:
            prompt: User description of UI pattern
            model_config: Model configuration from config.py
            
        Returns:
            Dictionary with benchmarking results including timing, cost, and generated HTML
        """
        model_id = model_config["model_id"]
        start_time = datetime.now()
        timeout = self.get_model_timeout(model_config)
        
        # Prepare the full prompt
        full_prompt = PROMPT_TEMPLATE.format(user_description=prompt)
        input_tokens = self.count_tokens(full_prompt)
        
        result = {
            "model_id": model_config["id"],
            "model_name": model_config["name"],
            "provider": "openai",
            "start_time": start_time.isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "input_tokens": input_tokens,
            "output_tokens": None,
            "total_tokens": None,
            "cost_usd": None,
            "status": "running",
            "html_content": None,
            "error_message": None
        }
        
        try:
            # Special handling for o1 models (they don't support system messages)
            if model_id.startswith("o1-"):
                messages = [
                    {"role": "user", "content": full_prompt}
                ]
                # o1 models don't support max_tokens parameter
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=model_id,
                        messages=messages
                    ),
                    timeout=timeout
                )
            else:
                # Standard models with system/user pattern
                messages = [
                    {"role": "system", "content": "You are a skilled frontend developer who creates clean, modern HTML with inline CSS."},
                    {"role": "user", "content": full_prompt}
                ]
                
                # Prepare completion parameters
                completion_params = {
                    "model": model_id,
                    "messages": messages
                }
                
                # Add parameters based on model type
                if model_id.startswith("gpt-5"):
                    # GPT-5 models - minimal parameters only
                    pass  # No additional parameters for GPT-5 models
                elif model_id.startswith("o3-"):
                    # o3 models - support reasoning_effort parameter
                    if "reasoning_effort" in model_config:
                        completion_params["reasoning_effort"] = model_config["reasoning_effort"]
                else:
                    # Standard models support temperature and max_tokens
                    completion_params["temperature"] = 0.3  # Lower temperature for more consistent code generation
                    completion_params["max_tokens"] = model_config.get("max_tokens", 4096)
                
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(**completion_params),
                    timeout=timeout
                )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract and clean response content
            raw_content = response.choices[0].message.content.strip()
            html_content = self.clean_html_content(raw_content)
            
            # Token usage
            usage = response.usage
            output_tokens = usage.completion_tokens if usage else self.count_tokens(html_content)
            total_tokens = usage.total_tokens if usage else (input_tokens + output_tokens)
            
            # Calculate cost
            cost_config = model_config["cost_per_million_tokens"]
            input_cost = (input_tokens / 1_000_000) * cost_config["input"]
            output_cost = (output_tokens / 1_000_000) * cost_config["output"]
            total_cost = input_cost + output_cost
            
            # Update result
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost_usd": round(total_cost, 6),
                "status": "success",
                "html_content": html_content
            })
            
        except asyncio.TimeoutError:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "status": "timeout",
                "error_message": f"Request timed out after {timeout} seconds"
            })
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "status": "error",
                "error_message": str(e)
            })
        
        return result
    
    async def test_connection(self) -> bool:
        """Test if OpenAI API connection is working"""
        try:
            response = await self.client.models.list()
            return len(response.data) > 0
        except Exception:
            return False
