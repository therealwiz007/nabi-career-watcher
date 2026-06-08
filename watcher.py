import os
import requests
from bs4 import BeautifulSoup

# ==================== CONFIGURATION ====================
INSTANCE_ID = os.environ.get("WAPPFLY_DEVICE_ID")    # Green-API idInstance (from GitHub secrets)
API_TOKEN = os.environ.get("WAPPFLY_API_KEY")        # Green-API apiTokenInstance (from GitHub secrets)

PHONE_NUMBERS = [
    os.environ.get("PHONE_ONE"),                     # Format in secrets: 91XXXXXXXXXX@c.us
    os.environ.get("PHONE_TWO")                      # Format in secrets: 91XXXXXXXXXX@c.us (Optional)
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
            # Extract clean, non-empty text lines from the webpage
            return [line.strip() for line in soup.get_text().splitlines() if line.strip()]
    except Exception as e:
        print(f"Error reading {url}: {e}")
    return None

def send_whatsapp_alert(message_text, target_chat_id):
    if not target_chat_id or not INSTANCE_ID or not API_TOKEN:
        print(f"Skipping alert for {target_chat_id}: Missing credentials or phone token.")
        return
        
    # Official Green-API message endpoint routing
    api_url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
    
    payload = {
        "chatId": target_chat_id,
        "message": message_text
    }
    
    try:
        res = requests.post(api_url, json=payload, timeout=12)
        if res.status_code == 200:
            print(f"🎉 Success! WhatsApp alert sent to {target_chat_id}!")
        else:
            print(f"Green-API Error Code: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Failed to communicate with Green-API server: {e}")

def check_website():
    stored_lines = []
    # Load previous baseline if it exists
    if os.path.exists(TEXT_FILE):
        with open(TEXT_FILE, "r", encoding="utf-8") as f:
            stored_lines = [line.strip() for line in f.readlines() if line.strip()]

    # Fetch fresh live content
    current_lines = get_url_text(URL_TO_WATCH)
    
    if current_lines:
        if stored_lines:
            # Check for lines that are in the new content but weren't there before
            new_additions = [line for line in current_lines if line not in stored_lines]
            if new_additions:
                print("Changes detected! Preparing text summary...")
                alert_text = "🚨 *NABI Career Page Update!* 🚨\n\n"
                alert_text += f"🔗 *Link:* {URL_TO_WATCH}\n\n"
                alert_text += "➕ *What was added/changed:*\n"
                
                # Take up to the first 5 changes to keep the text neat
                for line in new_additions[:5]:
                    alert_text += f"• {line}\n"
                if len(new_additions) > 5:
                    alert_text += f"• _...and {len(new_additions) - 5} more lines._\n"
                
                # Send notifications
                for phone in PHONE_NUMBERS:
                    send_whatsapp_alert(alert_text, phone)
            else:
                print("No new content added since the last check.")
        else:
            print("First run: Establishing baseline tracking text file.")
        
        # Save the current state as the baseline for the next run
        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            for line in current_lines:
                f.write(f"{line}\n")
    else:
        print("Could not scrape page successfully.")

# ==================== EXECUTION CONTROL ====================
if __name__ == "__main__":
    check_website()
# ===========================================================
