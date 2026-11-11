import os
import json
import requests
import xml.etree.ElementTree as ET
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
        r = requests.post(url, data=data, timeout=10)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def parse_rss(url, source_name, niche="General", limit=3):
    items = []
    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.text)
        for item in root.findall('.//item')[:limit]:
            title = item.find('title').text if item.find('title') is not None else "Untitled"
            link = item.find('link').text if item.find('link') is not None else ""
            if link:
                items.append({"title": title, "link": link, "source": source_name, "niche": niche})
    except: pass
    return items

def main():
    seen = load_seen()
    digest = []
    
    # Проверенные RSS-источники
    sources = [
        ("https://www.cssdesignawards.com/rss/", "CSSDA", "Award"),
        ("https://bestwebsite.gallery/feed/", "BWG", "Gallery"),
        ("https://www.awwwards.com/website-rss/", "Awwwards", "SOTD")
    ]
    
    all_items = []
    for url, name, niche in sources:
        all_items.extend(parse_rss(url, name, niche, limit=2))
    
    for item in all_items:
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
