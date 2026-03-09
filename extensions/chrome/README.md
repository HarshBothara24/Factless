# FACTLESS Chrome Extension

Real-time hallucination detection for AI-generated content in your browser.

## Supported Platforms

- ✅ ChatGPT (chat.openai.com)
- ✅ Claude (claude.ai)
- ✅ Google Gemini (gemini.google.com)
- ✅ Perplexity AI (perplexity.ai)

## Features

- **Automatic Detection**: Monitors AI responses in real-time
- **Inline Risk Badges**: Shows risk scores directly on AI responses
- **Detailed Analysis**: Click badges for comprehensive risk breakdown
- **Context Menu**: Right-click any text to analyze
- **Analysis History**: Track recent analyses in the popup
- **Configurable**: Customize API URL, thresholds, and display options

## Installation

### Method 1: Load Unpacked (Development)

1. **Start FACTLESS API Server**
   ```bash
   cd ../../
   python run_dev.py
   ```

2. **Open Chrome Extensions**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (top right)

3. **Load Extension**
   - Click "Load unpacked"
   - Select the `extensions/chrome` directory
   - Extension should appear in the list

Note: The extension currently uses Chrome's default icon. Custom icons can be added later.

4. **Configure Extension**
   - Click the FACTLESS extension in the list
   - Click "Details"
   - Verify it's enabled
   - Click extension icon in toolbar (puzzle piece)
   - Click "Settings"
   - Verify API URL (default: http://localhost:8000)
   - Click "Test Connection" to verify

## Usage

### Automatic Analysis

1. Visit any supported AI platform (ChatGPT, Claude, etc.)
2. Ask a question to the AI
3. FACTLESS automatically analyzes the response
4. Risk badge appears below the AI response
5. Click badge for detailed analysis

### Manual Analysis

**Option 1: Context Menu**
1. Select any text on the page
2. Right-click → "Analyze with FACTLESS"
3. Results appear in a modal

**Option 2: Extension Popup**
1. Select text on the page
2. Click FACTLESS icon in toolbar
3. Click "Analyze Selected Text"

### View History

1. Click FACTLESS icon in toolbar
2. See recent analyses in the popup
3. Each entry shows risk level and timestamp

## Configuration

### Settings Page

Access via:
- Extension popup → "Settings" button
- Right-click extension icon → "Options"
- `chrome://extensions/` → FACTLESS → "Extension options"

### Available Settings

| Setting | Description | Default |
|---------|-------------|---------|
| API Server URL | FACTLESS API endpoint | `http://localhost:8000` |
| Auto-Analysis | Automatically analyze AI responses | Enabled |
| Risk Threshold | Minimum risk level for warnings | Medium |
| Inline Warnings | Show badges on AI responses | Enabled |

## How It Works

```
AI Platform Generates Response
         ↓
Content Script Detects New Content
         ↓
Text Sent to FACTLESS API
         ↓
Analysis Performed (7-step pipeline)
         ↓
Risk Score Calculated
         ↓
Badge Displayed on Page
         ↓
User Clicks for Details
```

## Troubleshooting

### Extension Not Working

1. **Check API Connection**
   - Open extension popup
   - Status should show "Connected to FACTLESS API"
   - If not, verify API server is running

2. **Test API Manually**
   - Open `http://localhost:8000` in browser
   - Should see FACTLESS frontend

3. **Check Console**
   - Right-click page → "Inspect"
   - Check Console tab for errors
   - Look for "FACTLESS:" messages

### No Badges Appearing

1. **Verify Auto-Analysis is Enabled**
   - Open Settings
   - Check "Enable automatic analysis"

2. **Check Supported Platform**
   - Extension only works on supported AI platforms
   - See list at top of this README

3. **Reload Page**
   - Refresh the AI platform page
   - Extension reloads with page

### API Connection Failed

1. **Start API Server**
   ```bash
   python run_dev.py
   ```

2. **Check API URL**
   - Open Settings
   - Verify URL matches server
   - Click "Test Connection"

3. **Check CORS**
   - API must allow requests from browser
   - CORS is enabled by default in FACTLESS

## Development

### File Structure

```
chrome/
├── manifest.json       # Extension configuration
├── background.js       # Service worker
├── content.js         # Injected into AI platforms
├── popup.html         # Extension popup UI
├── popup.js           # Popup logic
├── options.html       # Settings page UI
├── options.js         # Settings logic
└── images/            # Extension icons
```

### Building

```bash
# Install dependencies (if any)
npm install

# Package extension
zip -r factless-chrome.zip . -x "*.git*" "node_modules/*"
```

### Testing

1. Make changes to source files
2. Go to `chrome://extensions/`
3. Click refresh icon on FACTLESS extension
4. Test on supported AI platforms

## Privacy & Security

- **No Data Collection**: Extension doesn't collect or store personal data
- **Local Processing**: All analysis done via your local API server
- **No External Requests**: Only communicates with your FACTLESS API
- **Open Source**: All code is visible and auditable

## Permissions Explained

| Permission | Why Needed |
|------------|------------|
| `activeTab` | Access current tab to analyze text |
| `storage` | Save settings and analysis history |
| `contextMenus` | Add "Analyze with FACTLESS" menu item |
| `host_permissions` | Inject content script into AI platforms |

## Known Issues

- Some AI platforms may update their UI, breaking selectors
- Very long responses may take longer to analyze
- Extension must be reloaded after API server restart

## Contributing

1. Fork the repository
2. Make changes in `extensions/chrome/`
3. Test thoroughly on all supported platforms
4. Submit pull request

## Support

- 📖 Documentation: See main project README
- 🐛 Issues: Report on GitHub
- 💬 Discussions: Use GitHub discussions

## License

MIT - See main project LICENSE file