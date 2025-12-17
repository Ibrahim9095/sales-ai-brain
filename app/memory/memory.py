import json
from datetime import datetime
import os

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "memory.json")

def save_message(user_id: int, role: str, message: str):
    # Mövcud faylı aç və oxu
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    # Yeni mesaj əlavə et
    entry = {
        "user_id": user_id,
        "user_text": message if role=="USER" else "",
        "ai_text": message if role=="AI" else "",
        "timestamp": datetime.now().isoformat()
    }
    data.append(entry)

    # JSON faylı yenilə
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
