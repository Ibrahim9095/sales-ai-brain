from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Sales AI Brain")

class Message(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "AI Brain is running"}

@app.post("/ai")
def ai_response(message: Message):
    # HƏMİŞƏ "reply" açarı qaytarır
    return {"reply": f"Sənin mesajın alındı: {message.text}"}
