import openai
from openai import OpenAI
from text_cleaner import clean_text

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Replace safely!

def analyze_post(raw_text: str) -> dict:
    # ✨ Clean early
    cleaned_text = clean_text(raw_text).strip()

    # ✨ If still garbage like "Donald J. Trump", remove it
    cleaned_lines = cleaned_text.splitlines()
    final_lines = []

    for line in cleaned_lines:
        line = line.strip()
        if line.lower().startswith("donald j. trump"):
            continue
        if line == "·":
            continue
        final_lines.append(line)

    real_text = "\n".join(final_lines).strip()

    # ✨ If cleaned text is empty, assume neutral
    if not real_text:
        return {
            "cleaned_post": "",
            "sentiment": "Neutral",
            "emoji": "⚪"
        }

    system_prompt = """
You are a financial sentiment analyzer for political posts.

Your job is:
- Given a post, determine if it is Bullish (positive), Bearish (negative), or Neutral for the general market.
- Only answer with one of these categories: "Bullish", "Bearish", or "Neutral".
"""

    user_prompt = f"Post:\n{real_text}\n\nAnswer only: Bullish, Bearish, or Neutral."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=10,
    )

    result = response.choices[0].message.content.strip()

    emoji = {
        "Bullish": "🟢",
        "Bearish": "🔴",
        "Neutral": "⚪"
    }.get(result, "❓")

    return {
        "cleaned_post": real_text,
        "sentiment": result,
        "emoji": emoji
    }
