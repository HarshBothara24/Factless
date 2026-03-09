# Chrome Extension Quick Start

## Installation (First Time)

### Step 1: Remove Old Version (if installed)
```
chrome://extensions/ → Find FACTLESS → Click "Remove"
```

### Step 2: Close Chrome Completely
- Close ALL Chrome windows
- Wait 5 seconds
- Reopen Chrome

### Step 3: Install Fresh
1. Open `chrome://extensions/`
2. Enable "Developer mode" (toggle top-right)
3. Click "Load unpacked"
4. Select folder: `D:\Coding\AI_ML\Project\Factless\extensions\chrome`
5. Click "Select Folder"

### Step 4: Verify
- ✅ No errors shown
- ✅ Extension appears in list
- ✅ Shows "Enabled"

## How to Use

### Method 1: Automatic (Recommended)

**On ChatGPT:**
1. Go to https://chat.openai.com
2. Ask any question
3. Wait for ChatGPT's response
4. **FACTLESS badge appears automatically** below the response
5. Click badge to see detailed analysis

**Works on:**
- ChatGPT (chat.openai.com)
- Claude (claude.ai)
- Gemini (gemini.google.com)
- Perplexity (perplexity.ai)

### Method 2: Manual Analysis

**Option A: Right-Click Menu**
1. Select any text on any webpage
2. Right-click
3. Click "Analyze with FACTLESS"
4. Results appear in modal

**Option B: Extension Popup**
1. Select text on the page
2. Click FACTLESS icon in toolbar
3. Click "Analyze Selected Text"
4. Results appear

### Method 3: From Popup History

1. Click FACTLESS icon
2. View "Recent Analysis" section
3. See history of past analyses

## Understanding the Popup

```
┌─────────────────────────────────┐
│  🛡️ FACTLESS                    │
│  AI Reliability Checker          │
├─────────────────────────────────┤
│  ● Connected to FACTLESS API    │ ← Green = Good
├─────────────────────────────────┤
│  🔍 Analyze Selected Text       │ ← Click after selecting
│  (Select text on page first)    │
│                                  │
│  ⚙️ Settings                    │
├─────────────────────────────────┤
│  Recent Analysis                 │
│  • No analysis history yet      │ ← Will show history
└─────────────────────────────────┘
```

## What Each Part Does

### Status Indicator
- **Green dot** = Connected to API ✅
- **Red dot** = Cannot connect ❌

### Analyze Selected Text Button
- Only works when text is selected on the page
- Won't work on chrome:// pages
- Won't work if no text selected

### Settings
- Configure API URL
- Test connection
- Enable/disable auto-analysis
- Set risk thresholds

### Recent Analysis
- Shows last 5 analyses
- Each shows risk level and timestamp
- Click to see details

## Common Questions

### Q: Why doesn't the badge appear?

**A:** Check these:
1. Are you on a supported site? (ChatGPT, Claude, etc.)
2. Is auto-analysis enabled? (Settings → Enable automatic analysis)
3. Did you refresh the page after installing?
4. Is the backend running? (http://localhost:8000)

### Q: "Analyze Selected Text" doesn't work

**A:** Make sure:
1. You selected text on the page FIRST
2. You're not on a chrome:// page
3. The page is fully loaded
4. Backend is running

### Q: "No analysis history yet"

**A:** This is normal! History appears after you:
- Analyze some text manually, OR
- Visit ChatGPT and get an AI response (auto-analyzed)

### Q: How do I know it's working?

**A:** Test it:
1. Go to https://chat.openai.com
2. Ask: "Tell me about Python"
3. Wait for response
4. Look for FACTLESS badge below response
5. Badge should appear within 2-3 seconds

## Troubleshooting

### Extension won't load
→ See [INSTALL_FIX.md](INSTALL_FIX.md)

### "Cannot connect to API"
```bash
cd D:\Coding\AI_ML\Project\Factless
python run_dev.py
```

### Badge not appearing
1. Refresh the AI platform page
2. Check Settings → Auto-analysis is ON
3. Check browser console (F12) for errors

## Visual Guide

### Automatic Analysis Flow:
```
You ask ChatGPT a question
         ↓
ChatGPT responds
         ↓
FACTLESS detects response (automatic)
         ↓
Analyzes text in background
         ↓
Badge appears below response
         ↓
Click badge for details
```

### Manual Analysis Flow:
```
Select text on any page
         ↓
Right-click → "Analyze with FACTLESS"
         ↓
Modal appears with results
```

## Success Checklist

After installation:
- [ ] Extension loads without errors
- [ ] Popup opens when clicking icon
- [ ] Status shows "Connected" (green)
- [ ] Can open Settings page
- [ ] Badge appears on ChatGPT responses
- [ ] Can analyze selected text

## Next Steps

1. **Test on ChatGPT**: Visit chat.openai.com and ask a question
2. **Check Settings**: Configure to your preferences
3. **Try Manual Analysis**: Select text and right-click
4. **View History**: Check popup for recent analyses

## Need More Help?

- Full documentation: [README.md](README.md)
- Troubleshooting: [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- Backend setup: [../../SETUP_GUIDE.md](../../SETUP_GUIDE.md)