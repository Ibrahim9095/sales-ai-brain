# 🧠 Sales AI Brain

Bu layihə **süni intellekt əsaslı Telegram bot və AI beyin sistemi** üçün hazırlanıb.  
Əsas məqsəd: satış və müştəri məsləhətləri üçün ağıllı bot yaratmaq.

---

## ✅ Layihədə indiyə kimi görülən işlər

1. **Layihə strukturu quruldu** (`brain/` qovluğu, `app/`, `ai/`, `config/`, `memory/`, `data/`, `prompts/`)  
2. **FastAPI skeleton** yaradıldı (`main.py`)  
3. **Telegram bot skeleton** yaradıldı (`telegram_bot.py`)  
4. **Süni intellekt qovluğu** (`ai/`)  
   - `deepseek_client.py` → DeepSeek API sorğuları  
   - `memory.py` → istifadəçi cümlələri və cavabların yaddaşı  
   - `router.py` → AI routeları (gələcək üçün)  
5. **Config qovluğu** (`config/`)  
   - `settings.py` → API açarları və konfiqurasiya  
6. **Memory sistemi** (`memory/`)  
   - `memory.py`, `schemas.py` → chat yaddaşı, JSON fayla yazmaq  
7. **Prompts qovluğu** (`prompts/`) → ilkin prompt faylları  
8. **Data qovluğu** (`data/memory.json`) → istifadəçi yaddaşı  
9. **Telegram + DeepSeek inteqrasiyası** test edildi  
10. **GitHub reposuna push edildi** və backup alındı  
11. `.gitignore` faylı yaradıldı → lazım olmayan fayllar izlənmir

---

## 🛠 Texnologiyalar

- Python 3.13  
- FastAPI  
- Telegram Bot API (`python-telegram-bot`)  
- Requests (DeepSeek API üçün)  
- VS Code  

---

## ⚡ Növbəti addımlar

1. DeepSeek API ilə real test və mesaj cavablarının optimallaşdırılması  
2. Yaddaş sistemi JSON-dan DB-ya köçürülməsi (gələcək)  
3. Alternativ gəlir üçün botun funksiyalarının artırılması  
4. Telegram botun satış və müştəri davranışları üçün təkmilləşdirilməsi  
5. Continuous GitHub update və branch management  

---

## 🔑 Quraşdırma

1. Repo clone et:  
```bash
git clone https://github.com/Ibrahim9095/sales-ai-brain.git
cd sales-ai-brain
