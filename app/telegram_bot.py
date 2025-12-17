import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from ai.deepseek_client import ask_deepseek


from ai.deepseek_client import ask_deepseek
from memory.memory import save_message  # memory faylın yeri

# .env faylını yüklə
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text

    # İstifadəçi mesajını yadda saxla
    save_message(user_id, "USER", text)

    # DeepSeek cavabı al
    ai_reply = ask_deepseek(text)

    # AI cavabını yadda saxla
    save_message(user_id, "AI", ai_reply)

    # Cavabı istifadəçiyə göndər
    await update.message.reply_text(ai_reply)

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram bot işləyir...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
