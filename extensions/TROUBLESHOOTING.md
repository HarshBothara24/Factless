# Extension Troubleshooting Guide

## Common Issues and Solutions

### VS Code Extension

#### Issue: "Failed to load extension"

**Solution 1: Recompile TypeScript**
```bash
cd extensions/vscode
npm install
npm run compile
```

**Solution 2: Check for syntax errors**
- Open `extensions/vscode/package.json`
- Look for any JSON syntax errors
- Ensure all brackets are properly closed

**Solution 3: Reload VS Code**
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type "Reload Window"
- Press Enter

#### Issue: "Cannot find module"

**Solution:**
```bash
cd extensions/vscode
rm -rf node_modules
npm install
npm run compile
```

#### Issue: Extension not activating

**Solution:**
1. Check the Output panel: View → Output → Select "FACTLESS"
2. Look for error messages
3. Verify backend is running: http://localhost:8000/health

### Chrome Extension

#### Issue: "Could not load icon" or "Could not load manifest"

**Cause**: Missing files referenced in manifest.json

**Solution**: The extension now works without custom icons. If you still see this error:

1. Open `chrome://extensions/`
2. Remove the FACTLESS extension
3. Click "Load unpacked" again
4. Select the `extensions/chrome` folder

#### Issue: "Could not load css 'content.css'"

**Solution**: The content.css file should now exist. If not:

1. Verify `extensions/chrome/content.css` exists
2. If missing, create it with basic styles:
```css
/* Minimal styles */
.factless-badge {
    margin: 10px 0;
}
```

#### Issue: Extension loads but doesn't work

**Checklist:**
- [ ] Backend API is running at http://localhost:8000
- [ ] Extension is enabled in chrome://extensions/
- [ ] You're on a supported platform (ChatGPT, Claude, Gemini, Perplexity)
- [ ] Auto-analysis is enabled in extension settings

**Debug Steps:**
1. Open DevTools (F12)
2. Go to Console tab
3. Look for "FACTLESS:" messages
4. Check for any error messages

#### Issue: "Cannot connect to API server"

**Solution:**
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check extension settings:
   - Click extension icon
   - Click "Settings"
   - Verify API URL: `http://localhost:8000`
   - Click "Test Connection"

3. Check CORS:
   - Backend should have CORS enabled (it does by default)
   - Check browser console for CORS errors

### Both Extensions

#### Issue: Analysis not working

**Common Causes:**

1. **Backend not running**
   ```bash
   cd ../..
   python run_dev.py
   ```

2. **Wrong API URL**
   - VS Code: Settings → Search "FACTLESS" → Check API URL
   - Chrome: Extension icon → Settings → Check API URL

3. **Firewall blocking localhost**
   - Check Windows Firewall settings
   - Allow Python through firewall

4. **Port 8000 in use**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

#### Issue: Slow analysis

**Causes:**
- Large text (>5000 characters)
- Gemini API slow response
- Network issues

**Solutions:**
- Reduce text length
- Check internet connection
- Use fallback mode (no Gemini API key)

## Verification Steps

### VS Code Extension

1. **Check Extension is Loaded**
   - Look for "FACTLESS" in status bar (bottom right)
   - Should show shield icon

2. **Test Basic Functionality**
   - Open any file
   - Select some text
   - Press `Ctrl+Shift+F`
   - Should see analysis results

3. **Check Logs**
   - View → Output → Select "FACTLESS"
   - Should see initialization messages

### Chrome Extension

1. **Check Extension is Loaded**
   - Go to `chrome://extensions/`
   - Find "FACTLESS - AI Reliability Checker"
   - Should show "Enabled"

2. **Test Basic Functionality**
   - Visit https://chat.openai.com
   - Ask ChatGPT a question
   - Wait for response
   - Should see FACTLESS badge appear

3. **Check Console**
   - Press F12
   - Go to Console tab
   - Should see "FACTLESS: Content script loaded"

## Getting Help

If issues persist:

1. **Check Documentation**
   - [VS Code README](vscode/README.md)
   - [Chrome README](chrome/README.md)
   - [Main Setup Guide](../SETUP_GUIDE.md)

2. **Verify Backend**
   - Open http://localhost:8000
   - Should see FACTLESS frontend
   - Try analyzing text there first

3. **Check System Requirements**
   - Python 3.11+
   - Node.js 18+ (for VS Code)
   - Chrome/Edge (for browser extension)
   - 2GB RAM minimum

4. **Report Issue**
   - Include error messages
   - Include browser/VS Code version
   - Include steps to reproduce

## Quick Fixes

### Reset VS Code Extension

```bash
cd extensions/vscode
rm -rf node_modules out
npm install
npm run compile
# Press F5 in VS Code
```

### Reset Chrome Extension

1. Go to `chrome://extensions/`
2. Remove FACTLESS extension
3. Close and reopen Chrome
4. Load extension again

### Reset Backend

```bash
cd ../..
# Kill any running processes on port 8000
python run_dev.py
```

## Success Indicators

### VS Code
- ✅ Status bar shows "FACTLESS"
- ✅ Commands appear in Command Palette
- ✅ Keyboard shortcut works
- ✅ Analysis results display

### Chrome
- ✅ Extension icon visible in toolbar
- ✅ Popup opens when clicked
- ✅ Status shows "Connected"
- ✅ Badges appear on AI responses

### Backend
- ✅ Server starts without errors
- ✅ Frontend loads at http://localhost:8000
- ✅ API docs at http://localhost:8000/docs
- ✅ Health check returns 200

## Still Having Issues?

1. Start fresh with backend only:
   ```bash
   python run_dev.py
   ```
   Test at http://localhost:8000

2. Once backend works, try extensions one at a time

3. Check all files are present:
   - `extensions/vscode/package.json`
   - `extensions/vscode/src/extension.ts`
   - `extensions/chrome/manifest.json`
   - `extensions/chrome/content.js`
   - `extensions/chrome/content.css`

4. Verify no syntax errors in JSON files