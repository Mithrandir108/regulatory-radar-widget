[README (3).md](https://github.com/user-attachments/files/24644397/README.3.md)
# Regulatory Radar Widget

Automated enforcement intelligence for European financial services regulators.

## Overview

This widget automatically fetches, filters, and displays enforcement actions from:
- **ESMA** (European Securities and Markets Authority)
- **ECB** (European Central Bank - Banking Supervision)
- **EBA** (European Banking Authority)
- **AMF** (Autorité des Marchés Financiers - France)

Powered by Claude AI for intelligent filtering and summarization.

## Features

- ✅ Automated updates every 4 hours via GitHub Actions
- ✅ AI-powered filtering (enforcement actions only)
- ✅ Clean, responsive HTML widget
- ✅ Hosted on GitHub Pages (free)

## Live Widget

```
https://mithrandir108.github.io/regulatory-radar-widget/enforcement-widget.html
```

## Setup

### 1. Add Anthropic API Key

Settings → Secrets and variables → Actions → New repository secret:
- **Name:** `ANTHROPIC_API_KEY`
- **Value:** Your Anthropic API key (get it at https://console.anthropic.com)

### 2. Enable GitHub Pages

Settings → Pages:
- **Source:** Deploy from branch `main`
- **Folder:** `/ (root)`

### 3. Run Workflow

Actions → "Update Enforcement Watch" → Run workflow

The widget will update automatically every 4 hours.

## Manual Execution

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
python enforcement_watch.py
```

## Embed in Website

```html
<iframe 
  src="https://mithrandir108.github.io/regulatory-radar-widget/enforcement-widget.html"
  width="100%"
  height="800"
  frameborder="0"
  scrolling="no"
  style="border: none;"
></iframe>
```

## File Structure

```
regulatory-radar-widget/
├── .github/
│   └── workflows/
│       └── enforcement-watch.yml  # GitHub Actions workflow
├── enforcement_watch.py           # Main Python script
├── requirements.txt               # Dependencies
├── enforcement-widget.html        # Generated HTML (auto-updated)
└── README.md
```

## Technical Details

- **Language:** Python 3.11+
- **AI Model:** Claude Sonnet 4
- **RSS Parser:** feedparser 6.0+
- **Update Frequency:** Every 4 hours (0 */4 * * *)
- **Cache:** None (always fresh data)

## License

MIT License - Feel free to use and adapt.

## Author

**Florian Nègre**  
Fractional Chief Growth Officer | B2B SaaS & FinTech  
https://negreflorian.com
