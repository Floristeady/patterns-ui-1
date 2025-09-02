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

        if (!prompt || selectedModelsArray.length === 0) {
            this.showStatus('Please enter a prompt and select at least one model', 'error');
            return;
        }

        try {
            // Show loading
            this.showLoading(true);
            this.showStatus('Starting benchmark...', 'info');

            // Start benchmark
            const response = await fetch('/api/benchmark', {
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

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to start benchmark');
            }

            const result = await response.json();
            
            // Set up WebSocket for real-time updates
            this.setupWebSocket(result.session_id);
            
            // Initialize results display
            this.initializeResults(prompt, selectedModelsArray);
            
            this.showStatus('Benchmark started! Watch for real-time updates...', 'success');

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
            this.updateModelResult(data.model_id, data.status, data.result);
            
            // Update benchmark progress
            this.updateBenchmarkProgress(data.model_id, data.status);
        }
        
        // Check if all models are complete
        this.checkBenchmarkCompletion();
    }

    initializeResults(prompt, selectedModels) {
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
        sessionInfo.innerHTML = `
            <strong>Test Started:</strong> ${new Date().toLocaleString()}<br>
            <strong>Prompt:</strong> ${prompt.substring(0, 150)}${prompt.length > 150 ? '...' : ''}<br>
            <strong>Selected Models:</strong> ${selectedModels.length}
        `;
        
        // Initialize results table
        const resultsTable = document.getElementById('resultsTable');
        resultsTable.innerHTML = '<div class="results-grid" id="resultsGrid"></div>';
        
        // Create result items for each model
        const resultsGrid = document.getElementById('resultsGrid');
        selectedModels.forEach(modelId => {
            const model = this.findModelById(modelId);
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item running';
            resultItem.id = `result-${modelId}`;
            
            resultItem.innerHTML = `
                <div class="result-model">${model ? model.name : modelId}</div>
                <div class="result-status">
                    <span class="status-icon running"></span>
                    <span class="status-text">Running...</span>
                </div>
                <div class="result-start-time">${new Date().toLocaleTimeString()}</div>
                <div class="result-end-time">-</div>
                <div class="result-duration">-</div>
                <div class="result-cost-tokens">-</div>
                <div class="result-actions">
                    <button class="btn btn-secondary view-html-btn" disabled>View HTML</button>
                </div>
            `;
            
            resultsGrid.appendChild(resultItem);
        });
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
    }

    updateModelResult(modelId, status, result) {
        const resultItem = document.getElementById(`result-${modelId}`);
        if (!resultItem) return;
        
        resultItem.className = `result-item ${status}`;
        
        const statusIcon = resultItem.querySelector('.status-icon');
        const statusText = resultItem.querySelector('.status-text');
        const startTimeEl = resultItem.querySelector('.result-start-time');
        const endTimeEl = resultItem.querySelector('.result-end-time');
        const durationEl = resultItem.querySelector('.result-duration');
        const costTokensEl = resultItem.querySelector('.result-cost-tokens');
        const viewBtn = resultItem.querySelector('.view-html-btn');
        
        statusIcon.className = `status-icon ${status}`;
        
        switch (status) {
            case 'success':
                statusText.textContent = 'Completed';
                endTimeEl.textContent = new Date().toLocaleTimeString();
                durationEl.textContent = `${result.duration_seconds}s`;
                costTokensEl.textContent = `$${result.cost_usd.toFixed(2)} (${result.total_tokens || 0})`;
                viewBtn.disabled = false;
                viewBtn.onclick = () => this.viewHtml(modelId, result);
                break;
                
            case 'error':
                statusText.textContent = 'Failed';
                endTimeEl.textContent = new Date().toLocaleTimeString();
                durationEl.textContent = result.duration_seconds ? `${result.duration_seconds}s` : '-';
                costTokensEl.textContent = '-';
                viewBtn.disabled = true;
                break;
                
            case 'timeout':
                statusText.textContent = 'Timeout';
                endTimeEl.textContent = new Date().toLocaleTimeString();
                durationEl.textContent = `${result.duration_seconds}s`;
                costTokensEl.textContent = '-';
                viewBtn.disabled = true;
                break;
                
            default:
                statusText.textContent = 'Running...';
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

    viewHtml(modelId, result) {
        // Create blob URL for the HTML content
        const blob = new Blob([result.html_content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        
        // Open in new tab
        const newWindow = window.open(url, '_blank');
        
        // Clean up blob URL after a short delay to ensure it loads
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 1000);
        
        // Store current result for other actions
        this.currentViewResult = result;
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
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BenchmarkApp();
});
