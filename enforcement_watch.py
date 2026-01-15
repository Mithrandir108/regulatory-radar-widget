#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enforcement Watch - Automated Regulatory Intelligence
Generates real-time feed of enforcement actions from EU financial regulators
Author: Florian Negre
"""

import os
import sys
import feedparser
from datetime import datetime, timedelta
from anthropic import Anthropic
import json

CONFIG_FILE = "config.json"
OUTPUT_FILE = "enforcement-widget.html"

RSS_FEEDS = {
    "esma": "https://www.esma.europa.eu/rss.xml",
    "ecb": "https://www.bankingsupervision.europa.eu/rss/pub.html",
    "eba": "https://www.eba.europa.eu/news-press/news/rss.xml",
    "amf": "https://www.amf-france.org/en/flux-rss/display/23",
    "bafin": "https://www.bafin.de/SiteGlobals/Functions/RSSFeed/EN/RSSNewsfeed_EN",
    "fca": "https://www.fca.org.uk/news/rss.xml",
}

SOURCE_CONFIG = {
    "esma": {"badge": "source-badge-esma", "name": "ESMA"},
    "ecb": {"badge": "source-badge-ecb", "name": "ECB"},
    "eba": {"badge": "source-badge-eba", "name": "EBA"},
    "amf": {"badge": "source-badge-amf", "name": "AMF"},
    "bafin": {"badge": "source-badge-bafin", "name": "BaFin"},
    "fca": {"badge": "source-badge-fca", "name": "FCA"},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Enforcement Watch</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:wght@400;700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background-color: transparent; padding: 2rem 0; }
    .widget-container { max-width: 1200px; margin: 0 auto; }
    .enforcement-grid { display: grid; gap: 1.5rem; }
    .enforcement-card { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; transition: all 0.2s ease; }
    .enforcement-card:hover { border-color: #3b82f6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1); transform: translateY(-2px); }
    .card-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; gap: 1rem; flex-wrap: wrap; }
    .source-badge { font-size: 11px; font-weight: 700; color: white; padding: 6px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; }
    .source-badge-esma { background: #3b82f6; }
    .source-badge-ecb { background: #10b981; }
    .source-badge-eba { background: #8b5cf6; }
    .source-badge-amf { background: #f59e0b; }
    .source-badge-bafin { background: #dc2626; }
    .source-badge-fca { background: #7c3aed; }
    .card-date { font-size: 14px; color: #6b7280; }
    .card-title { font-size: 18px; font-weight: 600; color: #242322; margin-bottom: 0.75rem; line-height: 1.4; }
    .card-title a { color: inherit; text-decoration: none; }
    .card-title a:hover { color: #3b82f6; }
    .card-summary { font-size: 15px; color: #242322; opacity: 0.85; line-height: 1.6; }
    .last-updated { text-align: center; font-size: 13px; color: #6b7280; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; }
    @media (max-width: 768px) {
      .enforcement-card { padding: 1.25rem; }
      .card-title { font-size: 16px; }
    }
  </style>
</head>
<body>
  <div class="widget-container">
    <div class="enforcement-grid">
{{CARDS}}
    </div>
    <div class="last-updated">Last updated: {{TIMESTAMP}}</div>
  </div>
</body>
</html>"""


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None


def save_config(api_key):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key}, f)


def setup_api_key():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        return api_key
    
    print("\n" + "="*60)
    print("  INITIAL CONFIGURATION")
    print("="*60)
    print("\nAnthropic API key not configured.")
    print("Get your key at: https://console.anthropic.com/settings/keys\n")
    
    api_key = input("Enter your Anthropic API key: ").strip()
    
    if not api_key.startswith("sk-ant-"):
        print("\n❌ ERROR: Key must start with 'sk-ant-'")
        sys.exit(1)
    
    save_config(api_key)
    print("\n✅ API key saved successfully!\n")
    return api_key


def fetch_rss_articles(days_ago=7):
    articles = []
    cutoff_time = datetime.now() - timedelta(days=days_ago)
    
    for source_key, feed_url in RSS_FEEDS.items():
        try:
            print(f"   Fetching {source_key.upper()}...")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:20]:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except:
                    pub_date = datetime.now()
                
                if pub_date > cutoff_time:
                    articles.append({
                        "source": source_key,
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.get("summary", entry.get("description", ""))[:500],
                        "published": pub_date.isoformat(),
                    })
        except Exception as e:
            print(f"   ⚠️  Error fetching {source_key}: {e}")
            continue
    
    return articles


def filter_with_claude(articles, api_key):
    client = Anthropic(api_key=api_key)
    
    prompt = f"""Analyze these regulatory news articles and select ONLY enforcement actions.

STRICT CRITERIA - Include ONLY if article mentions:
- Sanctions, fines, penalties (with amounts)
- Enforcement measures against financial institutions
- Supervisory actions with consequences
- Breach investigations with outcomes
- Non-compliance penalties

EXCLUDE:
- General guidelines, consultations, reports
- Policy announcements without enforcement
- Market data, statistics
- Conferences, events

Articles:
{json.dumps(articles, indent=2, ensure_ascii=False)}

Return 5 most relevant enforcement actions with:
- title: Original title
- summary: 2-3 sentences focusing on: WHO was penalized, WHAT violation, HOW MUCH fine
- Keep summaries under 150 words

JSON format:
{{
  "selected_articles": [
    {{
      "source": "esma",
      "title": "...",
      "link": "...",
      "published": "...",
      "summary": "..."
    }}
  ]
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text.replace("```json", "").replace("```", "").strip()
        data = json.loads(response)
        return data["selected_articles"]
    
    except Exception as e:
        print(f"\n❌ Claude API Error: {e}")
        return []


def generate_html(articles):
    cards_html = ""
    
    for article in articles:
        source_info = SOURCE_CONFIG[article["source"]]
        
        pub_date = datetime.fromisoformat(article["published"])
        days = (datetime.now() - pub_date).days
        
        if days == 0:
            time_label = "Today"
        elif days == 1:
            time_label = "Yesterday"
        elif days < 7:
            time_label = f"{days} days ago"
        else:
            time_label = pub_date.strftime("%d %b %Y")
        
        cards_html += f"""
      <div class="enforcement-card">
        <div class="card-header">
          <span class="source-badge {source_info['badge']}">{source_info['name']}</span>
          <span class="card-date">{time_label}</span>
        </div>
        <h3 class="card-title">
          <a href="{article['link']}" target="_blank" rel="noopener">
            {article['title']}
          </a>
        </h3>
        <p class="card-summary">
          {article['summary']}
        </p>
      </div>"""
    
    timestamp = datetime.now().strftime("%d %B %Y at %H:%M UTC")
    
    html = HTML_TEMPLATE.replace("{{CARDS}}", cards_html).replace("{{TIMESTAMP}}", timestamp)
    return html


def main():
    print("\n" + "="*60)
    print("  ENFORCEMENT WATCH - GENERATION")
    print("="*60 + "\n")
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        config = load_config()
        if not config:
            api_key = setup_api_key()
        else:
            api_key = config["api_key"]
            print("✓ API key loaded\n")
    else:
        print("✓ API key loaded from environment\n")
    
    print("📰 Fetching RSS feeds...")
    articles = fetch_rss_articles(days_ago=14)
    print(f"   → {len(articles)} articles found\n")
    
    if not articles:
        print("❌ No articles found.\n")
        return
    
    print("🤖 Analyzing with Claude AI...")
    filtered = filter_with_claude(articles, api_key)
    print(f"   → {len(filtered)} enforcement actions selected\n")
    
    if not filtered:
        print("⚠️  No enforcement actions found. Using fallback data.\n")
        filtered = articles[:5]
    
    print("📝 Generating HTML...")
    html = generate_html(filtered)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"   → File created: {OUTPUT_FILE}\n")
    print("="*60)
    print("✅ DONE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Stopped by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        sys.exit(1)
