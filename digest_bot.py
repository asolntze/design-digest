import os
import json
import requests
from bs4 import BeautifulSoup
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
        print(f"Status: {r.status_code}")
    except Exception as e:
        print(f"Error sending message: {e}")

def get_awwwards():
    items = []
    try:
        r = requests.get("https://www.awwwards.com/websites/", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.select('.item--profile')[:3]:
            link_tag = card.find('a', class_='js-titles')
            if link_tag:
                link = "https://www.awwwards.com" + link_tag['href']
                title = link_tag.get_text(strip=True)
                items.append({"title": title, "link": link, "source": "Awwwards", "niche": "General"})
    except: pass
    return items

def get_siteinspire():
    items = []
    try:
        r = requests.get("https://www.siteinspire.com/", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.select('.work-item')[:3]:
            link_tag = card.find('a')
            if link_tag:
                link = "https://www.siteinspire.com" + link_tag['href']
                title = card.select_one('.work-title').get_text(strip=True) if card.select_one('.work-title') else "Siteinspire Design"
                items.append({"title": title, "link": link, "source": "Siteinspire", "niche": "Portfolio"})
    except: pass
    return items

def get_httpster():
    items = []
    try:
        r = requests.get("https://httpster.net/", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.select('.project')[:2]:
            link_tag = card.find('a')
            if link_tag:
                link = link_tag['href']
                title = card.select_one('.project-name').get_text(strip=True) if card.select_one('.project-name') else "Httpster Project"
                items.append({"title": title, "link": link, "source": "Httpster", "niche": "Trendy"})
    except: pass
    return items

def main():
    seen = load_seen()
    digest = []
    niches_used = set()
    
    all_sources = get_awwwards() + get_siteinspire() + get_httpster()
    
    for item in all_sources:
        if item['link'] not in seen and item['niche'] not in niches_used and len(digest) < 5:
            seen.add(item['link'])
            niches_used.add(item['niche'])
            digest.append(item)
            
    if digest:
        date_str = datetime.now().strftime("%d.%m.%Y")
        message = f"<b>🎨 Design Digest | {date_str}</b>\n\n"
        for item in digest:
            message += f"<b>{item['title']}</b>\n<i>({item['source']})</i>\n<a href='{item['link']}'>Посмотреть сайт</a>\n\n"
        
        send_message(message)
        save_seen(seen)
        print("Digest sent successfully.")
    else:
        print("No new unique designs found today.")

if __name__ == "__main__":
    main()
