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
        print(f"Skipping alert for {target_phone}: Missing credentials or secret values.")
        return
        
    # The official primary text sending endpoint route
    api_url = "https://wappfly.com/api/send/text"
    
    # Passing token inside headers as explicitly required
    headers = {
        "X-API-Token": WAPPFLY_API_KEY
    }
    
    # Wappfly requires standard Form Data payload delivery rather than a JSON dictionary
    payload_data = {
        "device_id": WAPPFLY_DEVICE_ID,
        "to": target_phone,
        "message": message_text
    }
    
    try:
        # Note: We use 'data=payload_data' instead of 'json=payload' to bypass 404 parsing errors
        res = requests.post(api_url, data=payload_data, headers=headers, timeout=15)
        if res.status_code in [200, 201]:
            print(f"🎉 Success! WhatsApp alert successfully sent to {target_phone}!")
        else:
            print(f"Wappfly Alert Return Code: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to communicate with Wappfly server: {e}")

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

# ==================== EXECUTION CONTROL ====================
if __name__ == "__main__":
    print("🚀 Forcing active connection trial to verify live Wappfly dashboard tier...")
    test_msg = "🚀 *Wappfly System Verification!* 🚀\n\nYour free tier automation code and GitHub setup are processing cleanly!"
    
    for phone in PHONE_NUMBERS:
        send_whatsapp_alert(test_msg, phone)
# ===========================================================
