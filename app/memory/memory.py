import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]  # brain/
MEMORY_FILE = BASE_DIR / "data" / "memory.json"
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_memory():
    if not MEMORY_FILE.exists():
        return {"users": {}}
    return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))

def save_memory(data):
    MEMORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_answer_from_memory(user_id: str, question: str):
    data = load_memory()
    user = data.get("users", {}).get(user_id)
    if not user:
        return None
    for item in user.get("learned", []):
        if item["question"].lower() == question.lower():
            return item["answer"]
    return None

def learn_new_answer(user_id: str, question: str, answer: str):
    data = load_memory()
    users = data.setdefault("users", {})
    user = users.setdefault(user_id, {})

    # Əgər "learned" yoxdursa, əlavə et
    user.setdefault("learned", [])

    user["learned"].append({
        "question": question,
        "answer": answer,
        "learned_at": datetime.utcnow().isoformat()
    })

    save_memory(data)

    data = load_memory()
    users = data.setdefault("users", {})
    user = users.setdefault(user_id, {"learned": []})
    user["learned"].append({
        "question": question,
        "answer": answer,
        "learned_at": datetime.utcnow().isoformat()
    })
    save_memory(data)
