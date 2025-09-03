"""
Anthropic API Client for benchmarking
Handles communication with Claude models including Claude 4 Sonnet and Claude 4.1 Opus
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
import anthropic
from config import ANTHROPIC_API_KEY, API_TIMEOUT, PROMPT_TEMPLATE


class AnthropicClient:
    """Async client for Anthropic API with benchmarking capabilities"""
    
    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
    def count_tokens(self, text: str) -> int:
        """Estimate tokens for Claude models (rough approximation)"""
        # Claude uses approximately 1 token per 4 characters
        return len(text) // 4
    
    def clean_html_content(self, content: str) -> str:
        """Clean HTML content by fixing data URIs and other formatting issues"""
        if not content:
            return content
        
        import re
        import urllib.parse
        
        # Fix data URI SVGs by properly encoding them
        def fix_data_uri(match):
            full_match = match.group(0)
            svg_content = match.group(1)
            
            # Properly encode the SVG content for data URI
            encoded_svg = urllib.parse.quote(svg_content, safe='')
            
            return f"url('data:image/svg+xml,{encoded_svg}')"
        
        # Pattern to match data URI SVGs that are causing issues
        pattern = r"url\('data:image/svg\+xml,(<svg[^']*</svg>)'\)"
        content = re.sub(pattern, fix_data_uri, content)
        
        # Also fix any remaining quote issues in data URIs
        content = re.sub(r'data:image/svg\+xml,<svg([^>]*)"([^"]*)"([^>]*)', 
                        r"data:image/svg+xml,<svg\1'\2'\3", content)
        
        # Remove any trailing quote issues that might remain
        content = re.sub(r"'\); opacity: 0\.3;\">", "'); opacity: 0.3;\">", content)
        
        return content.strip()
    
    def get_model_timeout(self, model_config: Dict[str, Any]) -> int:
        """Get appropriate timeout for the model"""
        # Use custom timeout if specified in model config
        if "timeout" in model_config:
            return model_config["timeout"]
        
        # Default timeout for Anthropic models
        return API_TIMEOUT
    
    async def generate_content(self, prompt: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content using Anthropic model without HTML template
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
            "provider": "anthropic",
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
            # Handle streaming requirement for Claude Sonnet 4 and other models
            try:
                # First try without streaming
                response = await asyncio.wait_for(
                    self.client.messages.create(
                        model=model_id,
                        max_tokens=model_config.get("max_tokens", 8192),
                        temperature=0.3,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    ),
                    timeout=timeout
                )
            except Exception as e:
                error_msg = str(e)
                if "Streaming is required" in error_msg:
                    # If streaming is required, use reduced max_tokens to avoid the issue
                    print(f"Retrying {model_config['name']} content generation with reduced tokens...")
                    response = await asyncio.wait_for(
                        self.client.messages.create(
                            model=model_id,
                            max_tokens=8192,  # Reduced tokens to avoid streaming requirement
                            temperature=0.3,
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        ),
                        timeout=timeout
                    )
                else:
                    raise e
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract response content (no cleaning for JSON)
            raw_content = response.content[0].text.strip()
            
            # Token usage
            output_tokens = response.usage.output_tokens if response.usage else self.count_tokens(raw_content)
            total_tokens = input_tokens + output_tokens
            
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
    
    async def generate_html(self, prompt: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate HTML using Anthropic Claude model and return benchmarking results
        
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
            "provider": "anthropic",
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
            # Create message for Claude - handle streaming requirement gracefully
            try:
                # First try without streaming
                response = await asyncio.wait_for(
                    self.client.messages.create(
                        model=model_id,
                        max_tokens=model_config.get("max_tokens", 4096),
                        temperature=0.3,
                        system="You are a skilled frontend developer who creates clean, modern HTML with inline CSS. Always respond with complete, valid HTML code only. IMPORTANT: When using data URIs for SVG backgrounds, properly encode all special characters. Avoid using double quotes inside SVG data URIs - use single quotes or properly escape them.",
                        messages=[
                            {"role": "user", "content": full_prompt}
                        ]
                    ),
                    timeout=timeout
                )
            except Exception as e:
                error_msg = str(e)
                if "Streaming is required" in error_msg:
                    # If streaming is required, use a reduced max_tokens to avoid the issue
                    print(f"Retrying {model_config['name']} with reduced tokens...")
                    response = await asyncio.wait_for(
                        self.client.messages.create(
                            model=model_id,
                            max_tokens=8192,  # Reduced tokens to avoid streaming requirement
                            temperature=0.3,
                            system="You are a skilled frontend developer who creates clean, modern HTML with inline CSS. Always respond with complete, valid HTML code only. IMPORTANT: When using data URIs for SVG backgrounds, properly encode all special characters. Avoid using double quotes inside SVG data URIs - use single quotes or properly escape them.",
                            messages=[
                                {"role": "user", "content": full_prompt}
                            ]
                        ),
                        timeout=timeout
                    )
                else:
                    raise e
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract and clean response content
            html_content = ""
            for content_block in response.content:
                if content_block.type == "text":
                    html_content += content_block.text
            
            html_content = self.clean_html_content(html_content)
            
            # Token usage
            usage = response.usage
            input_tokens_used = usage.input_tokens if usage else input_tokens
            output_tokens = usage.output_tokens if usage else self.count_tokens(html_content)
            total_tokens = input_tokens_used + output_tokens
            
            # Calculate cost
            cost_config = model_config["cost_per_million_tokens"]
            input_cost = (input_tokens_used / 1_000_000) * cost_config["input"]
            output_cost = (output_tokens / 1_000_000) * cost_config["output"]
            total_cost = input_cost + output_cost
            
            # Update result
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "input_tokens": input_tokens_used,
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
            
        except anthropic.APIError as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 3),
                "status": "error",
                "error_message": f"Anthropic API Error: {str(e)}"
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
        """Test if Anthropic API connection is working"""
        try:
            # Try a simple message to test connection
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use a basic model for testing
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return len(response.content) > 0
        except Exception:
            return False
