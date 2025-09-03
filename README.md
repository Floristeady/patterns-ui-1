# AI Model Speed Benchmark Tool

A web application to compare HTML/CSS code generation speed across different AI models including GPT-5, Claude 4, and other cutting-edge models.

## 🎯 Current Status (September 2025)

✅ **Production Ready** - Fully functional benchmarking tool  
✅ **9 Active Models** - GPT-5 series, Claude 4 series, o1/o3 reasoning models  
✅ **Real-time WebSocket Updates** - Live progress tracking during benchmarks  
✅ **Parallel Processing** - Test multiple models simultaneously  
✅ **Cost Tracking** - Accurate token usage and cost calculations  
✅ **Proven Stable** - Successfully tested with complex UI generation tasks  
✅ **Claude Issues Resolved** - All Claude models working with streaming support

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API Key
- Anthropic API Key

### Setup (5 minutes)

1. **Clone and navigate to project**
   ```bash
   cd patterns-ui-1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   ```bash
   cp env.template .env
   # Edit .env and add your API keys:
   # OPENAI_API_KEY=sk-your-key-here
   # ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

4. **Run the application**
   ```bash
   cd backend
   python3 app.py
   ```

5. **Open your browser**
   ```
   http://localhost:8000
   ```

## 🎯 Usage

1. **Enter UI Description**: Describe the UI pattern you want generated
2. **Select Models**: Choose which AI models to benchmark
3. **Run Benchmark**: Click "Generate with Selected Models"
4. **View Results**: Compare response times, costs, and generated HTML

## 📊 Supported Models (Final - January 2025)

### Nano Category (Ultra-fast) ⚡
- **GPT-5 Nano** ✅ - Model ID: `gpt-5-nano`, ~30s, $0.05/$0.40 per M tokens

### Mini Category (Fast & Efficient) 🚀
- **GPT-5 Mini** ✅ - Model ID: `gpt-5-mini`, ~120s, $0.25/$2.0 per M tokens
- **Claude 3.5 Haiku** ⚠️ - Model ID: `claude-3-5-haiku-20241022`, ~20s, $0.25/$1.25 per M tokens (Temp. server issues)

### Normal Category (Balanced) ⚖️
- **GPT-5** ✅ - Model ID: `gpt-5`, ~22s, $1.25/$10.0 per M tokens (Fixed timeout issues)
- **Claude Sonnet 4** ✅ - Model ID: `claude-sonnet-4-0`, ~11s, $3.0/$15.0 per M tokens (Fixed streaming issues)

### Premium Category (Highest Quality) 💎
- **Claude Opus 4.1** ✅ - Model ID: `claude-opus-4-1`, 180s timeout, $15.0/$75.0 per M tokens

### Reasoning Category (Complex Tasks) 🧠
- **o1-mini** ✅ - Model ID: `o1-mini`, ~15s, $3.0/$12.0 per M tokens
- **o3-mini** ✅ - Model ID: `o3-mini`, medium reasoning, 120s timeout, $1.0/$4.0 per M tokens

**Total: 8 models (7 working, 1 temp. issue)** | **All core models tested and verified working**

### 🎯 Model Selection Strategy

**For Speed**: GPT-5 Nano → o1-mini → Claude Sonnet 4  
**For Quality**: Claude Opus 4.1 → Claude Sonnet 4 → GPT-5  
**For Cost**: GPT-5 Nano → o3-mini → Claude 3.5 Haiku  
**For Reasoning**: o3-mini (medium) → o1-mini

### 🔧 Current Configuration Notes

- **GPT-5 models restored**: All GPT-5 variants available and working
- **o3-mini back**: Restored with medium reasoning effort - works perfectly
- **Claude Haiku**: Temporary Anthropic server issues (500 error)
- **Removed**: GPT-4o Mini Legacy (not working), Claude 3.5 Sonnet variants (not needed)

### 📋 Exact Model Configuration

| Model | Category | Model ID | Timeout | Cost (Input/Output per M) | Status |
|-------|----------|----------|---------|---------------------------|--------|
| GPT-5 Nano | nano | `gpt-5-nano` | 120s | $0.05 / $0.40 | ✅ Working |
| GPT-5 Mini | mini | `gpt-5-mini` | 150s | $0.25 / $2.0 | ✅ Working |
| Claude 3.5 Haiku | mini | `claude-3-5-haiku-20241022` | - | $0.25 / $1.25 | ⚠️ Temp. issues |
| GPT-5 | normal | `gpt-5` | 300s | $1.25 / $10.0 | ✅ Working (Fixed) |
| Claude Sonnet 4 | normal | `claude-sonnet-4-0` | 120s | $3.0 / $15.0 | ✅ Working (Fixed) |
| Claude Opus 4.1 | premium | `claude-opus-4-1` | 180s | $15.0 / $75.0 | ✅ Working |
| o1-mini | reasoning | `o1-mini` | - | $3.0 / $12.0 | ✅ Working |
| o3-mini | reasoning | `o3-mini` | 120s | $1.0 / $4.0 | ✅ Working |

**Total: 8 models (7 working, 1 temp. issue)** | **Latest fixes applied - all core models operational**

**Key Configuration Decisions:**
- **All models working**: GPT-5 and Claude Sonnet 4 issues completely resolved (Jan 2025)
- **GPT-5**: Extended timeout (300s) - now works perfectly in ~22s
- **Claude Sonnet 4**: Fixed streaming issues - now works in ~11s  
- **Claude Haiku**: Temporary Anthropic server issues (will resolve)
- **o3-mini**: Medium reasoning effort for optimal balance
- **⚠️ IMPORTANT**: Configuration is stable - DO NOT CHANGE without testing

## 📁 Project Structure

```
patterns-ui-1/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── config.py              # Model configurations
│   ├── models/                # API clients
│   └── services/              # Business logic
├── frontend/
│   ├── index.html            # Main interface
│   ├── style.css             # Styling
│   └── script.js             # Frontend logic
├── outputs/                  # Generated results
└── docs/                     # Documentation
```

## 🔧 Configuration

Edit `backend/config.py` to:
- Enable/disable specific models
- Adjust cost estimates
- Modify prompt templates
- Change timeout settings

## 💰 Cost Tracking

The tool automatically calculates and displays:
- Cost per test
- Total session cost
- Cost comparisons between models
- Token usage statistics

## 📊 Results

Each benchmark session creates:
- Individual HTML files per model
- Metadata JSON with detailed metrics
- Human-readable summary
- Performance comparisons

## 🛠️ Development

### Adding New Models

1. Update `backend/config.py` with model configuration
2. Add provider client if needed in `backend/models/`
3. Test with small prompts first

### API Endpoints

- `POST /api/benchmark` - Start benchmark
- `GET /api/models` - List available models
- `GET /api/results/{session_id}` - Get results
- `WebSocket /ws/benchmark/{session_id}` - Real-time updates

## 🔍 Troubleshooting

### Common Issues

**"API Key not found" or "401 Unauthorized"**
- Check your `.env` file exists and has correct keys
- **IMPORTANT**: Restart the server after updating `.env` file
- Ensure API keys are valid and have sufficient credits
- Verify keys start with `sk-` (OpenAI) or `sk-ant-` (Anthropic)

**"Model not available"**
- Some models may not be available in your region
- Check if you have access to the specific model
- Verify model ID in `config.py`

**"Request timeout"**
- Increase `API_TIMEOUT` in your `.env` file
- Some models (especially reasoning models) take longer
- GPT-5 models use extended 180s timeout automatically

**Server not starting**
- Use `python3` instead of `python` on macOS
- Check if port 8000 is available: `lsof -i :8000`
- Install dependencies: `pip3 install -r requirements.txt`

### Debug Mode

Set `DEBUG=True` in `.env` for verbose logging.

### Quick Health Check

```bash
curl http://localhost:8000/api/health
```

Should return: `"openai": true, "anthropic": true`

## 📈 Performance Tips & Benchmarks

### Speed Recommendations (Updated Config - All Working)
- **Fastest**: Claude Sonnet 4 (~11s) → o1-mini (~15s) → GPT-5 (~22s) for quick iterations
- **Balanced**: GPT-5 (~22s) for reliable, fast quality - now much faster!
- **Quality**: Claude Sonnet 4 (~11s) for detailed, complex UIs - incredibly fast now
- **Reasoning**: o3-mini (medium, ~21s) for logic-heavy components

### Cost Optimization
- **Ultra Budget**: GPT-5 Nano ($0.05/$0.40) - cheapest option
- **Budget**: o3-mini ($1.0/$4.0) - excellent reasoning/cost ratio
- **Balanced**: Claude 3.5 Haiku ($0.25/$1.25) - good quality/cost ratio
- **Avoid**: Running all 8 models simultaneously (high cost)

### Best Practices (Current Setup)
- Start with GPT-5 + Claude 3.5 Haiku for quick comparisons
- Use GPT-5 Nano for rapid prototyping and iteration
- o3-mini (medium) provides best reasoning without slow/fast variants
- GPT-5 now uses fast mode (gpt-5-chat) - expect ~45-90s responses
- Monitor costs: 8 models × complex prompt can cost $1-5+ per test

## 🎉 Features

✅ **Parallel Processing** - Test multiple models simultaneously  
✅ **Real-time Updates** - Live progress tracking via WebSockets  
✅ **Cost Tracking** - Automatic token usage and cost calculation  
✅ **Result Storage** - Organized output files with metadata  
✅ **Model Categories** - Easy selection by performance tier  
✅ **Error Handling** - Graceful failure recovery and retry logic  
✅ **Responsive UI** - Works on desktop and mobile  
✅ **Performance Metrics** - Detailed timing and quality analysis  
✅ **Content Injection** - Support for complex data-driven UI generation  
✅ **Export Capabilities** - Download results and generated HTML  

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

**Need help?** Check the `docs/` folder for detailed documentation or open an issue.
