# brain/app/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram AI Monitor")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cari qovluğu tap
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
admin_panel_path = os.path.join(project_root, "telegram_admin_panel")

# ================== STATIC FAYLLAR - DÜZGÜN QURULUŞ ==================
# HTML faylları
html_path = os.path.join(admin_panel_path, "html")
if os.path.exists(html_path):
    app.mount("/html", StaticFiles(directory=html_path, html=True), name="html")

# CSS faylları
css_path = os.path.join(admin_panel_path, "css")
if os.path.exists(css_path):
    app.mount("/css", StaticFiles(directory=css_path), name="css")

# JS faylları
js_path = os.path.join(admin_panel_path, "js")
if os.path.exists(js_path):
    app.mount("/js", StaticFiles(directory=js_path), name="js")

# Static fayllar (images, sounds)
static_path = os.path.join(admin_panel_path, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# ================== ROUTES ==================
@app.get("/")
async def root():
    """Əsas səhifə"""
    return {"message": "Telegram AI Monitor API", "version": "1.0.0"}

@app.get("/admin")
async def admin_panel():
    """Admin panel səhifəsi"""
    html_file = os.path.join(html_path, "conversations.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    return {"error": "Admin panel not found"}

@app.get("/health")
async def health_check():
    """Server status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "Telegram AI Monitor",
        "api_version": "1.0.0"
    }

# ================== DATA STORAGE ==================
chat_messages = []
active_users = {}

# ================== WEBSOCKET ==================
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"📡 Yeni WebSocket: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ================== API ENDPOINTS ==================
class TelegramMessage(BaseModel):
    user_id: str
    username: str
    message: str
    is_bot: bool = False
    is_admin: bool = False
    risk_score: int = 0

@app.post("/api/telegram/message")
async def receive_telegram_message(message: TelegramMessage):
    """Telegram botundan mesaj qəbul et"""
    try:
        message_data = {
            "user_id": message.user_id,
            "username": message.username,
            "message": message.message,
            "is_bot": message.is_bot,
            "is_admin": message.is_admin,
            "risk_score": message.risk_score,
            "timestamp": datetime.now().isoformat()
        }
        
        chat_messages.append(message_data)
        
        # Aktiv user-ları yenilə
        active_users[message.user_id] = {
            "username": message.username,
            "last_message": message.message[:100],
            "last_time": datetime.now().isoformat(),
            "risk_score": message.risk_score
        }
        
        logger.info(f"📨 Telegram: {message.username} -> {message.message[:50]}...")
        
        # WebSocket bildiriş
        await manager.broadcast({
            "type": "new_message",
            "data": message_data
        })
        
        return JSONResponse({
            "success": True,
            "message": "Mesaj qəbul edildi",
            "risk_score": message.risk_score
        })
        
    except Exception as e:
        logger.error(f"Mesaj xətası: {e}")
        return JSONResponse({"success": False, "error": str(e)})

@app.get("/api/chats/active")
async def get_active_chats():
    """Aktiv söhbətləri gətir"""
    try:
        # Son 1 saat ərzində aktiv olan söhbətlər
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        active_list = []
        for user_id, user_data in active_users.items():
            last_time = datetime.fromisoformat(user_data["last_time"])
            if last_time > one_hour_ago:
                active_list.append({
                    "user_id": user_id,
                    "username": user_data["username"],
                    "last_message": user_data["last_message"],
                    "last_time": user_data["last_time"],
                    "risk_score": user_data["risk_score"],
                    "message_count": len([m for m in chat_messages if m["user_id"] == user_id])
                })
        
        # Son aktivliyə görə sırala
        active_list.sort(key=lambda x: x["last_time"], reverse=True)
        
        return {
            "success": True,
            "chats": active_list,
            "count": len(active_list),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/chats/{user_id}/full")
async def get_full_chat(user_id: str):
    """User-ın tam chat tarixçəsini gətir"""
    try:
        # User-ın mesajlarını tap
        user_messages = [
            msg for msg in chat_messages 
            if msg["user_id"] == user_id
        ]
        
        if not user_messages:
            return {
                "success": False,
                "error": "Bu user üçün mesaj tapılmadı"
            }
        
        formatted_messages = []
        for msg in user_messages[-50:]:
            sender_type = "user"
            sender_name = msg["username"]
            
            if msg.get("is_bot"):
                sender_type = "bot"
                sender_name = "🤖 Bot"
            elif msg.get("is_admin"):
                sender_type = "admin"
                sender_name = "👨‍💼 Admin"
            
            formatted_messages.append({
                "sender": sender_name,
                "text": msg["message"],
                "time": datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M"),
                "is_bot": msg.get("is_bot", False),
                "is_admin": msg.get("is_admin", False),
                "risk_score": msg.get("risk_score", 0)
            })
        
        # Statistikalar
        risk_scores = [m.get("risk_score", 0) for m in user_messages]
        max_risk = max(risk_scores) if risk_scores else 0
        
        return {
            "success": True,
            "username": user_messages[0]["username"],
            "user_id": user_id,
            "messages": formatted_messages,
            "stats": {
                "total": len(user_messages),
                "max_risk": max_risk,
                "risk_level": "YÜKSƏK" if max_risk > 80 else "ORTA" if max_risk > 60 else "AŞAĞI",
                "last_activity": "indi"
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ================== DEMO DATA ==================
@app.post("/api/demo/message")
async def create_demo_message():
    """Demo mesaj yarat"""
    import random
    
    users = ["Əli Hüseynov", "Ayşə Quliyeva", "Kamran Əliyev", "Leyla Məmmədova"]
    messages = [
        "Salam, məhsulun qiyməti nə qədərdir?",
        "Sifarişim gecikir, nə baş verib?",
        "Məhsuldan narazıyam, qaytarmaq istəyirəm!",
        "Kömək lazımdır, problem var!"
    ]
    
    user = random.choice(users)
    message = random.choice(messages)
    
    demo_msg = TelegramMessage(
        user_id=f"demo_{random.randint(1000, 9999)}",
        username=user,
        message=message,
        risk_score=random.randint(20, 90)
    )
    
    return await receive_telegram_message(demo_msg)

# ================== STARTUP ==================
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("🚀 TELEGRAM AI MONITOR SERVER")
    logger.info("=" * 60)
    logger.info("🌐 Admin Panel: http://localhost:8000/admin")
    logger.info("📡 API: http://localhost:8000/api")
    logger.info("🔌 WebSocket: ws://localhost:8000/ws")
    logger.info("🤖 Telegram Bot: READY")
    logger.info("=" * 60)

# ================== SERVER RUN ==================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)