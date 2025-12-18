import os
from dotenv import load_dotenv
from pathlib import Path

# .env yüklə
BASE_DIR = Path(__file__).resolve().parents[2]  # brain/
load_dotenv(BASE_DIR / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# yoxlama
print("Telegram token:", TELEGRAM_TOKEN)
print("DeepSeek key:", DEEPSEEK_API_KEY)
