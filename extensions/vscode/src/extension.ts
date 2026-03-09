/**
 * FACTLESS VS Code Extension
 * Real-time hallucination detection for AI-generated content
 */

import * as vscode from 'vscode';
import axios from 'axios';

interface AnalysisResult {
    risk_score: number;
    risk_level: string;
    explanations: Array<{
        signal_type: string;
        sentence_indices: number[];
        description: string;
        risk_contribution: number;
    }>;
    processing_time_ms: number;
    input_length: number;
}

interface FactlessConfig {
    apiUrl: string;
    autoAnalyze: boolean;
    riskThreshold: string;
    showInlineWarnings: boolean;
    monitorCopilot: boolean;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('FACTLESS extension is now active');

    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = "$(shield) FACTLESS";
    statusBarItem.tooltip = "FACTLESS AI Reliability Checker";
    statusBarItem.command = 'factless.showSettings';
    statusBarItem.show();

    // Analysis history
    const analysisHistory: AnalysisResult[] = [];

    // Diagnostic collection for inline warnings
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('factless');

    // Get configuration
    function getConfig(): FactlessConfig {
        const config = vscode.workspace.getConfiguration('factless');
        return {
            apiUrl: config.get('apiUrl', 'http://localhost:8000'),
            autoAnalyze: config.get('autoAnalyze', false),
            riskThreshold: config.get('riskThreshold', 'medium'),
            showInlineWarnings: config.get('showInlineWarnings', true),
            monitorCopilot: config.get('monitorCopilot', true)
        };
    }

    // Analyze text with FACTLESS API
    async function analyzeText(text: string): Promise<AnalysisResult | null> {
        const config = getConfig();

        try {
            const response = await axios.post(`${config.apiUrl}/analyze`, {
                text: text,
                include_module_details: true
            }, {
                timeout: 30000
            });

            return response.data;
        } catch (error: any) {
            if (error.code === 'ECONNREFUSED') {
                vscode.window.showErrorMessage(
                    'FACTLESS: Cannot connect to API server. Make sure it is running at ' + config.apiUrl
                );
            } else {
                vscode.window.showErrorMessage(
                    'FACTLESS: Analysis failed - ' + (error.message || 'Unknown error')
                );
            }
            return null;
        }
    }

    // Show analysis results in webview
    function showAnalysisResults(result: AnalysisResult, text: string) {
        const panel = vscode.window.createWebviewPanel(
            'factlessResults',
            'FACTLESS Analysis Results',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true
            }
        );

        panel.webview.html = getWebviewContent(result, text);
    }

    // Generate webview HTML
    function getWebviewContent(result: AnalysisResult, text: string): string {
        const riskColor = result.risk_level === 'HIGH' ? '#ef4444' : 
                         result.risk_level === 'MEDIUM' ? '#f59e0b' : '#10b981';

        return `<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                .header {
                    border-bottom: 2px solid ${riskColor};
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }
                .risk-score {
                    font-size: 48px;
                    font-weight: bold;
                    color: ${riskColor};
                }
                .risk-badge {
                    display: inline-block;
                    padding: 5px 15px;
                    background-color: ${riskColor};
                    color: white;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-left: 10px;
                }
                .progress-bar {
                    width: 100%;
                    height: 10px;
                    background-color: var(--vscode-input-background);
                    border-radius: 5px;
                    overflow: hidden;
                    margin: 10px 0;
                }
                .progress-fill {
                    height: 100%;
                    background-color: ${riskColor};
                    width: ${result.risk_score * 100}%;
                    transition: width 0.5s;
                }
                .explanation {
                    background-color: var(--vscode-input-background);
                    border-left: 4px solid ${riskColor};
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }
                .explanation-type {
                    font-weight: bold;
                    text-transform: capitalize;
                    margin-bottom: 5px;
                }
                .analyzed-text {
                    background-color: var(--vscode-textCodeBlock-background);
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                }
                .meta-info {
                    color: var(--vscode-descriptionForeground);
                    font-size: 12px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛡️ FACTLESS Analysis Results</h1>
                <div>
                    <span class="risk-score">${result.risk_score.toFixed(3)}</span>
                    <span class="risk-badge">${result.risk_level} RISK</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>

            <h2>Risk Signals Detected</h2>
            ${result.explanations.length > 0 ? 
                result.explanations.map(exp => `
                    <div class="explanation">
                        <div class="explanation-type">${exp.signal_type.replace('_', ' ')}</div>
                        <div>${exp.description}</div>
                        <div style="margin-top: 10px; font-size: 12px; color: var(--vscode-descriptionForeground);">
                            Risk Contribution: ${(exp.risk_contribution * 100).toFixed(1)}%
                        </div>
                    </div>
                `).join('') : 
                '<p style="color: var(--vscode-descriptionForeground);">No significant risk signals detected.</p>'
            }

            <h2>Analyzed Text</h2>
            <div class="analyzed-text">${text.substring(0, 500)}${text.length > 500 ? '...' : ''}</div>

            <div class="meta-info">
                Processing Time: ${result.processing_time_ms.toFixed(1)}ms | 
                Text Length: ${result.input_length} characters
            </div>
        </body>
        </html>`;
    }

    // Add inline diagnostics
    function addInlineDiagnostics(editor: vscode.TextEditor, result: AnalysisResult) {
        const config = getConfig();
        if (!config.showInlineWarnings) return;

        const diagnostics: vscode.Diagnostic[] = [];

        result.explanations.forEach(exp => {
            const severity = result.risk_level === 'HIGH' ? vscode.DiagnosticSeverity.Error :
                           result.risk_level === 'MEDIUM' ? vscode.DiagnosticSeverity.Warning :
                           vscode.DiagnosticSeverity.Information;

            // Create diagnostic for the entire document (simplified)
            const range = new vscode.Range(0, 0, editor.document.lineCount - 1, 0);
            const diagnostic = new vscode.Diagnostic(
                range,
                `FACTLESS: ${exp.description}`,
                severity
            );
            diagnostic.source = 'FACTLESS';
            diagnostics.push(diagnostic);
        });

        diagnosticCollection.set(editor.document.uri, diagnostics);
    }

    // Command: Analyze Selection
    const analyzeSelectionCommand = vscode.commands.registerCommand(
        'factless.analyzeSelection',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const selection = editor.selection;
            const text = editor.document.getText(selection);

            if (!text || text.trim().length === 0) {
                vscode.window.showWarningMessage('Please select some text to analyze');
                return;
            }

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "FACTLESS: Analyzing text...",
                cancellable: false
            }, async () => {
                const result = await analyzeText(text);
                if (result) {
                    analysisHistory.push(result);
                    showAnalysisResults(result, text);
                    addInlineDiagnostics(editor, result);

                    // Update status bar
                    statusBarItem.text = `$(shield) FACTLESS: ${result.risk_level} (${(result.risk_score * 100).toFixed(0)}%)`;
                    statusBarItem.backgroundColor = result.risk_level === 'HIGH' ? 
                        new vscode.ThemeColor('statusBarItem.errorBackground') : undefined;
                }
            });
        }
    );

    // Command: Analyze Clipboard
    const analyzeClipboardCommand = vscode.commands.registerCommand(
        'factless.analyzeClipboard',
        async () => {
            const text = await vscode.env.clipboard.readText();

            if (!text || text.trim().length === 0) {
                vscode.window.showWarningMessage('Clipboard is empty');
                return;
            }

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "FACTLESS: Analyzing clipboard content...",
                cancellable: false
            }, async () => {
                const result = await analyzeText(text);
                if (result) {
                    analysisHistory.push(result);
                    showAnalysisResults(result, text);
                }
            });
        }
    );

    // Command: Toggle Auto-Analysis
    let autoAnalyzeEnabled = false;
    const toggleAutoAnalysisCommand = vscode.commands.registerCommand(
        'factless.toggleAutoAnalysis',
        () => {
            autoAnalyzeEnabled = !autoAnalyzeEnabled;
            const config = vscode.workspace.getConfiguration('factless');
            config.update('autoAnalyze', autoAnalyzeEnabled, vscode.ConfigurationTarget.Global);
            
            vscode.window.showInformationMessage(
                `FACTLESS Auto-Analysis ${autoAnalyzeEnabled ? 'Enabled' : 'Disabled'}`
            );
        }
    );

    // Command: Show Settings
    const showSettingsCommand = vscode.commands.registerCommand(
        'factless.showSettings',
        () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'factless');
        }
    );

    // Monitor text changes for auto-analysis
    vscode.workspace.onDidChangeTextDocument(async (event: { document: any; }) => {
        const config = getConfig();
        if (!config.autoAnalyze) return;

        const editor = vscode.window.activeTextEditor;
        if (!editor || event.document !== editor.document) return;

        // Debounce: only analyze after 2 seconds of no changes
        // (Implementation would need a proper debounce mechanism)
    });

    // Register all commands
    context.subscriptions.push(
        analyzeSelectionCommand,
        analyzeClipboardCommand,
        toggleAutoAnalysisCommand,
        showSettingsCommand,
        statusBarItem,
        diagnosticCollection
    );

    // Check API connection on startup
    checkApiConnection();

    async function checkApiConnection() {
        const config = getConfig();
        try {
            await axios.get(`${config.apiUrl}/health`, { timeout: 5000 });
            vscode.window.showInformationMessage('FACTLESS: Connected to API server');
        } catch (error) {
            vscode.window.showWarningMessage(
                'FACTLESS: Cannot connect to API server. Please start the server or update the API URL in settings.'
            );
        }
    }
}

export function deactivate() {
    console.log('FACTLESS extension deactivated');
}