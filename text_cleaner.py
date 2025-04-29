import re

def clean_text(text: str = None) -> str:
    print("Cleaning text...")  # 👈 debug print
    """
    Cleans the post text:
    - Removes username, handle, post time
    - Removes counters (likes/comments/views numbers)
    - Removes 'Show More'
    - Removes URLs
    - If no text is provided, use default example text
    """

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip unwanted lines
        if not line:
            continue
        if line == "Show More":
            continue
        # if line.startswith("Donald J. Trump"):
        #     continue
        if line.startswith("@realDonaldTrump"):
            continue
        if re.match(r"^\d+[hms]?$", line):  # times like "1h" or "10m"
            continue
        if re.match(r"^\d{1,3}(\.\d{1,2})?[kK]?$", line):  # numbers like "300", "6.3k"
            continue
        if re.match(r"^(https?:\/\/)?[\w\.-]+\.[a-z]{2,}.*$", line):  # URLs
            continue

        cleaned_lines.append(line)

    print(f"Cleaned lines: {cleaned_lines}")  # 👈 debug print
    return "\n".join(cleaned_lines).strip()
