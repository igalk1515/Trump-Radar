# telegram_bot.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
# Channel username with @, or your numeric user ID for testing
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@TrumpFeedUpdates")

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❗ Failed to send Telegram message: {response.text}")
        else:
            print(f"✅ Message sent successfully to channel.")
    except Exception as e:
        print(f"❗ Error sending Telegram message: {e}")
