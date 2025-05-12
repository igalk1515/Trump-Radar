import time
import random
import re
import hashlib
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
# Track hash of last meaningful post (not just raw text)
last_post_hash = None
print("🚀 Starting TrumpRadar - TruthSocial Monitor...")

def fetch_latest_post():
    driver.get(URL)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.status")))

    try:
        posts = driver.find_elements(By.CSS_SELECTOR, "div.status")

        for post in posts:
            # Skip pinned posts
            try:
                post.find_element(By.CLASS_NAME, "status__pinned-icon")
                continue  # It's pinned
            except:
                pass  # Not pinned, continue processing

            try:
                wrapper = post.find_element(By.CLASS_NAME, "status__content-wrapper")
                paragraphs = wrapper.find_elements(By.TAG_NAME, "p")
                texts = []

                for p in paragraphs:
                    text = p.text.strip()
                    if not text:
                        continue
                    if re.match(r"^\d{1,2}:\d{2}$", text):  # Skip timecodes
                        continue
                    if re.match(r"^\d+([.,]?\d*)?[kK]?$", text):  # Skip view counts
                        continue
                    texts.append(text)

                # Deduplicate repeated sentences
                seen_sentences = set()
                unique_sentences = []
                for sentence in re.split(r'(?<=[.!?]) +', " ".join(texts)):
                    if sentence not in seen_sentences:
                        seen_sentences.add(sentence)
                        unique_sentences.append(sentence)

                combined_text = " ".join(unique_sentences)
                if combined_text:
                    print(f"[🧠] Extracted from post: {combined_text}", flush=True)
                    return combined_text

            except Exception as e_inner:
                print(f"[⚠️] Skipped a post due to error: {e_inner}")
                continue

        print("[ℹ️] No valid non-pinned posts found.")
        return ""

    except Exception as e:
        print(f"[❗] Failed to process posts: {e}")
        return ""

try:
    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Checking for new posts...", flush=True)

        try:
            latest_post_text = fetch_latest_post()
            print(f"[{time.strftime('%H:%M:%S')}] Latest post text: {latest_post_text}", flush=True)
            cleaned_text = clean_text(latest_post_text)

            # Skip image/video-only posts
            lines = cleaned_text.splitlines()
            if lines == ['Donald J. Trump', '·'] or \
               (len(lines) == 3 and lines[0] == 'Donald J. Trump' and lines[1] == '·' and re.match(r'^\d{2}:\d{2}$', lines[2])):
                print(f"[{time.strftime('%H:%M:%S')}] Skipping non-textual post.")
                if not cleaned_text or current_hash == last_post_hash:
                    time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))
                continue

            if cleaned_text:
                # Normalize and hash post before analyzing
                normalized_text = re.sub(r'\s+', ' ', cleaned_text.strip())
                current_hash = hashlib.md5(normalized_text.encode()).hexdigest()

                if current_hash != last_post_hash:
                    sentiment = analyze_post(cleaned_text)  # 🔥 Only analyze if new or changed

                    print("\n=== 🚨 NEW POST OR EDIT DETECTED! 🚨 ===")
                    print(time.strftime("%Y-%m-%d %H:%M:%S"))
                    print("-" * 40)
                    print(cleaned_text)
                    print("-" * 40)

                    if not sentiment["cleaned_post"] or sentiment["summary"].lower().startswith("the post lacks"):
                        print(f"[{time.strftime('%H:%M:%S')}] Skipping empty or non-substantive post.")
                        continue

                    final_message = (
                        f"{cleaned_text}\n\n"
                        f"TLDR: {sentiment['summary']}\n"
                        f"{sentiment['emoji']} {sentiment['sentiment']} (Score: {sentiment['score']})"
                    )

                    if sentiment["relevant_stocks_or_sectors"]:
                        final_message += "\nRelated Stocks/Sectors: " + ", ".join(sentiment["relevant_stocks_or_sectors"])

                    send_message(final_message)
                    last_post_hash = current_hash
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] No change detected (same post).")


                if current_hash != last_post_hash:
                    print("\n=== 🚨 NEW POST OR EDIT DETECTED! 🚨 ===")
                    print(time.strftime("%Y-%m-%d %H:%M:%S"))
                    print("-" * 40)
                    print(cleaned_text)
                    print("-" * 40)

                    stocks = sentiment["relevant_stocks_or_sectors"]
                    stocks_text = f"\nRelated Stocks/Sectors: {', '.join(stocks)}" if stocks else ""

                    if not sentiment["cleaned_post"] or (sentiment["summary"].lower().startswith("the post lacks")):
                        print(f"[{time.strftime('%H:%M:%S')}] Skipping empty or non-substantive post.")
                        continue

                    # Construct the message with summary
                    final_message = (
                        f"{cleaned_text}\n\n"
                        f"TLDR: {sentiment['summary']}\n"
                        f"{sentiment['emoji']} {sentiment['sentiment']} (Score: {sentiment['score']})"
                    )

                    if sentiment["relevant_stocks_or_sectors"]:
                        final_message += "\nRelated Stocks/Sectors: " + ", ".join(sentiment["relevant_stocks_or_sectors"])

                    send_message(final_message)
                    last_post_hash = current_hash
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] No change detected (same post/sentiment).")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Empty or invalid post.")

        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ❗ Error: {e}", flush=True)

        time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))

except KeyboardInterrupt:
    print("\nMonitoring stopped manually.")
finally:
    driver.quit()

