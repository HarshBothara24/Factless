// FACTLESS Frontend Application
class FactlessApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.analysisHistory = this.loadHistoryFromStorage();
        this.initializeElements();
        this.attachEventListeners();
        this.checkSystemStatus();
        this.displayHistory();
        
        // Example texts
        this.examples = {
            low: "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It's commonly used in applications like recommendation systems and image recognition. The field has grown significantly in recent years, with many companies adopting these technologies.",
            medium: "Python is definitely one of the most popular programming languages in the world. It's used by millions of developers for web development, data science, and automation. The language is known for its simplicity and readability, making it a great choice for beginners.",
            high: "Python is absolutely the fastest programming language ever created, with guaranteed 100% perfect execution in all scenarios. It was invented in 1995 by Dr. John Smith at MIT University. However, Python is also the slowest language for computational tasks. According to the Journal of Computer Excellence (2023), Python processes data at exactly 15.847392 teraflops per second."
        };
    }

    initializeElements() {
        // Input elements
        this.inputText = document.getElementById('inputText');
        this.charCount = document.getElementById('charCount');
        this.includeDetails = document.getElementById('includeDetails');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.exampleBtn = document.getElementById('exampleBtn');
        this.clearText = document.getElementById('clearText');

        // Status elements
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.refreshStatus = document.getElementById('refreshStatus');

        // Results elements
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.resultsContent = document.getElementById('resultsContent');
        this.riskScoreCard = document.getElementById('riskScoreCard');
        this.riskScore = document.getElementById('riskScore');
        this.riskBar = document.getElementById('riskBar');
        this.riskBadge = document.getElementById('riskBadge');
        this.processingTime = document.getElementById('processingTime');
        this.explanationsList = document.getElementById('explanationsList');
        this.noExplanations = document.getElementById('noExplanations');
        this.moduleDetails = document.getElementById('moduleDetails');
        this.moduleDetailsContent = document.getElementById('moduleDetailsContent');

        // Example cards
        this.exampleCards = document.querySelectorAll('.example-card');
        
        // History elements
        this.historyList = document.getElementById('historyList');
        this.clearHistory = document.getElementById('clearHistory');
    }

    attachEventListeners() {
        console.log('Attaching event listeners...');
        
        // Input text events
        this.inputText.addEventListener('input', () => this.updateCharCount());
        this.inputText.addEventListener('input', () => this.toggleAnalyzeButton());

        // Button events
        this.analyzeBtn.addEventListener('click', () => {
            console.log('Analyze button clicked');
            this.analyzeText();
        });
        this.exampleBtn.addEventListener('click', () => this.loadRandomExample());
        this.clearText.addEventListener('click', () => this.clearInput());
        this.refreshStatus.addEventListener('click', () => this.checkSystemStatus());

        // Example card events
        this.exampleCards.forEach(card => {
            card.addEventListener('click', () => {
                const risk = card.dataset.risk;
                this.loadExample(risk);
            });
        });

        // History events
        if (this.clearHistory) {
            this.clearHistory.addEventListener('click', () => this.clearAnalysisHistory());
        }

        // Enter key to analyze
        this.inputText.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.analyzeText();
            }
        });
        
        console.log('Event listeners attached successfully');
    }

    updateCharCount() {
        const length = this.inputText.value.length;
        this.charCount.textContent = `${length} / 10,000 characters`;
        
        if (length > 10000) {
            this.charCount.classList.add('text-red-500');
        } else {
            this.charCount.classList.remove('text-red-500');
        }
    }

    toggleAnalyzeButton() {
        const hasText = this.inputText.value.trim().length > 0;
        const isValidLength = this.inputText.value.length <= 10000;
        this.analyzeBtn.disabled = !hasText || !isValidLength;
    }

    clearInput() {
        this.inputText.value = '';
        this.updateCharCount();
        this.toggleAnalyzeButton();
        this.showEmptyState();
    }

    loadExample(risk) {
        this.inputText.value = this.examples[risk];
        this.updateCharCount();
        this.toggleAnalyzeButton();
        this.inputText.focus();
    }

    loadRandomExample() {
        const risks = ['low', 'medium', 'high'];
        const randomRisk = risks[Math.floor(Math.random() * risks.length)];
        this.loadExample(randomRisk);
    }

    async checkSystemStatus() {
        try {
            this.setStatus('checking', 'Checking system status...');
            
            const response = await fetch(`${this.apiBaseUrl}/status`);
            
            if (response.ok) {
                const data = await response.json();
                this.setStatus('healthy', `System healthy • Version ${data.version}`);
            } else {
                this.setStatus('error', 'System error - API not responding');
            }
        } catch (error) {
            this.setStatus('error', 'Cannot connect to API server');
            console.error('Status check failed:', error);
        }
    }

    setStatus(type, message) {
        this.statusText.textContent = message;
        
        // Reset classes
        this.statusIndicator.className = 'w-3 h-3 rounded-full mr-2';
        
        switch (type) {
            case 'healthy':
                this.statusIndicator.classList.add('bg-green-500');
                break;
            case 'checking':
                this.statusIndicator.classList.add('bg-yellow-500');
                break;
            case 'error':
                this.statusIndicator.classList.add('bg-red-500');
                break;
            default:
                this.statusIndicator.classList.add('bg-gray-400');
        }
    }

    async analyzeText() {
        console.log('analyzeText() called');
        const text = this.inputText.value.trim();
        
        console.log('Text length:', text.length);
        
        if (!text) {
            alert('Please enter some text to analyze.');
            return;
        }

        if (text.length > 10000) {
            alert('Text is too long. Please limit to 10,000 characters.');
            return;
        }

        this.showLoadingState();
        console.log('Sending request to API...');

        try {
            const requestData = {
                text: text,
                include_module_details: this.includeDetails.checked
            };

            console.log('Request data:', requestData);

            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const result = await response.json();
            console.log('Analysis result:', result);
            this.displayResults(result);
            
            // Add to history
            this.addToHistory(result, text);

        } catch (error) {
            console.error('Analysis failed:', error);
            this.showError(error.message);
        }
    }

    showLoadingState() {
        this.emptyState.classList.add('hidden');
        this.resultsContent.classList.add('hidden');
        this.loadingState.classList.remove('hidden');
    }

    showEmptyState() {
        this.loadingState.classList.add('hidden');
        this.resultsContent.classList.add('hidden');
        this.emptyState.classList.remove('hidden');
    }

    showError(message) {
        this.loadingState.classList.add('hidden');
        this.emptyState.classList.remove('hidden');
        this.emptyState.innerHTML = `
            <i class="fas fa-exclamation-triangle text-4xl mb-4 text-red-500"></i>
            <p class="text-red-600">Analysis Error</p>
            <p class="text-sm text-gray-500 mt-2">${message}</p>
        `;
    }

    displayResults(result) {
        this.loadingState.classList.add('hidden');
        this.emptyState.classList.add('hidden');
        this.resultsContent.classList.remove('hidden');

        // Display risk score
        this.displayRiskScore(result);

        // Display explanations
        this.displayExplanations(result.explanations);

        // Display module details if included
        if (result.module_details) {
            this.displayModuleDetails(result.module_details);
        } else {
            this.moduleDetails.classList.add('hidden');
        }

        // Display processing time
        this.processingTime.textContent = `Processed in ${result.processing_time_ms.toFixed(1)}ms`;
    }

    displayRiskScore(result) {
        const score = result.risk_score;
        const level = result.risk_level;

        // Update score display
        this.riskScore.textContent = score.toFixed(3);

        // Update progress bar
        this.riskBar.style.width = `${score * 100}%`;

        // Update styling based on risk level
        this.riskScoreCard.className = 'mb-6 p-4 rounded-lg border-2';
        this.riskBadge.textContent = level;
        this.riskBadge.className = 'px-3 py-1 rounded-full text-sm font-semibold border-2';

        switch (level) {
            case 'LOW':
                this.riskScoreCard.classList.add('risk-low');
                this.riskBadge.classList.add('risk-low');
                this.riskBar.className = 'h-2 rounded-full transition-all duration-500 bg-green-500';
                break;
            case 'MEDIUM':
                this.riskScoreCard.classList.add('risk-medium');
                this.riskBadge.classList.add('risk-medium');
                this.riskBar.className = 'h-2 rounded-full transition-all duration-500 bg-yellow-500';
                break;
            case 'HIGH':
                this.riskScoreCard.classList.add('risk-high');
                this.riskBadge.classList.add('risk-high');
                this.riskBar.className = 'h-2 rounded-full transition-all duration-500 bg-red-500';
                break;
        }
    }

    displayExplanations(explanations) {
        if (!explanations || explanations.length === 0) {
            this.explanationsList.classList.add('hidden');
            this.noExplanations.classList.remove('hidden');
            return;
        }

        this.noExplanations.classList.add('hidden');
        this.explanationsList.classList.remove('hidden');
        this.explanationsList.innerHTML = '';

        explanations.forEach(exp => {
            const expElement = document.createElement('div');
            expElement.className = 'p-3 bg-gray-50 rounded-lg border-l-4 border-orange-400';
            
            const typeIcon = this.getSignalTypeIcon(exp.signal_type);
            const sentenceText = exp.sentence_indices.length > 0 
                ? `Sentence(s): ${exp.sentence_indices.join(', ')}` 
                : 'General';

            expElement.innerHTML = `
                <div class="flex items-start space-x-3">
                    <i class="${typeIcon} text-orange-600 mt-1"></i>
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-sm font-medium text-gray-900 capitalize">${exp.signal_type.replace('_', ' ')}</span>
                            <span class="text-xs text-gray-500">${sentenceText}</span>
                        </div>
                        <p class="text-sm text-gray-700">${exp.description}</p>
                        <div class="mt-2">
                            <div class="flex items-center space-x-2">
                                <span class="text-xs text-gray-500">Risk contribution:</span>
                                <div class="flex-1 bg-gray-200 rounded-full h-1">
                                    <div class="h-1 bg-orange-500 rounded-full" style="width: ${exp.risk_contribution * 100}%"></div>
                                </div>
                                <span class="text-xs text-gray-600">${(exp.risk_contribution * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            this.explanationsList.appendChild(expElement);
        });
    }

    displayModuleDetails(details) {
        this.moduleDetails.classList.remove('hidden');
        this.moduleDetailsContent.innerHTML = '';

        const detailItems = [
            { label: 'Sentences', value: details.sentence_count, icon: 'fas fa-paragraph' },
            { label: 'Claims', value: details.claim_count, icon: 'fas fa-list' },
            { label: 'Contradictions', value: details.contradiction_count, icon: 'fas fa-exclamation-triangle' },
            { label: 'Logical Flaws', value: details.logical_flaw_count, icon: 'fas fa-brain' },
            { label: 'Overconfidence Signals', value: details.overconfidence_signals, icon: 'fas fa-exclamation' },
            { label: 'Claim Density', value: details.claim_density.toFixed(2), icon: 'fas fa-chart-bar' },
            { label: 'Suspicious Entities', value: details.suspicious_entities, icon: 'fas fa-user-secret' }
        ];

        detailItems.forEach(item => {
            const detailElement = document.createElement('div');
            detailElement.className = 'flex items-center justify-between p-2 bg-gray-50 rounded';
            detailElement.innerHTML = `
                <div class="flex items-center space-x-2">
                    <i class="${item.icon} text-blue-600"></i>
                    <span>${item.label}</span>
                </div>
                <span class="font-semibold">${item.value}</span>
            `;
            this.moduleDetailsContent.appendChild(detailElement);
        });
    }

    getSignalTypeIcon(signalType) {
        const icons = {
            'contradiction': 'fas fa-exclamation-triangle',
            'logical_flaw': 'fas fa-brain',
            'overconfidence': 'fas fa-exclamation',
            'claim_density': 'fas fa-chart-bar',
            'entity_fabrication': 'fas fa-user-secret',
            'error': 'fas fa-times-circle'
        };
        return icons[signalType] || 'fas fa-info-circle';
    }

    // History Management
    loadHistoryFromStorage() {
        try {
            const history = localStorage.getItem('factlessHistory');
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('Failed to load history:', error);
            return [];
        }
    }

    saveHistoryToStorage() {
        try {
            localStorage.setItem('factlessHistory', JSON.stringify(this.analysisHistory));
        } catch (error) {
            console.error('Failed to save history:', error);
        }
    }

    addToHistory(result, text) {
        const historyItem = {
            timestamp: new Date().toISOString(),
            risk_score: result.risk_score,
            risk_level: result.risk_level,
            text: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
            full_result: result
        };

        this.analysisHistory.unshift(historyItem);
        
        // Keep only last 10 items
        if (this.analysisHistory.length > 10) {
            this.analysisHistory = this.analysisHistory.slice(0, 10);
        }

        this.saveHistoryToStorage();
        this.displayHistory();
    }

    displayHistory() {
        if (!this.historyList) return;

        if (this.analysisHistory.length === 0) {
            this.historyList.innerHTML = '<p class="text-xs text-gray-500 italic">No analysis history yet</p>';
            return;
        }

        this.historyList.innerHTML = this.analysisHistory.map((item, index) => {
            const date = new Date(item.timestamp);
            const timeStr = date.toLocaleTimeString();
            const dateStr = date.toLocaleDateString();
            
            const riskColor = item.risk_level === 'HIGH' ? 'red' : 
                             item.risk_level === 'MEDIUM' ? 'yellow' : 'green';

            return `
                <div class="history-item p-2 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer text-xs border border-gray-200" data-index="${index}">
                    <div class="flex justify-between items-start mb-1">
                        <span class="px-2 py-0.5 rounded text-xs font-semibold bg-${riskColor}-100 text-${riskColor}-800">
                            ${item.risk_level} (${(item.risk_score * 100).toFixed(0)}%)
                        </span>
                        <span class="text-gray-500">${timeStr}</span>
                    </div>
                    <p class="text-gray-700 truncate">${item.text}</p>
                </div>
            `;
        }).join('');

        // Add click handlers to history items
        document.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                const historyItem = this.analysisHistory[index];
                this.displayResults(historyItem.full_result);
            });
        });
    }

    clearAnalysisHistory() {
        if (confirm('Are you sure you want to clear all analysis history?')) {
            this.analysisHistory = [];
            this.saveHistoryToStorage();
            this.displayHistory();
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing FACTLESS app...');
    try {
        const app = new FactlessApp();
        console.log('FACTLESS app initialized successfully');
        
        // Make app globally accessible for debugging
        window.factlessApp = app;
    } catch (error) {
        console.error('Failed to initialize app:', error);
    }
});
