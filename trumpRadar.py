import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai_analyzer import analyze_post
from text_cleaner import clean_text
from telegram_bot import send_message

# --- Configuration ---
URL = "https://truthsocial.com/@realDonaldTrump"
MIN_SLEEP, MAX_SLEEP = 30, 60

# --- Setup Chrome ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

# --- Last seen cleaned post ---
last_cleaned_post = None

print("🚀 Starting TrumpRadar - TruthSocial Monitor...")

def fetch_latest_post():
    driver.get(URL)
    post = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-index='0']")))
    try:
        show_more = post.find_element(By.XPATH, ".//button[contains(text(), 'Show More')]")
        show_more.click()
        time.sleep(1)
    except:
        pass
    return post.find_element(By.CSS_SELECTOR, "div[data-testid='status']").text.strip()

try:
    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Checking for new posts...", flush=True)
        try:
            latest_post_text = fetch_latest_post()
            cleaned_text = clean_text(latest_post_text)  # 🧹 Clean it immediately

            # Special case: skip if it's just Trump + dot (image/video)
            lines = cleaned_text.splitlines()
            if lines == ['Donald J. Trump', '·'] or \
            (len(lines) == 3 and lines[0] == 'Donald J. Trump' and lines[1] == '·' and re.match(r'^\d{2}:\d{2}$', lines[2])):
                print(f"[{time.strftime('%H:%M:%S')}] Skipping non-textual post (video/image only).")
                time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))
                continue

            if cleaned_text and cleaned_text != last_cleaned_post:
                print("\n=== 🚨 NEW POST OR EDIT DETECTED! 🚨 ===")
                print(time.strftime("%Y-%m-%d %H:%M:%S"))
                print("-" * 40)
                print(cleaned_text)
                print("-" * 40)

                sentiment = analyze_post(cleaned_text)
                final_message = f"{cleaned_text}\n\n{sentiment['emoji']} {sentiment['sentiment']}"

                send_message(final_message)
                last_cleaned_post = cleaned_text
            else:
                print(f"[{time.strftime('%H:%M:%S')}] No change detected.", flush=True)

        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ❗ Error: {e}", flush=True)

        time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))

except KeyboardInterrupt:
    print("\nMonitoring stopped manually.")

finally:
    driver.quit()
