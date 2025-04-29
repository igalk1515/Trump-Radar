# telegram_bot.py

import requests

TELEGRAM_TOKEN = "7200645597:AAHZJLtdLBQRS48jOCqAjb9luYVHMEW0HgQ"
TELEGRAM_CHAT_ID = "@TrumpFeedUpdates"  # Your Telegram CHANNEL username with @
# TELEGRAM_CHAT_ID = "889968462"  # Your Telegram user ID

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
