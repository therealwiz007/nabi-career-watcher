import os
import requests
from bs4 import BeautifulSoup

# ==================== CONFIGURATION ====================
WAPPFLY_API_KEY = os.environ.get("WAPPFLY_API_KEY")
WAPPFLY_DEVICE_ID = os.environ.get("WAPPFLY_DEVICE_ID")

PHONE_NUMBERS = [
    os.environ.get("PHONE_ONE"),
    os.environ.get("PHONE_TWO")
]

URL_TO_WATCH = "https://nabi.res.in/site/career"
TEXT_FILE = "last_website_text.txt"
# =======================================================

def get_url_text(url):
    """Fetches the website and returns clean visible text split into lines."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return [line.strip() for line in soup.get_text().splitlines() if line.strip()]
    except Exception as e:
        print(f"Error reading {url}: {e}")
    return None

def send_whatsapp_alert(message_text, target_phone):
    if not target_phone or not WAPPFLY_API_KEY or not WAPPFLY_DEVICE_ID:
        print("Skipping alert: Missing credentials or phone number secret.")
        return
        
    # The official verified REST endpoint for sending text via Wappfly
    api_url = "https://wappfly.com/api/send/text"
    
    headers = {
        "X-API-Token": WAPPFLY_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "device_id": WAPPFLY_DEVICE_ID,
        "to": target_phone,
        "message": message_text
    }
    
    try:
        res = requests.post(api_url, json=payload, headers=headers, timeout=12)
        if res.status_code in [200, 201]:
            print(f"🎉 WhatsApp alert successfully sent to {target_phone}!")
        else:
            print(f"Wappfly Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to connect to Wappfly: {e}")

def check_website():
    stored_lines = []
    if os.path.exists(TEXT_FILE):
        with open(TEXT_FILE, "r", encoding="utf-8") as f:
            stored_lines = [line.strip() for line in f.readlines() if line.strip()]

    current_lines = get_url_text(URL_TO_WATCH)
    
    if current_lines:
        if stored_lines:
            new_additions = [line for line in current_lines if line not in stored_lines]
            if new_additions:
                print("Changes detected! Preparing text summary...")
                alert_text = "🚨 *NABI Career Page Update!* 🚨\n\n"
                alert_text += f"🔗 *Link:* {URL_TO_WATCH}\n\n"
                alert_text += "➕ *What was added/changed:*\n"
                for line in new_additions[:5]:
                    alert_text += f"• {line}\n"
                if len(new_additions) > 5:
                    alert_text += f"• _...and {len(new_additions) - 5} more lines._\n"
                
                for phone in PHONE_NUMBERS:
                    send_whatsapp_alert(alert_text, phone)
            else:
                print("No new content added since the last check.")
        else:
            print("First run: Establishing baseline tracking text file.")
        
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            for line in current_lines:
                f.write(f"{line}\n")
    else:
        print("Could not scrape page successfully.")

if __name__ == "__main__":
    check_website()
