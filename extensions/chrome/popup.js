/**
 * FACTLESS Chrome Extension - Popup Script
 */

let config = {
    apiUrl: 'http://localhost:8000'
};

// Load configuration
chrome.storage.sync.get(['apiUrl'], (result) => {
    if (result.apiUrl) {
        config.apiUrl = result.apiUrl;
    }
    checkApiConnection();
});

// Check API connection
async function checkApiConnection() {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    try {
        const response = await fetch(`${config.apiUrl}/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });

        if (response.ok) {
            statusIndicator.classList.remove('disconnected');
            statusText.textContent = 'Connected to FACTLESS API';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        statusIndicator.classList.add('disconnected');
        statusText.textContent = 'Cannot connect to API server';
    }
}

// Analyze selected text
document.getElementById('analyzeSelection').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // First, try to get selected text directly
    try {
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => window.getSelection().toString()
        });
        
        const selectedText = results[0].result;
        
        if (selectedText && selectedText.trim().length > 0) {
            // Analyze the text directly
            analyzeTextDirectly(selectedText);
        } else {
            showNotification('Please select some text on the page first', 'error');
        }
    } catch (error) {
        console.error('Error getting selection:', error);
        showNotification('Cannot access this page. Try a regular webpage.', 'error');
    }
});

// Analyze text directly from popup
async function analyzeTextDirectly(text) {
    try {
        showNotification('Analyzing...', 'info');
        
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
        
        // Save to history
        chrome.storage.local.get(['analysisHistory'], (storage) => {
            const history = storage.analysisHistory || [];
            history.unshift({
                result: result,
                text: text.substring(0, 200),
                timestamp: Date.now()
            });
            
            const trimmedHistory = history.slice(0, 20);
            chrome.storage.local.set({ analysisHistory: trimmedHistory }, () => {
                loadHistory();
                showNotification('Analysis complete!', 'success');
            });
        });

    } catch (error) {
        console.error('Analysis error:', error);
        showNotification('Analysis failed. Check if backend is running.', 'error');
    }
}

// Open options page
document.getElementById('openOptions').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
});

// Load analysis history
function loadHistory() {
    chrome.storage.local.get(['analysisHistory'], (result) => {
        const history = result.analysisHistory || [];
        displayHistory(history);
    });
}

function displayHistory(history) {
    const historyList = document.getElementById('historyList');
    
    if (history.length === 0) {
        historyList.innerHTML = '<div class="empty-history">No analysis history yet</div>';
        return;
    }

    historyList.innerHTML = history.slice(0, 5).map(item => `
        <div class="history-item">
            <div class="history-item-header">
                <span class="risk-badge risk-${item.result.risk_level.toLowerCase()}">
                    ${item.result.risk_level}
                </span>
                <span style="font-size: 11px; color: #9ca3af;">
                    ${new Date(item.timestamp).toLocaleTimeString()}
                </span>
            </div>
            <div class="history-text">${item.text}</div>
        </div>
    `).join('');
}

// Listen for analysis completion
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'ANALYSIS_COMPLETE') {
        // Add to history
        chrome.storage.local.get(['analysisHistory'], (result) => {
            const history = result.analysisHistory || [];
            history.unshift({
                result: request.result,
                text: request.text,
                timestamp: Date.now()
            });
            
            // Keep only last 20 items
            const trimmedHistory = history.slice(0, 20);
            
            chrome.storage.local.set({ analysisHistory: trimmedHistory }, () => {
                loadHistory();
            });
        });
    }
});

function showNotification(message, type) {
    // Simple notification (could be enhanced)
    const statusText = document.getElementById('statusText');
    const originalText = statusText.textContent;
    statusText.textContent = message;
    
    setTimeout(() => {
        statusText.textContent = originalText;
    }, 2000);
}

// Load history on popup open
loadHistory();

// Refresh connection status every 30 seconds
setInterval(checkApiConnection, 30000);