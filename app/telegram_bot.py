# brain/app/telegram_bot.py
import logging
import json
import os
import aiohttp
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from dotenv import load_dotenv

# .env faylını yüklə
load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path'ları DÜZGÜN TƏYİN ET
current_dir = Path(__file__).parent.absolute()  # brain/app
project_root = current_dir.parent.parent.absolute()  # brain/
data_dir = project_root / "data"
memory_path = data_dir / "memory.json"

# Qovluğu yarat
data_dir.mkdir(parents=True, exist_ok=True)

logger.info(f"📁 Project root: {project_root}")
logger.info(f"📁 Data dir: {data_dir}")
logger.info(f"📁 Memory path: {memory_path}")

# Environment dəyişənləri
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

logger.info(f"🔑 TELEGRAM_TOKEN: {'TAPILDI' if TELEGRAM_TOKEN else 'YOX'}")
logger.info(f"🤖 DEEPSEEK_API_KEY: {'TAPILDI' if DEEPSEEK_API_KEY else 'YOX'}")

class MemoryManager:
    def __init__(self):
        self.memory_path = memory_path
        self.memory_data = self.load_memory()
    
    def load_memory(self):
        """memory.json faylını yüklə"""
        try:
            if self.memory_path.exists():
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"✅ Memory yükləndi: {len(data.get('exact_matches', []))} sual")
                return data
            else:
                # Əgər fayl yoxdursa, BOŞ yaradaq
                empty_data = {"exact_matches": [], "partial_matches": []}
                self.save_memory(empty_data)
                logger.info("✅ Yeni boş memory.json yaradıldı")
                return empty_data
                
        except Exception as e:
            logger.error(f"❌ Memory yükləmə xətası: {e}")
            return {"exact_matches": [], "partial_matches": []}
    
    def save_memory(self):
        """memory.json faylına yaz"""
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Memory saxlandı: {len(self.memory_data.get('exact_matches', []))} sual")
            return True
        except Exception as e:
            logger.error(f"❌ Memory saxlanma xətası: {e}")
            return False
    
    def find_response(self, message: str):
        """Mesajı memory-də axtar - SADƏCƏ EXACT MATCH"""
        message = message.strip()
        
        for item in self.memory_data.get("exact_matches", []):
            for pattern in item.get("patterns", []):
                if message == pattern:
                    logger.info(f"✅ Exact match tapıldı: '{pattern}'")
                    return item.get("response")
        return None
    
    def add_question(self, question: str, answer: str):
        """Yeni sual-cavabı memory-ə əlavə et"""
        try:
            question = question.strip()
            answer = answer.strip()
            
            # Əvvəlcə yoxla ki, artıq var
            for item in self.memory_data.get("exact_matches", []):
                if question in item.get("patterns", []):
                    logger.info(f"ℹ️ Bu sual artıq var: '{question[:30]}...'")
                    return False
            
            # Yeni sual əlavə et
            new_item = {
                "patterns": [question],
                "response": answer,
                "added": datetime.now().isoformat(),
                "source": "deepseek_learned"
            }
            
            self.memory_data["exact_matches"].append(new_item)
            
            # Fayla yaz
            if self.save_memory():
                logger.info(f"🧠 Yeni sual əlavə edildi: '{question[:30]}...'")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Sual əlavə etmə xətası: {e}")
            return False
    
    def get_stats(self):
        """Memory statistikaları"""
        exact = len(self.memory_data.get("exact_matches", []))
        partial = len(self.memory_data.get("partial_matches", []))
        return {"total": exact + partial, "exact": exact, "partial": partial}

class DeepSeekClient:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    async def ask(self, question: str):
        """DeepSeek API-dan cavab al"""
        if not self.api_key:
            logger.error("❌ DeepSeek API KEY yoxdur!")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Satış köməkçisi kimi davran
            system_prompt = """Sən bir satış köməkçisi botsan. Müştərilərə məhsullar, qiymətlər, çatdırılma, zəmanət, 
            geri qaytarma və digər satış məsələlərində kömək edirsən. Cavablarını qısa, aydın və faydalı ver. 
            Rəsmi və mehriban üslubdan istifadə et."""
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    json=payload, 
                    headers=headers, 
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        reply = result["choices"][0]["message"]["content"]
                        logger.info("✅ DeepSeek cavabı alındı")
                        return reply
                    else:
                        error = await response.text()
                        logger.error(f"❌ DeepSeek xətası: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"🔥 DeepSeek xətası: {e}")
            return None

# Global instance'lar
memory = MemoryManager()
deepseek = DeepSeekClient()

# ƏSAS MESAJ HANDLER - SADƏ VERSİYA
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text
    
    logger.info(f"📨 {user.first_name}: {user_message[:50]}...")
    
    # 1. ƏVVƏLCƏ MEMORY-DƏ AXTAR
    memory_response = memory.find_response(user_message)
    
    if memory_response:
        # MEMORY-DƏ TAPDI - CAVAB VER
        logger.info("✅ Memory-dən cavab tapıldı")
        await update.message.reply_text(memory_response)
        return
    
    # 2. MEMORY-DƏ YOXDURSA - DEEPSEEK ÇAĞIR
    logger.info("❌ Memory-də yox, DeepSeek çağırılır...")
    
    # API-dan cavab al
    deepseek_response = await deepseek.ask(user_message)
    
    if not deepseek_response:
        # DeepSeek xətası
        await update.message.reply_text("Üzr istəyirəm, texniki problem yaşandı. Bir az sonra yenidən cəhd edin.")
        return
    
    # 3. CAVABI GÖNDƏR
    await update.message.reply_text(deepseek_response)
    
    # 4. YENİ SUALI MEMORY-Ə ƏLAVƏ ET (HƏR ŞEYDƏN ƏVVƏL!)
    success = memory.add_question(user_message, deepseek_response)
    
    if success:
        logger.info(f"💾 Yeni sual memory-ə əlavə edildi: '{user_message[:30]}...'")
    else:
        logger.error("❌ Sual memory-ə əlavə edilə bilmədi!")

# COMMAND HANDLERS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats = memory.get_stats()
    
    welcome_msg = f"""
👋 Salam {user.first_name}!

🤖 **SATIŞ KÖMƏKÇİSİ BOT**
Məhsullar, qiymətlər, çatdırılma və digər satış məsələlərində kömək edirəm.

📊 **Yaddaş statistikası:**
• Yaddaşda: {stats['total']} sual-cavab
• Exact: {stats['exact']}
• Partial: {stats['partial']}

🔄 **İşləmə prinsipi:**
1. Əvvəlcə yaddaşımda axtarıram
2. Tapmasam, AI-dan soruşuram  
3. Yeni cavabı YADDAŞIMA ƏLAVƏ EDİRƏM
4. Gələn dəfə eyni sualı bilərəm!

📝 **Nümunə suallar:**
• Məhsulun qiyməti nədir?
• Çatdırılma nə qədər çəkir?
• Zəmanət nə qədərdir?
"""
    
    await update.message.reply_text(welcome_msg)

async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memory statusunu göstər"""
    stats = memory.get_stats()
    
    # Son 5 sualı göstər
    recent = memory.memory_data.get("exact_matches", [])[-5:]
    recent_text = ""
    for i, item in enumerate(recent, 1):
        question = item.get("patterns", [""])[0]
        recent_text += f"{i}. {question[:40]}...\n"
    
    status_text = f"""
📊 **MEMORY STATISTIKASI**

• Ümumi sual: {stats['total']}
• Exact matches: {stats['exact']}
• Partial matches: {stats['partial']}

📁 Fayl: {memory_path}

📈 **Son 5 sual:**
{recent_text if recent_text else 'Heç bir sual yoxdur'}

ℹ️ Hər yeni sual avtomatik olaraq yaddaşa əlavə edilir.
"""
    
    await update.message.reply_text(status_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memory-i təmizlə (sadəcə test üçün)"""
    # Yalnız admin üçün
    memory.memory_data = {"exact_matches": [], "partial_matches": []}
    memory.save_memory()
    
    await update.message.reply_text("✅ Memory təmizləndi!")

# MAIN
def main():
    # Token yoxla
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_TOKEN təyin edilməyib!")
        logger.info("ℹ️ .env faylını yoxlayın:")
        logger.info("TELEGRAM_TOKEN=8590066805:AAF8piEn8JCWOhl8wFVS4q4t0bSI4hsv0UU")
        return
    
    try:
        # Botu qur
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Əmrlər
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("memory", memory_command))
        app.add_handler(CommandHandler("stats", memory_command))
        app.add_handler(CommandHandler("clear", clear_command))
        
        # Mesaj handler
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            handle_message
        ))
        
        # Başlama mesajı
        logger.info("=" * 60)
        logger.info("🤖 SATIŞ KÖMƏKÇİSİ BOT BAŞLADI")
        logger.info("=" * 60)
        logger.info(f"🧠 Memory: {memory.get_stats()['total']} sual")
        logger.info(f"🤖 DeepSeek: {'✅ Aktiv' if DEEPSEEK_API_KEY else '❌ Deaktiv'}")
        logger.info("=" * 60)
        logger.info("🔄 İŞLƏMƏ ALQORİTMASI:")
        logger.info("1. Sual gəlir")
        logger.info("2. memory.json-də axtarılır")
        logger.info("3. Tapılsa → memory cavabı")
        logger.info("4. Tapılmasa → DeepSeek çağırılır")
        logger.info("5. Yeni cavab → memory.json-a əlavə edilir")
        logger.info("=" * 60)
        
        # Botu başlat
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Bot xətası: {e}")
        raise

if __name__ == "__main__":
    main()