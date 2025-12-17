from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os
import requests

# .env faylını yüklə
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# FastAPI endpoint (test üçün)
API_URL = "http://127.0.0.1:8000/ai"

# Mesajı idarə edən funksiya
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # FastAPI-yə POST
    response = requests.post(API_URL, json={"text": user_text})
    ai_reply = response.json()["reply"]

    # Bot cavabı göndərir
    await update.message.reply_text(ai_reply)

# Botu işə salan funksiya
def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Telegram bot işləyir...")
    app.run_polling()

# Əsas
if __name__ == "__main__":
    run_bot()
