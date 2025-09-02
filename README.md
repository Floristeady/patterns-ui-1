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

## 📊 Supported Models (Updated September 2025)

### Nano Category (Ultra-fast) ⚡
- **GPT-5 Nano** ✅ - ~30s response time, $0.002 per test

### Mini Category (Fast & Efficient) 🚀
- **GPT-5 Mini** ✅ - ~120s response time, $0.016 per test
- **Claude 3.5 Haiku** ✅ - ~22s response time, budget-friendly

### Normal Category (Balanced) ⚖️
- **GPT-5** ✅ - High quality, 180s timeout
- **Claude Sonnet 4** ✅ - ~60s response time, $0.095 per test
- **Claude 3.5 Sonnet (Latest)** ✅ - ~12s response time, stable model

### Premium Category (Highest Quality) 💎
- **Claude Opus 4.1** ✅ - Premium quality, higher cost

### Reasoning Category (Complex Tasks) 🧠
- **o1-mini** ✅ - ~12s response time, $0.030 per test
- **o3-mini** ✅ - ~29s response time, $0.017 per test

**Total: 9 active models** | **Legacy models disabled by default**

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

### Speed Recommendations
- **Fastest**: o1-mini (~12s) or GPT-5 Nano (~30s) for quick iterations
- **Balanced**: Claude 3.5 Haiku (~22s) for cost-effective quality
- **Quality**: Claude Sonnet 4 (~60s) for detailed, complex UIs
- **Reasoning**: o3-mini (~29s) for logic-heavy components

### Cost Optimization
- **Budget**: Claude 3.5 Haiku - excellent quality/cost ratio
- **Premium**: GPT-5 Mini - slower but very cost-effective per token
- **Avoid**: Running all 8 models simultaneously (high cost)

### Best Practices
- Start with 2-3 models for initial testing
- Use nano/mini models for rapid iteration
- Monitor your API usage and costs in real-time
- GPT-5 models may take 2-3 minutes for complex requests

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
