import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from app.config.settings import TELEGRAM_TOKEN
from app.ai.deepseek_client import ask_deepseek
from app.memory.memory import get_answer_from_memory, learn_new_answer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()

    logger.info(f"📩 MESAJ GƏLDİ | user={user_id} | text='{text}'")

    # 1️⃣ MEMORY yoxla
    memory_answer = get_answer_from_memory(user_id, text)
    if memory_answer:
        logger.info("🧠 MEMORY TAPDI → DeepSeek çağırılmadı")
        await update.message.reply_text(memory_answer)
        return

    logger.info("❌ MEMORY TAPMADI → DeepSeek çağırılır")

    # 2️⃣ DeepSeek çağır
    teacher_answer = ask_deepseek(text)
    logger.info("🧑‍🏫 DeepSeek cavab verdi")

    # 3️⃣ Yaddaşa yaz
    learn_new_answer(user_id, text, teacher_answer)
    logger.info("💾 Cavab MEMORY-yə yazıldı")

    # 4️⃣ Cavabı göndər
    await update.message.reply_text(teacher_answer)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🤖 Bot işə düşdü")
    app.run_polling()

if __name__ == "__main__":
    main()
