import os
import json
import requests
import feedparser
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SEEN_FILE = "seen_links.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def get_awwwards_rss():
    items = []
    try:
        feed = feedparser.parse("https://www.awwwards.com/website-rss/")
        for entry in feed.entries[:3]:
            items.append({
                "title": entry.title,
                "link": entry.link,
                "source": "Awwwards",
                "niche": "General"
            })
    except: pass
    return items

def get_siteinspire_rss():
    items = []
    try:
        feed = feedparser.parse("https://www.siteinspire.com/rss/")
        for entry in feed.entries[:3]:
            items.append({
                "title": entry.title,
                "link": entry.link,
                "source": "Siteinspire",
                "niche": "Portfolio"
            })
    except: pass
    return items

def main():
    seen = load_seen()
    digest = []
    niches_used = set()
    
    all_sources = get_awwwards_rss() + get_siteinspire_rss()
    
    for item in all_sources:
        if item['link'] not in seen and len(digest) < 5:
            seen.add(item['link'])
            digest.append(item)
            
    if digest:
        date_str = datetime.now().strftime("%d.%m.%Y")
        message = f"<b>🎨 Design Digest | {date_str}</b>\n\n"
        for item in digest:
            message += f"<b>{item['title']}</b>\n<i>({item['source']})</i>\n<a href='{item['link']}'>Посмотреть сайт</a>\n\n"
        
        send_message(message)
        save_seen(seen)
        print(f"Sent {len(digest)} designs.")
    else:
        print("No new unique designs found today.")

if __name__ == "__main__":
    main()
