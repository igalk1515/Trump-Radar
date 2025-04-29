# Base image: full Python
FROM python:3.11

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libglib2.0-0 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libgbm1 \
    libvulkan1 \
    xdg-utils \
    xvfb \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Install ChromeDriver matching Chrome 135
RUN wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/135.0.7049.114/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# Set virtual display (optional for headless Chrome)
ENV DISPLAY=:99

# Install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY trumpRadar.py .
COPY telegram_bot.py .
COPY text_cleaner.py .
COPY openai_analyzer.py .

# Start the script
CMD ["python", "trumpRadar.py"]
