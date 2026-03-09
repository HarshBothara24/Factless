# Chrome Extension Installation Fix

## Issue: "Could not load css 'content.css'"

This error occurs because Chrome cached the old manifest before content.css was created.

## Solution: Complete Reload

### Method 1: Remove and Reinstall (Recommended)

1. **Remove Extension**
   - Go to `chrome://extensions/`
   - Find "FACTLESS - AI Reliability Checker"
   - Click "Remove"
   - Confirm removal

2. **Close and Reopen Chrome**
   - Completely close Chrome (all windows)
   - Reopen Chrome

3. **Reinstall Extension**
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Navigate to `D:\Coding\AI_ML\Project\Factless\extensions\chrome`
   - Click "Select Folder"

4. **Verify Installation**
   - Extension should load without errors
   - No "Could not load css" error
   - Extension icon appears in toolbar

### Method 2: Hard Refresh (Alternative)

1. Go to `chrome://extensions/`
2. Find FACTLESS extension
3. Click the refresh icon (circular arrow)
4. If error persists, use Method 1

### Method 3: Clear Extension Cache

1. Close Chrome completely
2. Delete Chrome extension cache:
   - Windows: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions`
   - Find the FACTLESS extension folder
   - Delete it
3. Reopen Chrome
4. Reinstall extension

## Verification

After reinstalling, check:

- [ ] No errors in `chrome://extensions/`
- [ ] Extension shows "Enabled"
- [ ] Clicking extension icon opens popup
- [ ] Popup shows "Connected to FACTLESS API" (if backend running)

## Using the Extension

### On ChatGPT (or other AI platforms):

1. **Automatic Analysis**
   - Visit https://chat.openai.com
   - Ask ChatGPT a question
   - Wait for response
   - FACTLESS badge should appear below response automatically

2. **Manual Analysis**
   - Select any text on the page
   - Right-click → "Analyze with FACTLESS"
   - Or click extension icon → "Analyze Selected Text"

### From Extension Popup:

The popup shows:
- **Connection Status**: Green = connected, Red = disconnected
- **Analyze Selected Text**: Click after selecting text on page
- **Settings**: Configure API URL and options
- **Recent Analysis**: History of recent analyses

**Note**: The "Analyze Selected Text" button only works when:
- You have text selected on the current page
- The page is a web page (not chrome:// pages)
- The extension has permission for that site

## Troubleshooting

### "No analysis history yet"

This is normal! It means:
- No analyses have been performed yet
- History will appear after you analyze some text

### "Cannot connect to API server"

Solution:
1. Start the backend:
   ```bash
   cd D:\Coding\AI_ML\Project\Factless
   python run_dev.py
   ```
2. Verify it's running: http://localhost:8000
3. Click "Settings" in popup
4. Click "Test Connection"

### Badge not appearing on ChatGPT

1. Refresh the ChatGPT page
2. Check extension is enabled
3. Check "Auto-Analysis" is enabled in settings
4. Check browser console (F12) for errors

## Files Checklist

Verify these files exist in `extensions/chrome/`:

- [ ] manifest.json
- [ ] content.js
- [ ] content.css ← **This file must exist!**
- [ ] background.js
- [ ] popup.html
- [ ] popup.js
- [ ] options.html
- [ ] options.js

If content.css is missing, the extension won't load.

## Success!

Once installed correctly:
- ✅ No errors in chrome://extensions/
- ✅ Extension icon visible
- ✅ Popup opens
- ✅ Can analyze text
- ✅ Badges appear on AI responses

## Need Help?

See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for more solutions.