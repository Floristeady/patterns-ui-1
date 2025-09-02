# Product Requirements Document (PRD)
## AI Model Speed Benchmark for UI Pattern Generation
## date 2025-01-01 (Updated with latest AI models)

### 1. Executive Summary

**Product**: Benchmarking tool to measure HTML/CSS code generation speed across different AI models.

**Objective**: Compare performance (response time) of multiple AI models when generating UI patterns from natural language descriptions.

**MVP Scope**: Local web application that allows users to input a UI description, select which models to test, execute the same request across selected models simultaneously, and display comparative response times.

### 2. Technical Specifications

#### 2.1 Technology Stack
- **Backend**: Python (FastAPI or Flask)
- **Frontend**: HTML, CSS, Vanilla JavaScript (minimalist design)
- **APIs**: OpenAI API, Anthropic API
- **Storage**: Local file system

#### 2.2 Available Models

**Nano Category:**
- GPT-5 Nano (OpenAI)
- GPT-4.1 Nano (OpenAI)

**Mini Category:**
- GPT-5 Mini (OpenAI)
- GPT-4.1 Mini (OpenAI)
- GPT-4o-mini (OpenAI) [Legacy]
- Claude 3 Haiku (Anthropic) [Legacy]

**Normal Category:**
- GPT-5 (OpenAI)
- GPT-4.1 (OpenAI)
- Claude 4 Sonnet (Anthropic)
- GPT-4o (OpenAI) [Legacy]
- Claude 3.5 Sonnet (Anthropic) [Legacy]

**Premium Category:**
- Claude 4.1 Opus (Anthropic)

**Reasoning Category:**
- o1-preview (OpenAI)
- o1-mini (OpenAI)

### 3. Core Features

#### 3.1 Main Interface
```
┌─────────────────────────────────────────────┐
│  AI UI Generation Speed Test                │
├─────────────────────────────────────────────┤
│                                             │
│  Describe the UI pattern you need:          │
│  ┌─────────────────────────────────────┐   │
│  │                                     │   │
│  │  [Text area for description]        │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Select models to test:                     │
│  ┌─────────────────────────────────────┐   │
│  │ Nano:                               │   │
│  │ ☑ GPT-5 Nano   ☑ GPT-4.1 Nano      │   │
│  │                                     │   │
│  │ Mini:                               │   │
│  │ ☑ GPT-5 Mini   ☑ GPT-4.1 Mini      │   │
│  │                                     │   │
│  │ Normal:                             │   │
│  │ ☑ GPT-5        ☑ Claude 4 Sonnet   │   │
│  │ ☑ GPT-4.1                          │   │
│  │                                     │   │
│  │ Premium:                            │   │
│  │ ☑ Claude 4.1 Opus                  │   │
│  │                                     │   │
│  │ Reasoning:                          │   │
│  │ ☑ o1-preview   ☑ o1-mini           │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [Select All] [Deselect All]                │
│  [Generate with Selected Models]            │
│                                             │
└─────────────────────────────────────────────┘
```

#### 3.2 Results View
```
┌─────────────────────────────────────────────┐
│  Generation Results                         │
├─────────────────────────────────────────────┤
│                                             │
│  Test Started: 2024-08-29 10:30:15         │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Model         Start    End    Duration│   │
│  ├─────────────────────────────────────┤   │
│  │ Nano Models:                         │   │
│  │ GPT-5 Nano    10:30:15 10:30:16 1.2s│   │
│  │               [View HTML] ✓         │   │
│  │                                     │   │
│  │ Mini Models:                         │   │
│  │ GPT-5 Mini    10:30:15 10:30:17 1.8s│   │
│  │               [View HTML] ✓         │   │
│  │                                     │   │
│  │ Normal Models:                       │   │
│  │ GPT-5         10:30:15 10:30:19 2.8s│   │
│  │               [View HTML] ✓         │   │
│  │                                     │   │
│  │ Claude 4 Sonnet 10:30:15 10:30:18 3.2s│   │
│  │               [View HTML] ✓         │   │
│  │                                     │   │
│  │ Premium Models:                      │   │
│  │ Claude 4.1 Opus 10:30:15 10:30:22 6.8s│   │
│  │               [View HTML] ✓         │   │
│  │                                     │   │
│  │ Reasoning Models:                    │   │
│  │ o1-preview    10:30:15 10:30:24 8.7s│   │
│  │               [View HTML] ✓         │   │
│  │                                     │   │
│  │ o1-mini       10:30:15 10:30:20 5.4s│   │
│  │               [View HTML] ✓         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [New Test] [Download Results]              │
└─────────────────────────────────────────────┘
```

### 4. User Flow

1. User enters UI pattern description
2. User selects which models to test (all selected by default)
3. Click "Generate with Selected Models"
4. System sends the same prompt to each selected model (in parallel)
5. System displays real-time status for each model (pending/running/completed/error)
6. System measures time from request start to response completion
7. System saves each generated HTML in local folder
8. System displays comparative times with start/end timestamps
9. User can open each HTML in new tab

### 5. Data Structure

#### 5.1 Prompt Template
```python
prompt_template = """
Generate ONLY HTML code with inline CSS for the following UI pattern:

{user_description}

Requirements:
- Valid, complete HTML5
- CSS must be inline (style attributes)
- JavaScript only if absolutely necessary
- Must be responsive
- Use realistic example content

Respond ONLY with the HTML code, no explanations.
"""
```

#### 5.2 File Structure
```
/outputs
  /template_YYYYMMDD_HHMMSS
    /gpt5_nano.html
    /gpt41_nano.html
    /gpt5_mini.html
    /gpt41_mini.html
    /gpt5.html
    /gpt41.html
    /claude4_sonnet.html
    /claude41_opus.html
    /o1_preview.html
    /o1_mini.html
    /legacy/
      /gpt4o_mini.html
      /claude_haiku.html
      /gpt4o.html
      /claude_sonnet.html
    /metadata.json
```

#### 5.3 Metadata JSON
```json
{
  "timestamp": "2024-08-29T10:30:15",
  "prompt": "3 column grid with 9 cards...",
  "selected_models": ["gpt5_nano", "gpt5_mini", "gpt5", "claude4_sonnet"],
  "results": {
    "gpt5_nano": {
      "start_time": "2024-08-29T10:30:15.123",
      "end_time": "2024-08-29T10:30:16.323",
      "duration_seconds": 1.2,
      "tokens_used": 380,
      "cost_usd": 0.00015,
      "status": "success",
      "error": null
    },
    "gpt5_mini": {
      "start_time": "2024-08-29T10:30:15.125",
      "end_time": "2024-08-29T10:30:16.925",
      "duration_seconds": 1.8,
      "tokens_used": 420,
      "cost_usd": 0.0008,
      "status": "success",
      "error": null
    },
    "gpt5": {
      "start_time": "2024-08-29T10:30:15.127",
      "end_time": "2024-08-29T10:30:17.927",
      "duration_seconds": 2.8,
      "tokens_used": 580,
      "cost_usd": 0.0045,
      "status": "success",
      "error": null
    },
    "claude4_sonnet": {
      "start_time": "2024-08-29T10:30:15.129",
      "end_time": null,
      "duration_seconds": null,
      "tokens_used": null,
      "cost_usd": null,
      "status": "error",
      "error": "API rate limit exceeded"
    }
  }
}
```

### 6. Model Status States

Each model should display one of these states during execution:
- **Pending**: Gray, waiting to start
- **Running**: Blue with spinner, processing
- **Success**: Green checkmark, completed
- **Error**: Red X, failed with error message

### 7. Error Handling

- If a model fails, display error status but continue with other models
- Show specific error message (rate limit, timeout, API error)
- Allow retry for individual failed models
- Log all errors with timestamps

### 8. Non-Functional Requirements

- **Performance**: Parallel API calls using asyncio
- **Timeout**: 30 seconds maximum per model
- **UI**: Minimalist, no CSS frameworks, light background, system fonts
- **Security**: API keys in local .env file
- **Real-time updates**: Show progress as models complete

### 9. Initial Configuration

#### 9.1 .env File
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

#### 9.2 config.py
```python
MODELS = {
    "nano": [
        {
            "id": "gpt5_nano",
            "name": "GPT-5 Nano", 
            "provider": "openai", 
            "model_id": "gpt-5-nano",
            "enabled": True,
            "cost_per_million_tokens": {"input": 0.1, "output": 0.4}
        },
        {
            "id": "gpt41_nano",
            "name": "GPT-4.1 Nano", 
            "provider": "openai", 
            "model_id": "gpt-4.1-nano",
            "enabled": True,
            "cost_per_million_tokens": {"input": 0.1, "output": 0.4}
        }
    ],
    "mini": [
        {
            "id": "gpt5_mini",
            "name": "GPT-5 Mini", 
            "provider": "openai", 
            "model_id": "gpt-5-mini",
            "enabled": True,
            "cost_per_million_tokens": {"input": 0.25, "output": 2.0}
        },
        {
            "id": "gpt41_mini",
            "name": "GPT-4.1 Mini", 
            "provider": "openai", 
            "model_id": "gpt-4.1-mini",
            "enabled": True,
            "cost_per_million_tokens": {"input": 0.4, "output": 1.6}
        },
        {
            "id": "gpt4o_mini",
            "name": "GPT-4o-mini [Legacy]", 
            "provider": "openai", 
            "model_id": "gpt-4o-mini",
            "enabled": False,
            "cost_per_million_tokens": {"input": 0.15, "output": 0.6}
        },
        {
            "id": "claude_haiku",
            "name": "Claude 3 Haiku [Legacy]", 
            "provider": "anthropic", 
            "model_id": "claude-3-haiku-20240307",
            "enabled": False,
            "cost_per_million_tokens": {"input": 0.25, "output": 1.25}
        }
    ],
    "normal": [
        {
            "id": "gpt5",
            "name": "GPT-5", 
            "provider": "openai", 
            "model_id": "gpt-5",
            "enabled": True,
            "cost_per_million_tokens": {"input": 2.5, "output": 10.0}
        },
        {
            "id": "gpt41",
            "name": "GPT-4.1", 
            "provider": "openai", 
            "model_id": "gpt-4.1",
            "enabled": True,
            "cost_per_million_tokens": {"input": 2.0, "output": 8.0}
        },
        {
            "id": "claude4_sonnet",
            "name": "Claude 4 Sonnet", 
            "provider": "anthropic", 
            "model_id": "claude-4-sonnet-20250522",
            "enabled": True,
            "cost_per_million_tokens": {"input": 3.0, "output": 15.0}
        },
        {
            "id": "gpt4o",
            "name": "GPT-4o [Legacy]", 
            "provider": "openai", 
            "model_id": "gpt-4o",
            "enabled": False,
            "cost_per_million_tokens": {"input": 5.0, "output": 15.0}
        },
        {
            "id": "claude_sonnet",
            "name": "Claude 3.5 Sonnet [Legacy]", 
            "provider": "anthropic", 
            "model_id": "claude-3-5-sonnet-20240620",
            "enabled": False,
            "cost_per_million_tokens": {"input": 3.0, "output": 15.0}
        }
    ],
    "premium": [
        {
            "id": "claude41_opus",
            "name": "Claude 4.1 Opus", 
            "provider": "anthropic", 
            "model_id": "claude-4.1-opus-20250322",
            "enabled": True,
            "cost_per_million_tokens": {"input": 15.0, "output": 75.0}
        }
    ],
    "reasoning": [
        {
            "id": "o1_preview",
            "name": "o1-preview", 
            "provider": "openai", 
            "model_id": "o1-preview",
            "enabled": True,
            "cost_per_million_tokens": {"input": 15.0, "output": 60.0}
        },
        {
            "id": "o1_mini",
            "name": "o1-mini", 
            "provider": "openai", 
            "model_id": "o1-mini",
            "enabled": True,
            "cost_per_million_tokens": {"input": 3.0, "output": 12.0}
        }
    ]
}
```

### 10. Acceptance Criteria

1. ✓ User can input UI pattern description
2. ✓ User can select/deselect individual models to test across all categories (Nano, Mini, Normal, Premium, Reasoning)
3. ✓ System executes prompt on selected models in parallel
4. ✓ System displays real-time status for each model
5. ✓ System shows start time, end time, duration, and estimated cost for each model
6. ✓ System handles errors gracefully without stopping other models
7. ✓ System saves generated HTML in organized folder structure
8. ✓ User can view generated HTML in new tab
9. ✓ Interface groups models by category (including new Nano and Premium categories)
10. ✓ "Select All" and "Deselect All" buttons work correctly for each category
11. ✓ System tracks and displays cost information per test
12. ✓ Legacy models are properly marked and disabled by default
13. ✓ System supports latest API endpoints for new models

### 11. API Response Handling

```python
async def generate_with_model(model_config, prompt):
    """
    Returns:
    {
        "model_id": "gpt4o_mini",
        "start_time": datetime,
        "end_time": datetime,
        "duration": float,
        "status": "success|error",
        "html_content": str or None,
        "error_message": str or None
    }
    """
```

### 12. Cost Considerations

#### 12.1 Model Pricing (USD per million tokens)

| Category | Model | Input | Output | Est. Cost per Test* |
|----------|-------|--------|--------|---------------------|
| Nano | GPT-5 Nano | $0.10 | $0.40 | $0.0002 |
| Nano | GPT-4.1 Nano | $0.10 | $0.40 | $0.0002 |
| Mini | GPT-5 Mini | $0.25 | $2.00 | $0.0008 |
| Mini | GPT-4.1 Mini | $0.40 | $1.60 | $0.0008 |
| Normal | GPT-5 | $2.50 | $10.00 | $0.0045 |
| Normal | GPT-4.1 | $2.00 | $8.00 | $0.0036 |
| Normal | Claude 4 Sonnet | $3.00 | $15.00 | $0.0065 |
| Premium | Claude 4.1 Opus | $15.00 | $75.00 | $0.033 |
| Reasoning | o1-preview | $15.00 | $60.00 | $0.027 |
| Reasoning | o1-mini | $3.00 | $12.00 | $0.0054 |

*Estimated cost assumes ~150 input tokens + ~400 output tokens per test

#### 12.2 Budget Management Features

- Real-time cost tracking per test session
- Daily/monthly spending limits
- Cost estimates before running tests
- Model selection based on budget constraints
- Historical cost analysis and reporting

### 13. Future Enhancements (Post-MVP)

- Test history with search/filter
- Side-by-side visual comparison
- Quality scoring with human feedback
- Predefined UI pattern templates
- Iterative result modification with follow-up prompts
- Export results (CSV, JSON, PDF reports)
- Server deployment with multi-user support
- Custom prompt templates per model category
- Batch testing with multiple prompts
- A/B testing for UI variations
- Integration with design systems and component libraries
- Performance benchmarking (loading speed, accessibility)
- Model fine-tuning based on user preferences
