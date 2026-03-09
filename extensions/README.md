# FACTLESS Extensions

This directory contains IDE and browser extensions for FACTLESS.

## Available Extensions

### 1. VS Code Extension (`vscode/`)

Real-time hallucination detection integrated into Visual Studio Code.

**Status**: ✅ Ready for development testing

**Quick Start**:
```bash
cd vscode
npm install
npm run compile
# Press F5 in VS Code to launch
```

**Features**:
- Analyze selected text with Ctrl+Shift+F
- Inline diagnostics
- Clipboard analysis
- Auto-analysis toggle
- Detailed results panel

**Documentation**: See [vscode/README.md](vscode/README.md)

### 2. Chrome Extension (`chrome/`)

Automatic analysis of AI responses in your browser.

**Status**: ✅ Ready for development testing

**Quick Start**:
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome/` directory

**Supported Platforms**:
- ChatGPT (chat.openai.com)
- Claude (claude.ai)
- Google Gemini (gemini.google.com)
- Perplexity AI (perplexity.ai)

**Features**:
- Auto-detection of AI responses
- Inline risk badges
- Context menu integration
- Analysis history
- Configurable settings

**Documentation**: See [chrome/README.md](chrome/README.md)

## Prerequisites

### For VS Code Extension
- Node.js 18+
- VS Code 1.80.0+
- FACTLESS API server running

### For Chrome Extension
- Chrome or Edge browser
- FACTLESS API server running

## Common Setup

Both extensions require the FACTLESS API server to be running:

```bash
# From project root
cd ../..
python run_dev.py
```

The API server should be accessible at `http://localhost:8000`.

## Configuration

Both extensions can be configured to use a custom API URL:

**VS Code**: Settings → Search "FACTLESS" → Set API URL

**Chrome**: Extension icon → Settings → Set API URL

## Development

### VS Code Extension

```bash
cd vscode
npm install
npm run compile
npm run watch  # For continuous compilation
```

### Chrome Extension

No build step required. Just reload the extension after making changes:
1. Go to `chrome://extensions/`
2. Click refresh icon on FACTLESS extension

## Testing

### Test VS Code Extension

1. Launch extension (F5)
2. Open any file
3. Select text
4. Press Ctrl+Shift+F
5. Verify results appear

### Test Chrome Extension

1. Load extension in Chrome
2. Visit ChatGPT
3. Ask a question
4. Verify badge appears on response
5. Click badge for details

## Troubleshooting

### "Cannot connect to API server"

**Solution**: Ensure FACTLESS API is running
```bash
cd ../..
python run_dev.py
```

### VS Code: "Extension not activating"

**Solution**: Recompile and reload
```bash
npm run compile
# Then press F5 again
```

### Chrome: "Extension not loading"

**Solution**: Check for errors
1. Go to `chrome://extensions/`
2. Click "Errors" button on FACTLESS
3. Fix any reported issues

## Notes

- **Icons**: Extensions currently work without custom icons (using browser defaults)
- **Development Mode**: Both extensions are in development mode
- **Production**: For production deployment, see respective README files

## Support

- Main documentation: [../../README.md](../../README.md)
- Setup guide: [../../SETUP_GUIDE.md](../../SETUP_GUIDE.md)
- Report issues: GitHub Issues