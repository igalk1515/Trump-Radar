import openai
from openai import OpenAI
from text_cleaner import clean_text
import json

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Replace safely!

def analyze_post(raw_text: str) -> dict:
    cleaned_text = clean_text(raw_text).strip()

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

    if not real_text:
        return {
            "cleaned_post": "",
            "sentiment": "Neutral",
            "score": 0,
            "emoji": "⚪",
            "relevant_stocks_or_sectors": []
        }

    system_prompt = """
You are a financial sentiment analyzer for political posts.

Your job is:
1. Summarize the main idea of the post in **one short sentence**.
2. Based on the post's tone and content, assess its potential impact on the U.S. stock market in the very near future (1-2 days).
3. Classify it into one of the following:
   - "Extremely Bullish"
   - "Bullish"
   - "Neutral"
   - "Bearish"
   - "Extremely Bearish"
4. Assign a score between -10 to +10 (+10 means the market is going to rise dramatically, -10 means the market is going to crash).
5. If the post clearly affects any specific stock tickers or sectors (e.g., Apple, Energy, Tech), list them.

Respond **only** in this exact JSON format:
{
  "summary": "One-sentence summary here.",
  "sentiment": "Neutral",
  "score": 0,
  "relevant_stocks_or_sectors": ["example1", "example2"]
}
"""


    user_prompt = f"Post:\n{real_text}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=300,
    )

    try:
        raw_content = response.choices[0].message.content.strip()

        # Remove markdown code block wrappers if present
        if raw_content.startswith("```"):
            raw_content = raw_content.strip("`").strip()
            if raw_content.startswith("json"):
                raw_content = raw_content[len("json"):].strip()

        try:
            result = json.loads(raw_content)
        except Exception as e:
            print("[❗] Failed to parse JSON from OpenAI response. Raw content:")
            print(response.choices[0].message.content)
            raise e

    except Exception as e:
        print("[❗] Failed to parse JSON from OpenAI response. Raw content:")
        print(response.choices[0].message.content)
        raise e

    summary = result.get("summary", "")
    sentiment = result.get("sentiment", "Neutral")
    score = result.get("score", 0)
    relevant = result.get("relevant_stocks_or_sectors", [])

    emoji = {
        "Extremely Bullish": "🟢🟢🟢",
        "Bullish": "🟢",
        "Neutral": "⚪",
        "Bearish": "🔴",
        "Extremely Bearish": "🔴🔴🔴"
    }.get(sentiment, "❓")

    # Extra attention if tariff-related
    attention_keywords = [
        # China / Trade War
        "china", "tariff", "tariffs", "trade war", "trade deal", "trade agreement",
        "import", "export", "sanction", "embargo", "ccp", "xi", "jinping", "chinese",


        # Market Crash
        "market", "selloff", "panic", "recession",
        "depression", "stagflation", "yield curve", "job losses", "inflation",

        # Government / Fed
        "fed", "interest rate", "hike", "cut rates", "quantitative tightening",
        "qe", "federal reserve", "central bank", "monetary policy"
    ]

    attention_grabber = any(keyword in real_text.lower() for keyword in attention_keywords)


    return {
        "cleaned_post": real_text,
        "summary": summary,
        "sentiment": sentiment,
        "score": score,
        "emoji": emoji + (" 🚨 🚨 🚨" if attention_grabber else ""),
        "relevant_stocks_or_sectors": relevant
    }