# FACTLESS VS Code Extension

Real-time hallucination detection for AI-generated code and text in Visual Studio Code.

## Features

- **Real-time Analysis**: Analyze AI-generated content with a single command
- **Inline Warnings**: See risk indicators directly in your editor
- **GitHub Copilot Monitoring**: Automatically check Copilot suggestions
- **Clipboard Analysis**: Analyze any text from your clipboard
- **Detailed Reports**: View comprehensive analysis results in a side panel
- **Configurable Thresholds**: Set your own risk tolerance levels

## Installation

### From Source

1. Clone the repository
2. Navigate to `extensions/vscode`
3. Run `npm install`
4. Run `npm run compile`
5. Press F5 in VS Code to open a new window with the extension loaded

Note: The extension currently uses VS Code's default icon. Custom icons can be added later.

## Setup

1. **Start FACTLESS API Server**
   ```bash
   cd ../../
   python run_dev.py
   ```

2. **Configure Extension**
   - Open VS Code Settings (Ctrl+,)
   - Search for "FACTLESS"
   - Set API URL (default: http://localhost:8000)

## Usage

### Analyze Selected Text

1. Select any text in the editor
2. Press `Ctrl+Shift+F` (or `Cmd+Shift+F` on Mac)
3. View results in the side panel

### Analyze Clipboard

1. Copy AI-generated text to clipboard
2. Open Command Palette (Ctrl+Shift+P)
3. Run "FACTLESS: Analyze Clipboard Content"

### Auto-Analysis

1. Open Command Palette
2. Run "FACTLESS: Toggle Auto-Analysis"
3. The extension will automatically analyze new content

## Commands

- `FACTLESS: Analyze Selected Text` - Analyze currently selected text
- `FACTLESS: Analyze Clipboard Content` - Analyze clipboard content
- `FACTLESS: Toggle Auto-Analysis` - Enable/disable automatic analysis
- `FACTLESS: Open Settings` - Open extension settings

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `factless.apiUrl` | FACTLESS API server URL | `http://localhost:8000` |
| `factless.autoAnalyze` | Automatically analyze AI content | `false` |
| `factless.riskThreshold` | Minimum risk level for warnings | `medium` |
| `factless.showInlineWarnings` | Show inline editor warnings | `true` |
| `factless.monitorCopilot` | Monitor GitHub Copilot suggestions | `true` |

## Requirements

- VS Code 1.80.0 or higher
- FACTLESS API server running (see main project README)
- Node.js 18+ (for development)

## Known Issues

- Auto-analysis may cause performance issues with very large files
- Copilot monitoring requires GitHub Copilot extension to be installed

## Release Notes

### 1.0.0

- Initial release
- Basic text analysis functionality
- Inline warnings
- Clipboard analysis
- Configurable settings

## Contributing

See the main project repository for contribution guidelines.

## License

MIT