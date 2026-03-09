/**
 * FACTLESS Chrome Extension - Options Script
 */

// Load saved settings
document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.sync.get([
        'apiUrl',
        'autoAnalyze',
        'riskThreshold',
        'showInlineWarnings'
    ], (result) => {
        document.getElementById('apiUrl').value = result.apiUrl || 'http://localhost:8000';
        document.getElementById('autoAnalyze').checked = result.autoAnalyze !== false;
        document.getElementById('showInlineWarnings').checked = result.showInlineWarnings !== false;
        
        const threshold = result.riskThreshold || 'medium';
        document.getElementById(`threshold${threshold.charAt(0).toUpperCase() + threshold.slice(1)}`).checked = true;
    });
});

// Test API connection
document.getElementById('testConnection').addEventListener('click', async () => {
    const apiUrl = document.getElementById('apiUrl').value;
    const statusElement = document.getElementById('connectionStatus');
    const button = document.getElementById('testConnection');
    
    button.disabled = true;
    button.textContent = 'Testing...';
    statusElement.textContent = '';
    
    try {
        const response = await fetch(`${apiUrl}/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
            statusElement.textContent = '✓ Connected';
            statusElement.style.color = '#10b981';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        statusElement.textContent = '✗ Connection failed';
        statusElement.style.color = '#ef4444';
    } finally {
        button.disabled = false;
        button.textContent = 'Test Connection';
    }
});

// Save settings
document.getElementById('settingsForm').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const settings = {
        apiUrl: document.getElementById('apiUrl').value,
        autoAnalyze: document.getElementById('autoAnalyze').checked,
        riskThreshold: document.querySelector('input[name="riskThreshold"]:checked').value,
        showInlineWarnings: document.getElementById('showInlineWarnings').checked
    };
    
    chrome.storage.sync.set(settings, () => {
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.className = 'status-message success';
        statusMessage.textContent = '✓ Settings saved successfully';
        
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 3000);
    });
});