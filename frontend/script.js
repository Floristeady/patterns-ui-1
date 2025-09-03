/**
 * AI Model Benchmarking Tool - Frontend JavaScript
 * Handles UI interactions, API calls, and real-time updates
 */

class BenchmarkApp {
    constructor() {
        this.models = {};
        this.selectedModels = new Set();
        this.currentSession = null;
        this.websocket = null;
        this.benchmarkState = {
            total: 0,
            completed: 0,
            running: new Set(),
            firstCompleted: false
        };
        this.progressToast = null;
        
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadModels();
        this.updateUI();
    }

    bindEvents() {
        // Main action button
        document.getElementById('runBenchmarkBtn').addEventListener('click', () => this.runBenchmark());
        
        // Model selector button
        document.getElementById('modelSelectorBtn').addEventListener('click', () => this.toggleModelDropdown());
        
        // New test button
        document.getElementById('newTestBtn').addEventListener('click', () => this.resetForNewTest());
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('modelDropdown');
            const button = document.getElementById('modelSelectorBtn');
            if (!dropdown.contains(e.target) && !button.contains(e.target)) {
                this.closeModelDropdown();
            }
        });
        

        
        // Prompt input
        document.getElementById('promptInput').addEventListener('input', () => this.updateUI());
        

    }

    async loadModels() {
        try {
            this.showStatus('Loading available models...', 'info');
            
            const response = await fetch('/api/models');
            const data = await response.json();
            
            this.models = data;
            this.renderModelSelection();
            
            this.showStatus('Models loaded successfully', 'success');
            
        } catch (error) {
            console.error('Error loading models:', error);
            this.showStatus('Failed to load models', 'error');
        }
    }

    renderModelSelection() {
        const container = document.getElementById('modelDropdown');
        container.innerHTML = '';

        // Add "Select All Models" option at the top
        const selectAllItem = document.createElement('div');
        selectAllItem.className = 'select-all-item';
        selectAllItem.innerHTML = `
            <label class="select-all-label">
                <input 
                    type="checkbox" 
                    class="select-all-checkbox" 
                    id="selectAllCheckbox"
                >
                <span class="select-all-text">Select All Models</span>
            </label>
        `;
        container.appendChild(selectAllItem);

        for (const [category, models] of Object.entries(this.models)) {
            const enabledModels = models.filter(m => m.enabled);
            if (enabledModels.length === 0) continue;

            // Category header
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'model-dropdown-header';
            categoryHeader.textContent = this.formatCategoryName(category);
            container.appendChild(categoryHeader);
            
            // Models in this category
            enabledModels.forEach(model => {
                const modelItem = document.createElement('div');
                modelItem.className = 'model-dropdown-item';
                modelItem.innerHTML = this.renderDropdownModelItem(model);
                container.appendChild(modelItem);
            });
        }

        // Select all models by default
        container.querySelectorAll('.model-dropdown-checkbox:not(:disabled)').forEach(checkbox => {
            checkbox.checked = true;
            this.selectedModels.add(checkbox.value);
        });
        
        // Set "Select All" checkbox state
        this.updateSelectAllCheckbox();
        
        // Bind "Select All" checkbox event
        const selectAllCheckbox = document.getElementById('selectAllCheckbox');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.handleSelectAllChange(e.target.checked);
            });
        }
        
        // Bind model checkbox events
        container.querySelectorAll('.model-dropdown-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const modelId = e.target.value;
                if (e.target.checked) {
                    this.selectedModels.add(modelId);
                } else {
                    this.selectedModels.delete(modelId);
                }
                this.updateSelectAllCheckbox();
                this.updateUI();
            });
        });
    }

    renderDropdownModelItem(model) {
        const isLegacy = model.name.includes('[Legacy]');
        
        return `
            <label class="model-dropdown-label" data-model-id="${model.id}">
                <input 
                    type="checkbox" 
                    class="model-dropdown-checkbox" 
                    value="${model.id}"
                    ${!model.enabled ? 'disabled' : ''}
                >
                <div class="model-dropdown-info">
                    <div class="model-dropdown-name">${model.name}</div>
                    <div class="model-dropdown-details">
                        <span class="model-provider">${model.provider}</span>
                        ${isLegacy ? '<span class="legacy-badge">Legacy</span>' : ''}
                    </div>
                </div>
            </label>
        `;
    }

    formatCategoryName(category) {
        const names = {
            'nano': 'Nano Models',
            'mini': 'Mini Models',
            'normal': 'Standard Models',
            'premium': 'Premium Models',
            'reasoning': 'Reasoning Models'
        };
        return names[category] || category;
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(0) + 'K';
        }
        return num.toString();
    }

    toggleModelDropdown() {
        const dropdown = document.getElementById('modelDropdown');
        const arrow = document.querySelector('.dropdown-arrow');
        
        if (dropdown.classList.contains('hidden')) {
            dropdown.classList.remove('hidden');
            arrow.classList.add('open');
        } else {
            dropdown.classList.add('hidden');
            arrow.classList.remove('open');
        }
    }
    
    closeModelDropdown() {
        const dropdown = document.getElementById('modelDropdown');
        const arrow = document.querySelector('.dropdown-arrow');
        
        dropdown.classList.add('hidden');
        arrow.classList.remove('open');
    }
    
    handleSelectAllChange(isChecked) {
        const checkboxes = document.querySelectorAll('.model-dropdown-checkbox:not(:disabled)');
        
        if (isChecked) {
            // Select all models
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
                this.selectedModels.add(checkbox.value);
            });
        } else {
            // Deselect all models
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
                this.selectedModels.delete(checkbox.value);
            });
            this.selectedModels.clear();
        }
        
        this.updateUI();
    }
    
    updateSelectAllCheckbox() {
        const selectAllCheckbox = document.getElementById('selectAllCheckbox');
        if (!selectAllCheckbox) return;
        
        const totalCheckboxes = document.querySelectorAll('.model-dropdown-checkbox:not(:disabled)').length;
        const checkedCheckboxes = document.querySelectorAll('.model-dropdown-checkbox:not(:disabled):checked').length;
        
        if (checkedCheckboxes === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checkedCheckboxes === totalCheckboxes) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }

    selectAllModels() {
        document.querySelectorAll('.model-checkbox:not(:disabled)').forEach(checkbox => {
            checkbox.checked = true;
            this.selectedModels.add(checkbox.value);
        });
        this.updateUI();
    }

    deselectAllModels() {
        document.querySelectorAll('.model-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        this.selectedModels.clear();
        this.updateUI();
    }

    updateUI() {
        const prompt = document.getElementById('promptInput').value.trim();
        const hasPrompt = prompt.length > 0;
        const hasSelectedModels = this.selectedModels.size > 0;
        
        // Update run button
        const runBtn = document.getElementById('runBenchmarkBtn');
        runBtn.disabled = !hasPrompt || !hasSelectedModels;
        
        if (hasSelectedModels) {
            runBtn.textContent = `Generate with ${this.selectedModels.size} Model${this.selectedModels.size > 1 ? 's' : ''}`;
        } else {
            runBtn.textContent = 'Generate with Selected Models';
        }
        
        // Update model selector text
        const selectorText = document.getElementById('modelSelectorText');
        if (selectorText) {
            if (this.selectedModels.size === 0) {
                selectorText.textContent = 'No models selected';
            } else {
                const allModelsCount = document.querySelectorAll('.model-dropdown-checkbox:not(:disabled)').length;
                if (this.selectedModels.size === allModelsCount) {
                    selectorText.textContent = 'All models selected';
                } else {
                    const selectedModelNames = Array.from(this.selectedModels).map(id => {
                        const model = this.findModelById(id);
                        return model ? model.name.split(' ')[0] : id; // Just first word
                    }).join(', ');
                    
                    if (selectedModelNames.length > 30) {
                        selectorText.textContent = `${this.selectedModels.size} models selected`;
                    } else {
                        selectorText.textContent = selectedModelNames;
                    }
                }
            }
        }
        
        // Update cost estimate
        this.updateCostEstimate();
    }

    updateCostEstimate() {
        const estimateDiv = document.getElementById('costEstimate');
        
        if (this.selectedModels.size === 0) {
            estimateDiv.style.display = 'none';
            return;
        }

        let totalEstimatedCost = 0;
        const prompt = document.getElementById('promptInput').value.trim();
        const estimatedInputTokens = Math.max(50, prompt.length / 4); // Rough estimate
        const estimatedOutputTokens = 400; // Typical HTML output

        for (const modelId of this.selectedModels) {
            const model = this.findModelById(modelId);
            if (model) {
                const inputCost = (estimatedInputTokens / 1000000) * model.cost_per_million_tokens.input;
                const outputCost = (estimatedOutputTokens / 1000000) * model.cost_per_million_tokens.output;
                totalEstimatedCost += inputCost + outputCost;
            }
        }

        estimateDiv.style.display = 'block';
        estimateDiv.innerHTML = `
            Estimated cost: $${totalEstimatedCost.toFixed(6)} 
            (${this.selectedModels.size} model${this.selectedModels.size > 1 ? 's' : ''})
        `;
    }

    findModelById(modelId) {
        for (const models of Object.values(this.models)) {
            const model = models.find(m => m.id === modelId);
            if (model) return model;
        }
        return null;
    }

    async runBenchmark() {
        const prompt = document.getElementById('promptInput').value.trim();
        const selectedModelsArray = Array.from(this.selectedModels);
        const contentLevel = document.getElementById('contentSelector').value;
        const benchmarkMode = document.getElementById('benchmarkMode').value;
        this.currentBenchmarkMode = benchmarkMode; // Store for WebSocket handling

        if (!prompt || selectedModelsArray.length === 0) {
            this.showStatus('Please enter a prompt and select at least one model', 'error');
            return;
        }

        try {
            // Show loading
            this.showLoading(true);
            this.showStatus('Starting benchmark...', 'info');

            let response;
            
            // Choose API endpoint based on benchmark mode
            if (benchmarkMode === 'traditional') {
                // Use original benchmark API
                response = await fetch('/api/benchmark', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        selected_models: selectedModelsArray,
                        content_level: contentLevel
                    })
                });
            } else {
                // Use new agent benchmark API
                response = await fetch('/api/benchmark/agents', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_input: prompt,
                        selected_models: selectedModelsArray,
                        benchmark_mode: benchmarkMode
                    })
                });
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to start benchmark');
            }

            const result = await response.json();
            
            // Set up WebSocket for real-time updates
            this.setupWebSocket(result.session_id);
            
            // Initialize results display
            this.initializeResults(prompt, selectedModelsArray, benchmarkMode);
            
            const modeText = benchmarkMode === 'traditional' ? 'POC' : 
                           benchmarkMode === 'responder' ? 'Content' :
                           benchmarkMode === 'materializer' ? 'Materializer (Layout)' : 'Chain (Both)';
            
            this.showStatus(`${modeText} benchmark started! Watch for real-time updates...`, 'success');

        } catch (error) {
            console.error('Error starting benchmark:', error);
            this.showStatus(`Failed to start benchmark: ${error.message}`, 'error');
            this.showLoading(false);
        }
    }

    setupWebSocket(sessionId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/benchmark/${sessionId}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketUpdate(data);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showStatus('Connection error. Results may not update in real-time.', 'error');
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.showLoading(false);
        };
    }

    handleWebSocketUpdate(data) {
        console.log('WebSocket update:', data);
        
        if (data.model_id && data.status) {
            // For Chain mode, only process chain_completed updates
            if (this.currentBenchmarkMode === 'chain') {
                if (data.status === "chain_completed" && data.result) {
                    console.log('Chain completed - updating UI with final results');
                    this.updateChainModeResult(data.model_id, "success", data.result);
                } else if (data.result && data.result.responder_phase && data.result.materializer_phase) {
                    console.log('Chain completed (fallback) - updating UI with final results');
                    this.updateChainModeResult(data.model_id, data.status, data.result);
                } else {
                    // For Chain mode, show phase progress but don't update final results
                    console.log('Chain phase update:', data.status, 'for', data.model_id);
                    this.updateChainPhaseProgress(data.model_id, data.status, data.result);
                    return;
                }
            } else {
                // For non-Chain modes, process normally
                this.updateModelResult(data.model_id, data.status, data.result);
            }
            
            // Update benchmark progress (convert chain_completed to success for progress tracking)
            const progressStatus = data.status === "chain_completed" ? "success" : data.status;
            this.updateBenchmarkProgress(data.model_id, progressStatus);
        }
        
        // Check if all models are complete
        this.checkBenchmarkCompletion();
    }

    updateChainPhaseProgress(modelId, status, result) {
        const resultItem = document.getElementById(`result-${modelId}`);
        if (!resultItem) return;
        
        // Just update the status text to show progress, don't change data
        const statusText = resultItem.querySelector('.status-text');
        if (statusText) {
            if (result && result.agent_type === 'responder') {
                statusText.textContent = 'Content phase completed...';
            } else if (result && result.agent_type === 'materializer') {
                statusText.textContent = 'Layout phase completed...';
            }
        }
    }

    updateChainModeResult(modelId, status, chainResult) {
        const resultItem = document.getElementById(`result-${modelId}`);
        if (!resultItem) return;
        
        // Update main class
        resultItem.className = `result-item ${status} chain-mode`;
        
        // Get elements
        const contentTimeEl = resultItem.querySelector('.result-content-time');
        const layoutTimeEl = resultItem.querySelector('.result-layout-time');
        const durationEl = resultItem.querySelector('.result-duration');
        const costTokensEl = resultItem.querySelector('.result-cost-tokens');
        const tooltipContent = resultItem.querySelector('.tooltip-content');
        
        if (status === 'success' && chainResult.responder_phase && chainResult.materializer_phase) {
            // Get data for this specific model from both phases
            const responderData = chainResult.responder_phase[modelId];
            const materializerData = chainResult.materializer_phase[modelId];
            
            if (responderData && materializerData) {
                // Update times
                const contentTime = responderData.duration_seconds || 0;
                const layoutTime = materializerData.duration_seconds || 0;
                const totalTime = contentTime + layoutTime;
                
                if (contentTimeEl) contentTimeEl.textContent = `${contentTime.toFixed(1)}s`;
                if (layoutTimeEl) layoutTimeEl.textContent = `${layoutTime.toFixed(1)}s`;
                if (durationEl) durationEl.textContent = `${totalTime.toFixed(1)}s`;
                
                // Update cost (sum of both phases)
                const totalCost = (responderData.cost_usd || 0) + (materializerData.cost_usd || 0);
                const totalTokens = (responderData.total_tokens || 0) + (materializerData.total_tokens || 0);
                if (costTokensEl) {
                    costTokensEl.textContent = `$${totalCost.toFixed(4)} (${totalTokens})`;
                }
                
                // Update tooltip with chain-specific information
                if (tooltipContent) {
                    const startTime = responderData.start_time ? new Date(responderData.start_time).toLocaleTimeString() : '-';
                    const endTime = materializerData.end_time ? new Date(materializerData.end_time).toLocaleTimeString() : '-';
                    
                    tooltipContent.innerHTML = `
                        Started: ${startTime}<br>
                        Ended: ${endTime}<br>
                        Content Phase: ${contentTime.toFixed(1)}s ($${(responderData.cost_usd || 0).toFixed(4)})<br>
                        Layout Phase: ${layoutTime.toFixed(1)}s ($${(materializerData.cost_usd || 0).toFixed(4)})<br>
                        Total tokens: ${totalTokens}<br>
                        Status: Chain Completed
                    `;
                }
                
                // Enable View HTML button for chain mode - merge content + template
                const viewBtn = resultItem.querySelector('.view-html-btn');
                if (viewBtn && materializerData.html_content && responderData.html_content) {
                    viewBtn.disabled = false;
                    viewBtn.onclick = () => this.viewChainHtml(modelId, responderData.html_content, materializerData.html_content);
                }
            }
        } else {
            // Handle error/timeout cases
            if (contentTimeEl) contentTimeEl.textContent = '-';
            if (layoutTimeEl) layoutTimeEl.textContent = '-';
            if (durationEl) durationEl.textContent = '-';
            if (costTokensEl) costTokensEl.textContent = '-';
            
            if (tooltipContent) {
                tooltipContent.innerHTML = `
                    Started: -<br>
                    Ended: -<br>
                    Content Phase: Failed<br>
                    Layout Phase: Failed<br>
                    Total tokens: -<br>
                    Status: ${status === 'timeout' ? 'Timeout' : 'Error'}
                `;
            }
        }
    }

    initializeResults(prompt, selectedModels, benchmarkMode = 'traditional') {
        // Initialize benchmark state
        this.benchmarkState = {
            total: selectedModels.length,
            completed: 0,
            running: new Set(selectedModels),
            firstCompleted: false
        };
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        
        // Update session info
        const sessionInfo = document.getElementById('sessionInfo');
        const benchmarkTypeText = benchmarkMode === 'traditional' ? 'POC' : 
                                 benchmarkMode === 'responder' ? 'Content' :
                                 benchmarkMode === 'materializer' ? 'Materializer (Layout)' : 'Chain (Both Separated)';
        
        sessionInfo.innerHTML = `
            <strong>Test Started:</strong> ${new Date().toLocaleString()}<br>
            <strong>Benchmark Type:</strong> ${benchmarkTypeText}<br>
            <strong>Prompt:</strong> ${prompt.substring(0, 150)}${prompt.length > 150 ? '...' : ''}<br>
            <strong>Selected Models:</strong> ${selectedModels.length}
        `;
        
        // Initialize results table
        const resultsTable = document.getElementById('resultsTable');
        resultsTable.innerHTML = '<div class="results-grid" id="resultsGrid"></div>';
        
        // Create result items for each model
        const resultsGrid = document.getElementById('resultsGrid');
        
        // Add header row
        this.addTableHeader(resultsGrid, benchmarkMode);
        
        selectedModels.forEach(modelId => {
            const model = this.findModelById(modelId);
            const resultItem = document.createElement('div');
            resultItem.className = `result-item running ${benchmarkMode === 'chain' ? 'chain-mode' : ''}`;
            resultItem.id = `result-${modelId}`;
            resultItem.dataset.benchmarkMode = benchmarkMode; // Store benchmark mode for later use
            
            if (benchmarkMode === 'chain') {
                // Chain mode: Model | Benchmark | Content Time | Layout Time | Total | Cost | Actions
                resultItem.innerHTML = `
                    <div class="result-model">${model ? model.name : modelId}</div>
                    <div class="result-benchmark-type">
                        <span class="benchmark-badge chain">⛓️ Chain</span>
                    </div>
                    <div class="result-content-time">-</div>
                    <div class="result-layout-time">-</div>
                    <div class="result-duration">-</div>
                    <div class="result-cost-tokens">-</div>
                    <div class="result-actions">
                        <div class="info-tooltip">
                            ℹ️
                            <div class="tooltip-content">
                                Started: ${new Date().toLocaleTimeString()}<br>
                                Ended: -<br>
                                Input tokens: -<br>
                                Output tokens: -<br>
                                Agent: -<br>
                                Status: Running...
                            </div>
                        </div>
                        <button class="btn btn-secondary view-html-btn" disabled>View HTML</button>
                    </div>
                `;
            } else {
                // Simple modes: Model | Benchmark | Duration | Cost | Status | Actions
                const benchmarkInfo = this.getBenchmarkInfo(benchmarkMode);
                const buttonText = benchmarkMode === 'responder' ? 'View JSON' : 'View HTML';
                resultItem.innerHTML = `
                    <div class="result-model">${model ? model.name : modelId}</div>
                    <div class="result-benchmark-type">
                        <span class="benchmark-badge ${benchmarkMode}">${benchmarkInfo.icon} ${benchmarkInfo.name}</span>
                    </div>
                    <div class="result-duration">-</div>
                    <div class="result-cost-tokens">-</div>
                    <div class="result-status">
                        <span class="status-icon running"></span>
                        <span class="status-text">Running...</span>
                    </div>
                    <div class="result-actions">
                        <div class="info-tooltip">
                            ℹ️
                            <div class="tooltip-content">
                                Started: ${new Date().toLocaleTimeString()}<br>
                                Ended: -<br>
                                Input tokens: -<br>
                                Output tokens: -<br>
                                Agent: -<br>
                                Status: Running...
                            </div>
                        </div>
                        <button class="btn btn-secondary view-html-btn" disabled>${buttonText}</button>
                    </div>
                `;
            }
            
            resultsGrid.appendChild(resultItem);
        });
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
    }

    addTableHeader(resultsGrid, benchmarkMode) {
        const headerRow = document.createElement('div');
        headerRow.className = `result-item header ${benchmarkMode === 'chain' ? 'chain-mode' : ''}`;
        headerRow.style.background = 'var(--bg-white)';
        headerRow.style.fontWeight = '600';
        headerRow.style.borderLeft = '4px solid var(--border-medium)';
        
        if (benchmarkMode === 'chain') {
            headerRow.innerHTML = `
                <div>Model</div>
                <div>Benchmark</div>
                <div>Content Time</div>
                <div>Layout Time</div>
                <div>Total Time</div>
                <div>Cost</div>
                <div>Actions</div>
            `;
        } else {
            headerRow.innerHTML = `
                <div>Model</div>
                <div>Benchmark</div>
                <div>Duration</div>
                <div>Cost</div>
                <div>Status</div>
                <div>Actions</div>
            `;
        }
        
        resultsGrid.appendChild(headerRow);
    }

    getBenchmarkInfo(benchmarkMode) {
        const benchmarkTypes = {
            'traditional': { icon: '🔄', name: 'POC' },
            'responder': { icon: '📝', name: 'Content' },
            'materializer': { icon: '🎨', name: 'Materializer' },
            'chain': { icon: '⛓️', name: 'Chain' }
        };
        
        return benchmarkTypes[benchmarkMode] || { icon: '❓', name: 'Unknown' };
    }

    updateModelResult(modelId, status, result) {
        const resultItem = document.getElementById(`result-${modelId}`);
        if (!resultItem) return;
        
        // Update main class
        const isChainMode = resultItem.classList.contains('chain-mode');
        resultItem.className = `result-item ${status} ${isChainMode ? 'chain-mode' : ''}`;
        
        // Get elements
        const durationEl = resultItem.querySelector('.result-duration');
        const costTokensEl = resultItem.querySelector('.result-cost-tokens');
        const tooltipContent = resultItem.querySelector('.tooltip-content');
        
        // Chain mode specific elements
        const contentTimeEl = resultItem.querySelector('.result-content-time');
        const layoutTimeEl = resultItem.querySelector('.result-layout-time');
        
        // Simple mode specific elements
        const statusIcon = resultItem.querySelector('.status-icon');
        const statusText = resultItem.querySelector('.status-text');
        
        // Update tooltip with detailed information
        if (tooltipContent && result) {
            const startTime = result.start_time ? new Date(result.start_time).toLocaleTimeString() : '-';
            const endTime = result.end_time ? new Date(result.end_time).toLocaleTimeString() : '-';
            const inputTokens = result.input_tokens || result.prompt_tokens || '-';
            const outputTokens = result.output_tokens || '-';
            const agentType = result.agent_type || 'traditional';
            const statusText = status === 'success' ? 'Success' : 
                             status === 'error' ? `Error: ${result.error_message || 'Unknown error'}` :
                             status === 'timeout' ? 'Timeout' : 'Running...';
            
            tooltipContent.innerHTML = `
                Started: ${startTime}<br>
                Ended: ${endTime}<br>
                Input tokens: ${inputTokens}<br>
                Output tokens: ${outputTokens}<br>
                Agent: ${agentType}<br>
                Status: ${statusText}
            `;
        }
        
        // Update based on status
        switch (status) {
            case 'success':
                if (isChainMode) {
                    // For chain mode, we need to handle the phase results differently
                    // This will be updated when we receive chain results
                    if (contentTimeEl) contentTimeEl.textContent = '-'; // Will be updated with chain data
                    if (layoutTimeEl) layoutTimeEl.textContent = '-';   // Will be updated with chain data
                }
                
                if (durationEl) {
                    durationEl.textContent = result.duration_seconds ? `${result.duration_seconds.toFixed(1)}s` : '-';
                }
                
                if (costTokensEl) {
                    const cost = result.cost_usd ? `$${result.cost_usd.toFixed(4)}` : '-';
                    const tokens = result.total_tokens || (result.input_tokens + result.output_tokens) || 0;
                    costTokensEl.textContent = tokens > 0 ? `${cost} (${tokens})` : cost;
                }
                
                // Update status for simple modes
                if (statusIcon && statusText) {
                    statusIcon.className = `status-icon success`;
                    statusText.textContent = 'Completed';
                }
                
                // Enable View HTML/JSON button
                const viewBtn = resultItem.querySelector('.view-html-btn');
                if (viewBtn && result.html_content) {
                    viewBtn.disabled = false;
                    
                    // Update button text based on benchmark mode
                    const benchmarkMode = resultItem.dataset.benchmarkMode;
                    if (benchmarkMode === 'responder') {
                        viewBtn.textContent = 'View JSON';
                    } else {
                        viewBtn.textContent = 'View HTML';
                    }
                    
                    viewBtn.onclick = () => this.viewContent(modelId, result);
                }
                break;
                
            case 'error':
            case 'timeout':
                if (durationEl) {
                    durationEl.textContent = result.duration_seconds ? `${result.duration_seconds.toFixed(1)}s` : '-';
                }
                if (costTokensEl) {
                    costTokensEl.textContent = '-';
                }
                
                // Update status for simple modes
                if (statusIcon && statusText) {
                    statusIcon.className = `status-icon ${status}`;
                    statusText.textContent = status === 'timeout' ? 'Timeout' : 'Failed';
                }
                
                // Update chain mode times
                if (isChainMode) {
                    if (contentTimeEl) contentTimeEl.textContent = '-';
                    if (layoutTimeEl) layoutTimeEl.textContent = '-';
                }
                break;
                
            default:
                // Running state
                if (statusIcon && statusText) {
                    statusIcon.className = `status-icon running`;
                    statusText.textContent = 'Running...';
                }
        }
    }

    updateBenchmarkProgress(modelId, status) {
        // Update running models
        if (status === 'success' || status === 'error' || status === 'timeout') {
            this.benchmarkState.running.delete(modelId);
            this.benchmarkState.completed++;
            
            // If this is the first completed model
            if (!this.benchmarkState.firstCompleted) {
                this.benchmarkState.firstCompleted = true;
                // Transition from fullscreen loading to progress toast
                this.transitionToProgressiveLoading();
            }
            
            // Update progress toast
            this.updateProgressToast();
        }
    }
    
    transitionToProgressiveLoading() {
        // Hide fullscreen loading
        this.showLoading(false);
        
        // Show progress toast if there are still running models
        if (this.benchmarkState.running.size > 0) {
            this.showProgressToast();
        }
    }
    
    showProgressToast() {
        const remaining = this.benchmarkState.running.size;
        const completed = this.benchmarkState.completed;
        const total = this.benchmarkState.total;
        
        // Create progress message
        const modelNames = Array.from(this.benchmarkState.running).map(modelId => {
            const model = this.findModelById(modelId);
            return model ? model.name.split(' ')[0] : modelId;
        });
        
        const message = `⏳ Processing ${remaining} remaining model${remaining > 1 ? 's' : ''}: ${modelNames.join(', ')}`;
        const progress = `(${completed}/${total} completed)`;
        
        this.progressToast = this.showStatus(`${message} ${progress}`, 'info', false); // Don't auto-remove
    }
    
    updateProgressToast() {
        if (this.progressToast && this.benchmarkState.running.size > 0) {
            const remaining = this.benchmarkState.running.size;
            const completed = this.benchmarkState.completed;
            const total = this.benchmarkState.total;
            
            const modelNames = Array.from(this.benchmarkState.running).map(modelId => {
                const model = this.findModelById(modelId);
                return model ? model.name.split(' ')[0] : modelId;
            });
            
            const message = `⏳ Processing ${remaining} remaining model${remaining > 1 ? 's' : ''}: ${modelNames.join(', ')}`;
            const progress = `(${completed}/${total} completed)`;
            
            this.progressToast.textContent = `${message} ${progress}`;
        } else if (this.progressToast) {
            // Remove progress toast when all models complete
            this.removeProgressToast();
        }
    }
    
    removeProgressToast() {
        if (this.progressToast && this.progressToast.parentNode) {
            this.progressToast.parentNode.removeChild(this.progressToast);
            this.progressToast = null;
        }
    }

    checkBenchmarkCompletion() {
        const runningItems = document.querySelectorAll('.result-item.running');
        if (runningItems.length === 0) {
            // All models completed
            this.showLoading(false);
            this.removeProgressToast(); // Remove progress toast
            this.showStatus('Benchmark completed!', 'success');
            this.updateSummaryStats();
            
            if (this.websocket) {
                this.websocket.close();
            }
        }
    }

    updateSummaryStats() {
        const resultItems = document.querySelectorAll('.result-item');
        const successful = document.querySelectorAll('.result-item.success').length;
        const failed = document.querySelectorAll('.result-item.error, .result-item.timeout').length;
        
        let totalCost = 0;
        let fastestTime = Infinity;
        let slowestTime = 0;
        let fastestModel = '';
        let slowestModel = '';
        
        resultItems.forEach(item => {
            const costText = item.querySelector('.result-duration').textContent;
            if (costText && costText !== '-') {
                const time = parseFloat(costText);
                if (time < fastestTime) {
                    fastestTime = time;
                    fastestModel = item.querySelector('.result-model').textContent;
                }
                if (time > slowestTime) {
                    slowestTime = time;
                    slowestModel = item.querySelector('.result-model').textContent;
                }
            }
            
            const costTokensEl = item.querySelector('.result-cost-tokens').textContent;
            if (costTokensEl && costTokensEl.startsWith('$')) {
                // Extract cost from format "$0.22 (677)"
                const costMatch = costTokensEl.match(/\$(\d+\.?\d*)/);
                if (costMatch) {
                    totalCost += parseFloat(costMatch[1]);
                }
            }
        });
        
        const summaryDiv = document.getElementById('summaryStats');
        summaryDiv.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${successful}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">$${totalCost.toFixed(6)}</div>
                <div class="stat-label">Total Cost</div>
            </div>
            ${fastestTime < Infinity ? `
                <div class="stat-item">
                    <div class="stat-value">${fastestTime}s</div>
                    <div class="stat-label">Fastest (${fastestModel})</div>
                </div>
            ` : ''}
            ${slowestTime > 0 ? `
                <div class="stat-item">
                    <div class="stat-value">${slowestTime}s</div>
                    <div class="stat-label">Slowest (${slowestModel})</div>
                </div>
            ` : ''}
        `;
    }

    viewContent(modelId, result) {
        const content = result.html_content;
        
        // Detect if content is JSON or HTML
        let isJSON = false;
        try {
            JSON.parse(content);
            isJSON = true;
        } catch (e) {
            isJSON = false;
        }
        
        if (isJSON) {
            // Handle JSON content - create a formatted HTML page to display it
            const formattedJSON = JSON.stringify(JSON.parse(content), null, 2);
            const htmlWrapper = `
<!DOCTYPE html>
<html>
<head>
    <title>JSON Response - ${modelId}</title>
    <style>
        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .model-name {
            color: #2d3748;
            font-size: 18px;
            font-weight: 600;
        }
        .content-type {
            color: #718096;
            font-size: 14px;
        }
        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .copy-btn {
            background: #4299e1;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 10px;
        }
        .copy-btn:hover {
            background: #3182ce;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="model-name">Model: ${result.model_name || modelId}</div>
            <div class="content-type">Content Type: JSON Response</div>
        </div>
        <button class="copy-btn" onclick="copyToClipboard()">Copy JSON</button>
        <pre id="jsonContent">${formattedJSON}</pre>
    </div>
    
    <script>
        function copyToClipboard() {
            const content = document.getElementById('jsonContent').textContent;
            navigator.clipboard.writeText(content).then(() => {
                alert('JSON copied to clipboard!');
            });
        }
    </script>
</body>
</html>`;
            
            const blob = new Blob([htmlWrapper], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const newWindow = window.open(url, '_blank');
            
            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 1000);
            
        } else {
            // Handle HTML content (original behavior)
            const blob = new Blob([content], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const newWindow = window.open(url, '_blank');
            
            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 1000);
        }
        
        // Store current result for other actions
        this.currentViewResult = result;
    }

    viewChainHtml(modelId, jsonContent, htmlTemplate) {
        try {
            // Parse JSON content
            const contentData = JSON.parse(jsonContent);
            
            // Merge content with template
            const mergedHtml = this.mergeContentWithTemplate(contentData, htmlTemplate);
            
            // Create blob URL for merged HTML
            const blob = new Blob([mergedHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            
            // Open in new tab
            const newWindow = window.open(url, '_blank');
            
            // Clean up blob URL
            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 1000);
            
        } catch (error) {
            console.error('Error merging Chain HTML:', error);
            alert('Error al generar HTML final. Mostrando template sin contenido.');
            
            // Fallback to template only
            const blob = new Blob([htmlTemplate], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const newWindow = window.open(url, '_blank');
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        }
    }

    mergeContentWithTemplate(contentData, htmlTemplate) {
        // Flatten nested JSON structure
        const flatData = this.flattenJson(contentData);
        
        // Find all placeholders in template
        const placeholderRegex = /\{\{([^}]+)\}\}/g;
        const placeholders = [];
        let match;
        while ((match = placeholderRegex.exec(htmlTemplate)) !== null) {
            placeholders.push(match[1].trim());
        }
        
        // Create mapping of placeholders to values
        const mapping = this.smartMapping(placeholders, flatData);
        
        // Replace placeholders in template
        let result = htmlTemplate;
        for (const [placeholder, value] of Object.entries(mapping)) {
            const regex = new RegExp(`\\{\\{\\s*${placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*\\}\\}`, 'g');
            result = result.replace(regex, String(value));
        }
        
        return result;
    }

    flattenJson(data, prefix = '') {
        const result = {};
        
        if (typeof data === 'object' && data !== null) {
            if (Array.isArray(data)) {
                data.forEach((item, index) => {
                    const newKey = prefix ? `${prefix}_${index + 1}` : `item_${index + 1}`;
                    Object.assign(result, this.flattenJson(item, newKey));
                });
            } else {
                for (const [key, value] of Object.entries(data)) {
                    const newKey = prefix ? `${prefix}_${key}` : key;
                    if (typeof value === 'object' && value !== null) {
                        Object.assign(result, this.flattenJson(value, newKey));
                    } else {
                        result[newKey] = String(value);
                    }
                }
            }
        } else {
            result[prefix || 'value'] = String(data);
        }
        
        return result;
    }

    smartMapping(placeholders, flatData) {
        const mapping = {};
        const flatDataLower = {};
        
        // Create lowercase version for flexible matching
        for (const [key, value] of Object.entries(flatData)) {
            flatDataLower[key.toLowerCase()] = value;
        }
        
        for (const placeholder of placeholders) {
            const placeholderLower = placeholder.toLowerCase();
            let value = null;
            
            // Strategy 1: Exact match
            if (flatData[placeholder]) {
                value = flatData[placeholder];
            } else if (flatDataLower[placeholderLower]) {
                value = flatDataLower[placeholderLower];
            }
            // Strategy 2: Keyword matching
            else if (!value) {
                value = this.matchByKeywords(placeholderLower, flatData);
            }
            // Strategy 3: Similarity matching
            else if (!value) {
                value = this.matchBySimilarity(placeholderLower, flatData);
            }
            
            mapping[placeholder] = value || `[${placeholder}]`; // Fallback
        }
        
        return mapping;
    }

    matchByKeywords(placeholder, flatData) {
        const keywordMap = {
            'title': ['title', 'name', 'heading', 'header'],
            'name': ['name', 'title', 'label'],
            'description': ['description', 'desc', 'content', 'text', 'summary'],
            'price': ['price', 'cost', 'amount', 'value'],
            'image': ['image', 'img', 'photo', 'picture'],
            'url': ['url', 'link', 'href'],
            'date': ['date', 'time', 'created', 'updated']
        };
        
        // Find keyword type for placeholder
        for (const [keyType, keywords] of Object.entries(keywordMap)) {
            if (keywords.some(kw => placeholder.includes(kw))) {
                // Find matching data key
                for (const [dataKey, dataValue] of Object.entries(flatData)) {
                    if (keywords.some(kw => dataKey.toLowerCase().includes(kw))) {
                        return dataValue;
                    }
                }
            }
        }
        
        return null;
    }

    matchBySimilarity(placeholder, flatData) {
        let bestMatch = null;
        let bestScore = 0;
        
        const placeholderWords = new Set(placeholder.split('_'));
        
        for (const [dataKey, dataValue] of Object.entries(flatData)) {
            const dataWords = new Set(dataKey.toLowerCase().split('_'));
            const commonWords = [...placeholderWords].filter(word => dataWords.has(word));
            const score = commonWords.length / Math.max(placeholderWords.size, 1);
            
            if (score > bestScore && score > 0.3) {
                bestScore = score;
                bestMatch = dataValue;
            }
        }
        
        return bestMatch;
    }





    resetForNewTest() {
        // Hide results section
        document.getElementById('resultsSection').style.display = 'none';
        
        // Clear selections
        this.deselectAllModels();
        
        // Clear prompt
        document.getElementById('promptInput').value = '';
        
        // Reset state
        this.currentSession = null;
        this.benchmarkState = {
            total: 0,
            completed: 0,
            running: new Set(),
            firstCompleted: false
        };
        this.removeProgressToast();
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // Update UI
        this.updateUI();
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showStatus(message, type = 'info', autoRemove = true) {
        const container = document.getElementById('statusMessages');
        
        const statusDiv = document.createElement('div');
        statusDiv.className = `status-message ${type}`;
        statusDiv.textContent = message;
        
        container.appendChild(statusDiv);
        
        // Auto-remove after 5 seconds if autoRemove is true
        if (autoRemove) {
            setTimeout(() => {
                if (statusDiv.parentNode) {
                    statusDiv.parentNode.removeChild(statusDiv);
                }
            }, 5000);
        }
        
        return statusDiv; // Return element for external management
    }
    // Temporary method to test Chain mode with real data
    testChainModeWithRealData() {
        const testChainResult = {
            "responder_phase": {
                "claude_haiku35": {
                    "model_id": "claude_haiku35",
                    "status": "success", 
                    "duration_seconds": 4.627,
                    "cost_usd": 0.001234,
                    "total_tokens": 500,
                    "html_content": '{"dashboard": {"title": "Metrics Dashboard"}}',
                    "start_time": new Date().toISOString(),
                    "end_time": new Date().toISOString()
                }
            },
            "materializer_phase": {
                "claude_haiku35": {
                    "model_id": "claude_haiku35",
                    "status": "success",
                    "duration_seconds": 20.414, 
                    "cost_usd": 0.002461,
                    "total_tokens": 800,
                    "html_content": '<!DOCTYPE html><html><body><h1>{{title}}</h1></body></html>',
                    "start_time": new Date().toISOString(),
                    "end_time": new Date().toISOString()
                }
            }
        };
        
        console.log('Testing Chain mode with real data...');
        this.updateChainModeResult("claude_haiku35", "success", testChainResult);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BenchmarkApp();
    
    // Make test function available in console
    window.testChain = () => window.app.testChainModeWithRealData();
});
