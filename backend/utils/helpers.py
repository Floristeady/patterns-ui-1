"""
Utility functions and helpers for the benchmarking application
"""

import re
import html
from typing import Dict, Any, Optional
from datetime import datetime


def sanitize_html_content(html_content: str) -> str:
    """
    Basic sanitization of HTML content for safety
    Note: For production use, consider using a proper HTML sanitizer like bleach
    """
    if not html_content:
        return ""
    
    # Remove script tags and their content
    html_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content, flags=re.IGNORECASE)
    
    # Remove dangerous event handlers
    dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout', 'onfocus', 'onblur']
    for attr in dangerous_attrs:
        html_content = re.sub(f'{attr}\\s*=\\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
    
    return html_content


def extract_html_title(html_content: str) -> str:
    """Extract title from HTML content"""
    if not html_content:
        return "Generated HTML"
    
    # Try to find title tag
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
    if title_match:
        return title_match.group(1).strip()
    
    # Try to find h1 tag
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
    if h1_match:
        return h1_match.group(1).strip()
    
    return "Generated HTML"


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way"""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def format_cost(cost_usd: float) -> str:
    """Format cost in a human-readable way"""
    if cost_usd < 0.001:
        return f"${cost_usd:.6f}"
    elif cost_usd < 0.01:
        return f"${cost_usd:.4f}"
    else:
        return f"${cost_usd:.2f}"


def format_tokens(tokens: int) -> str:
    """Format token count in a human-readable way"""
    if tokens >= 1000000:
        return f"{tokens/1000000:.1f}M"
    elif tokens >= 1000:
        return f"{tokens/1000:.1f}K"
    else:
        return str(tokens)


def validate_prompt(prompt: str) -> Dict[str, Any]:
    """
    Validate user prompt and return validation result
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not prompt or not prompt.strip():
        result["valid"] = False
        result["errors"].append("Prompt cannot be empty")
        return result
    
    prompt = prompt.strip()
    
    # Check minimum length
    if len(prompt) < 10:
        result["warnings"].append("Very short prompt might produce generic results")
    
    # Check maximum length
    if len(prompt) > 2000:
        result["warnings"].append("Very long prompt might exceed token limits for some models")
    
    # Check for potentially problematic content
    problematic_patterns = [
        r'\b(hack|exploit|vulnerability|malicious)\b',
        r'\b(password|secret|private key|api key)\b',
        r'\b(adult|explicit|inappropriate)\b'
    ]
    
    for pattern in problematic_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            result["warnings"].append("Prompt contains potentially sensitive content")
            break
    
    return result


def estimate_tokens_from_text(text: str) -> int:
    """
    Rough estimation of tokens from text
    More accurate than simple word count but not as precise as actual tokenization
    """
    if not text:
        return 0
    
    # Rough approximation: 1 token ≈ 4 characters for English text
    # This is a simplification, actual tokenization is more complex
    return max(1, len(text) // 4)


def generate_session_summary(session_data: Dict[str, Any]) -> str:
    """Generate a human-readable summary of a benchmark session"""
    if not session_data:
        return "No session data available"
    
    summary_lines = []
    
    # Basic info
    summary_lines.append(f"Session: {session_data.get('session_id', 'Unknown')}")
    summary_lines.append(f"Started: {session_data.get('start_time', 'Unknown')}")
    
    if session_data.get('duration_seconds'):
        summary_lines.append(f"Duration: {format_duration(session_data['duration_seconds'])}")
    
    # Results summary
    results = session_data.get('results', {})
    if results:
        successful = sum(1 for r in results.values() if r.get('status') == 'success')
        total = len(results)
        summary_lines.append(f"Models: {successful}/{total} successful")
        
        # Total cost
        total_cost = sum(r.get('cost_usd', 0) for r in results.values() if r.get('cost_usd'))
        if total_cost > 0:
            summary_lines.append(f"Total cost: {format_cost(total_cost)}")
    
    # Performance stats
    summary_stats = session_data.get('summary', {})
    if summary_stats.get('fastest_model'):
        fastest = summary_stats['fastest_model']
        summary_lines.append(f"Fastest: {fastest['model_name']} ({format_duration(fastest['duration_seconds'])})")
    
    return " | ".join(summary_lines)


def clean_filename(filename: str) -> str:
    """Clean filename to be filesystem-safe"""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    # Ensure it's not empty
    if not filename.strip():
        filename = "untitled"
    
    return filename.strip()


def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serialize objects to JSON-compatible format
    Handles datetime objects and other non-serializable types
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return safe_json_serialize(obj.__dict__)
    else:
        return obj
