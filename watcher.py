import os
import hashlib
import requests
from bs4 import BeautifulSoup

# ==================== CONFIGURATION ====================
# Securely pulling your private credentials from GitHub Actions environment
WAPPFLY_API_KEY = os.environ.get("WAPPFLY_API_KEY")
WAPPFLY_DEVICE_ID = os.environ.get("WAPPFLY_DEVICE_ID")

# The two hidden phone numbers to alert
PHONE_NUMBERS = [
    os.environ.get("PHONE_ONE"),
    os.environ.get("PHONE_TWO")
]

URL_TO_WATCH = "https://nabi.res.in/site/career"
HASH_FILE = "last_hash.txt"
# =======================================================

def get_url_hash(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().strip().encode('utf-8')
            return hashlib.md5(page_text).hexdigest()
    except Exception as e:
        print(f"Error reading {url}: {e}")
    return None

def send_whatsapp_alert(message_text, target_phone):
    if not target_phone:
        print("Skipping alert: Target phone number environment variable is empty.")
        return

    api_url = "https://api.wappfly.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WAPPFLY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "device_id": WAPPFLY_DEVICE_ID,
        "to": target_phone,
        "message": message_text
    }
    try:
        res = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if res.status_code in [200, 201]:
            print(f"WhatsApp alert successfully sent to {target_phone}!")
        else:
            print(f"Wappfly error for {target_phone}: {res.text}")
    except Exception as e:
        print(f"Failed to connect to Wappfly for {target_phone}: {e}")

def check_website():
    stored_hash = ""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            stored_hash = f.read().strip()

    current_hash = get_url_hash(URL_TO_WATCH)
    
    if current_hash:
        # If we have a past recorded state, and it doesn't match the new state -> SITE UPDATED!
        if stored_hash and stored_hash != current_hash:
            print("Change detected! Dispatching notifications...")
            alert_text = f"🚨 *NABI Career Page Update!* 🚨\n\nChanges found on: {URL_TO_WATCH}"
            
            # Loops through both numbers and pings them
            for phone in PHONE_NUMBERS:
                send_whatsapp_alert(alert_text, phone)
        else:
            print("No changes found on the page.")
        
        # Save the current state as the baseline benchmark for the next run
        with open(HASH_FILE, "w") as f:
            f.write(current_hash)
    else:
        print("Could not scrape page successfully on this run.")

if __name__ == "__main__":
    check_website()
