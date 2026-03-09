/**
 * FACTLESS Chrome Extension - Content Script
 * Monitors AI responses and analyzes them for hallucination risk
 */

// Configuration
let config = {
    apiUrl: 'http://localhost:8000',
    autoAnalyze: true,
    riskThreshold: 'medium',
    showInlineWarnings: true
};

// Load configuration from storage
chrome.storage.sync.get(['apiUrl', 'autoAnalyze', 'riskThreshold', 'showInlineWarnings'], (result) => {
    config = { ...config, ...result };
});

// Detect which AI platform we're on
const platform = detectPlatform();

console.log('FACTLESS: Content script loaded on', platform);

function detectPlatform() {
    const hostname = window.location.hostname;
    if (hostname.includes('openai.com')) return 'chatgpt';
    if (hostname.includes('claude.ai')) return 'claude';
    if (hostname.includes('gemini.google.com') || hostname.includes('bard.google.com')) return 'gemini';
    if (hostname.includes('perplexity.ai')) return 'perplexity';
    return 'unknown';
}

// Platform-specific selectors for AI responses
const selectors = {
    chatgpt: '.markdown.prose',
    claude: '.font-claude-message',
    gemini: '.model-response-text',
    perplexity: '.prose'
};

// Store analyzed responses to avoid re-analysis
const analyzedResponses = new Set();

// Mutation observer to detect new AI responses
const observer = new MutationObserver((mutations) => {
    if (!config.autoAnalyze) return;

    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                checkForAIResponse(node);
            }
        });
    });
});

// Start observing
observer.observe(document.body, {
    childList: true,
    subtree: true
});

function checkForAIResponse(element) {
    const selector = selectors[platform];
    if (!selector) return;

    const responseElements = element.querySelectorAll ? 
        element.querySelectorAll(selector) : 
        (element.matches && element.matches(selector) ? [element] : []);

    responseElements.forEach((responseElement) => {
        const text = responseElement.innerText || responseElement.textContent;
        
        if (text && text.length > 50 && !analyzedResponses.has(text)) {
            analyzedResponses.add(text);
            analyzeResponse(text, responseElement);
        }
    });
}

async function analyzeResponse(text, element) {
    try {
        const response = await fetch(`${config.apiUrl}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                include_module_details: false
            })
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const result = await response.json();
        displayAnalysisResult(result, element);

        // Send to popup for history
        chrome.runtime.sendMessage({
            type: 'ANALYSIS_COMPLETE',
            result: result,
            text: text.substring(0, 200)
        });

    } catch (error) {
        console.error('FACTLESS: Analysis error', error);
    }
}

function displayAnalysisResult(result, element) {
    if (!config.showInlineWarnings) return;

    // Remove existing badge if any
    const existingBadge = element.querySelector('.factless-badge');
    if (existingBadge) {
        existingBadge.remove();
    }

    // Create risk badge
    const badge = document.createElement('div');
    badge.className = 'factless-badge';
    badge.setAttribute('data-risk-level', result.risk_level.toLowerCase());
    
    const riskColor = result.risk_level === 'HIGH' ? '#ef4444' : 
                     result.risk_level === 'MEDIUM' ? '#f59e0b' : '#10b981';

    badge.innerHTML = `
        <div class="factless-badge-content" style="
            background-color: ${riskColor};
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 10px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <span>🛡️</span>
            <span>FACTLESS: ${result.risk_level} Risk - ${(result.risk_score * 100).toFixed(0)}%</span>
        </div>
    `;

    // Add click handler to show details
    badge.addEventListener('click', () => {
        showDetailedResults(result);
    });

    // Insert badge after the response
    element.parentNode.insertBefore(badge, element.nextSibling);
}

function showDetailedResults(result) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'factless-modal';
    modal.innerHTML = `
        <div class="factless-modal-overlay"></div>
        <div class="factless-modal-content">
            <div class="factless-modal-header">
                <h2>🛡️ FACTLESS Analysis Results</h2>
                <button class="factless-modal-close">&times;</button>
            </div>
            <div class="factless-modal-body">
                <div class="factless-risk-score">
                    <div class="factless-score-value">${result.risk_score.toFixed(3)}</div>
                    <div class="factless-risk-badge factless-risk-${result.risk_level.toLowerCase()}">
                        ${result.risk_level} RISK
                    </div>
                </div>
                <div class="factless-progress-bar">
                    <div class="factless-progress-fill" style="width: ${result.risk_score * 100}%"></div>
                </div>
                <h3>Risk Signals Detected</h3>
                ${result.explanations.length > 0 ? 
                    result.explanations.map(exp => `
                        <div class="factless-explanation">
                            <div class="factless-explanation-type">${exp.signal_type.replace('_', ' ')}</div>
                            <div class="factless-explanation-desc">${exp.description}</div>
                            <div class="factless-explanation-meta">
                                Risk Contribution: ${(exp.risk_contribution * 100).toFixed(1)}%
                            </div>
                        </div>
                    `).join('') : 
                    '<p class="factless-no-signals">No significant risk signals detected.</p>'
                }
                <div class="factless-meta-info">
                    Processing Time: ${result.processing_time_ms.toFixed(1)}ms | 
                    Text Length: ${result.input_length} characters
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close modal handlers
    const closeBtn = modal.querySelector('.factless-modal-close');
    const overlay = modal.querySelector('.factless-modal-overlay');
    
    const closeModal = () => modal.remove();
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);
}

// Context menu for manual analysis
document.addEventListener('contextmenu', (e) => {
    const selectedText = window.getSelection().toString();
    if (selectedText && selectedText.length > 20) {
        chrome.runtime.sendMessage({
            type: 'UPDATE_CONTEXT_MENU',
            hasSelection: true
        });
    }
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'ANALYZE_SELECTION') {
        const selectedText = window.getSelection().toString();
        if (selectedText) {
            analyzeResponse(selectedText, document.body);
            sendResponse({ success: true });
        } else {
            sendResponse({ success: false, error: 'No text selected' });
        }
    }
    return true;
});

console.log('FACTLESS: Ready to analyze AI responses');