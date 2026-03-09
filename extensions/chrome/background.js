/**
 * FACTLESS Chrome Extension - Background Service Worker
 */

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'factless-analyze',
        title: 'Analyze with FACTLESS',
        contexts: ['selection']
    });

    console.log('FACTLESS: Extension installed');
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'factless-analyze' && info.selectionText) {
        chrome.tabs.sendMessage(tab.id, {
            type: 'ANALYZE_SELECTION'
        });
    }
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'UPDATE_CONTEXT_MENU') {
        // Context menu is already created, no need to update
    }
    return true;
});

// Badge management
function updateBadge(riskLevel) {
    const colors = {
        'LOW': '#10b981',
        'MEDIUM': '#f59e0b',
        'HIGH': '#ef4444'
    };

    chrome.action.setBadgeText({ text: riskLevel.substring(0, 1) });
    chrome.action.setBadgeBackgroundColor({ color: colors[riskLevel] || '#6b7280' });
}

// Listen for analysis results to update badge
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'ANALYSIS_COMPLETE') {
        updateBadge(request.result.risk_level);
        
        // Clear badge after 10 seconds
        setTimeout(() => {
            chrome.action.setBadgeText({ text: '' });
        }, 10000);
    }
});

console.log('FACTLESS: Background service worker ready');