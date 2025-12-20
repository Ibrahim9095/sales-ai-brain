# brain/app/api/dashboard.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# ===== REAL DATA FUNCTIONS =====
# Bu funksiyalar main.py-dəki data storage-dan real məlumat gətirəcək

def get_real_dashboard_stats():
    """Real dashboard stats"""
    from ..main import chat_messages, active_users, intervention_mode, bot_stopped
    
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)
    
    # Günün mesajları
    today_msgs = [
        msg for msg in chat_messages
        if datetime.fromisoformat(msg["timestamp"]) > one_day_ago
    ]
    
    # Unikal user-lar
    unique_users_today = len(set(msg["user_id"] for msg in today_msgs))
    
    # Riskli user-lar
    warning_users = set()
    danger_users = set()
    
    for msg in today_msgs:
        uid = msg["user_id"]
        risk = msg.get("risk_score", 0)
        if risk > 80:
            danger_users.add(uid)
        elif risk > 60:
            warning_users.add(uid)
    
    # Müdaxilələr
    active_interventions = sum(1 for mode in intervention_mode.values() if mode)
    
    # Bot aktivliyi
    active_bots = len([uid for uid, stopped in bot_stopped.items() if not stopped])
    stopped_bots = len([uid for uid, stopped in bot_stopped.items() if stopped])
    
    return {
        "total_users": max(unique_users_today, 1),
        "active_chats": len(active_users),
        "messages_today": len(today_msgs),
        "messages_hour": len([m for m in today_msgs if datetime.fromisoformat(m["timestamp"]) > now - timedelta(hours=1)]),
        "warning_users": len(warning_users),
        "danger_users": len(danger_users),
        "active_interventions": active_interventions,
        "active_bots": active_bots,
        "stopped_bots": stopped_bots,
        "avg_response_time": 1.8,
        "server_status": "🟢 Online",
        "bot_status": "🟢 Active",
        "api_status": "🟢 Healthy"
    }

def get_real_alerts():
    """Real alerts"""
    from ..main import chat_messages
    
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    high_risk_msgs = [
        msg for msg in chat_messages
        if msg.get("risk_score", 0) > 70 and 
        datetime.fromisoformat(msg["timestamp"]) > one_hour_ago and
        not msg.get("is_bot", False)
    ]
    
    alerts = []
    for msg in high_risk_msgs[:10]:
        risk_level = "high" if msg["risk_score"] > 80 else "medium"
        
        alerts.append({
            "id": f"alert_{len(alerts)}",
            "username": msg["username"],
            "risk_score": msg["risk_score"],
            "level": risk_level,
            "message": msg["message"][:150],
            "timestamp": msg["timestamp"],
            "user_id": msg["user_id"],
            "risk_reasons": msg.get("risk_reasons", [])
        })
    
    return alerts

def get_real_active_chats():
    """Real active chats"""
    from ..main import chat_messages, active_users, intervention_mode, bot_stopped
    
    two_hours_ago = datetime.now() - timedelta(hours=2)
    
    recent_msgs = [
        msg for msg in chat_messages
        if datetime.fromisoformat(msg["timestamp"]) > two_hours_ago
    ]
    
    if not recent_msgs:
        return []
    
    # User-lara görə qrupla
    user_chats = defaultdict(list)
    for msg in recent_msgs:
        user_chats[msg["user_id"]].append(msg)
    
    chats = []
    for user_id, msgs in user_chats.items():
        msgs.sort(key=lambda x: x["timestamp"])
        last_msg = msgs[-1]
        
        # Risk analizi
        risk_scores = [m["risk_score"] for m in msgs]
        max_risk = max(risk_scores, default=0)
        
        # Sayımlar
        danger_count = len([m for m in msgs if m["risk_score"] > 80])
        warning_count = len([m for m in msgs if 60 < m["risk_score"] <= 80])
        
        # Son mesajı qısalt
        last_message = last_msg["message"]
        if len(last_message) > 120:
            last_message = last_message[:117] + "..."
        
        # Unread mesajlar (son 5 dəqiqə)
        five_min_ago = datetime.now() - timedelta(minutes=5)
        unread_count = len([
            m for m in msgs 
            if not m.get("is_bot", False) and 
            not m.get("is_admin", False) and
            datetime.fromisoformat(m["timestamp"]) > five_min_ago
        ])
        
        chats.append({
            "user_id": user_id,
            "username": last_msg["username"],
            "last_message": last_message,
            "last_time": last_msg["timestamp"],
            "is_bot": last_msg["is_bot"],
            "message_count": len(msgs),
            "risk_score": int(max_risk),
            "has_danger": danger_count > 0,
            "has_warning": warning_count > 0,
            "intervention_mode": intervention_mode.get(user_id, False),
            "bot_stopped": bot_stopped.get(user_id, False),
            "unread": unread_count,
            "last_activity": active_users.get(user_id, {}).get("last_active", datetime.now()).isoformat()
        })
    
    # Sırala (son aktiv əvvəl)
    chats.sort(key=lambda x: x["last_time"], reverse=True)
    return chats

def get_real_bot_status():
    """Real bot status"""
    from ..main import bot_stopped
    
    total_bots = len(bot_stopped)
    active_bots = len([uid for uid, stopped in bot_stopped.items() if not stopped])
    stopped_bots = len([uid for uid, stopped in bot_stopped.items() if stopped])
    
    return {
        "total": total_bots,
        "active": active_bots,
        "stopped": stopped_bots,
        "status": "active" if active_bots > stopped_bots else "warning",
        "last_check": datetime.now().isoformat()
    }

def get_real_recent_interventions():
    """Real interventions"""
    from ..main import intervention_mode, active_users
    
    interventions = []
    for user_id, intervened in intervention_mode.items():
        if intervened and user_id in active_users:
            interventions.append({
                "user_id": user_id,
                "username": active_users[user_id]["username"],
                "started_at": active_users[user_id].get("last_active", datetime.now()).isoformat(),
                "reason": "high_risk",
                "status": "active"
            })
    
    return interventions[-10:]  # Son 10 intervention

# ===== API ENDPOINTS =====
@router.get("/stats")
async def get_dashboard_stats():
    """Dashboard stats cards üçün data"""
    try:
        data = get_real_dashboard_stats()
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts():
    """Real-time alerts üçün data"""
    try:
        alerts = get_real_alerts()
        return {
            "success": True,
            "count": len(alerts),
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-chats")
async def get_active_chats():
    """Active chats üçün data"""
    try:
        chats = get_real_active_chats()
        return {
            "success": True,
            "count": len(chats),
            "chats": chats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bot-status")
async def get_bot_status():
    """Bot status üçün data"""
    try:
        status = get_real_bot_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-interventions")
async def get_recent_interventions():
    """Recent interventions üçün data"""
    try:
        interventions = get_real_recent_interventions()
        return {
            "success": True,
            "count": len(interventions),
            "interventions": interventions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def get_dashboard_overview():
    """Bütün dashboard data bir yerdə"""
    try:
        return {
            "success": True,
            "data": {
                "stats": get_real_dashboard_stats(),
                "alerts": get_real_alerts(),
                "active_chats": get_real_active_chats(),
                "bot_status": get_real_bot_status(),
                "recent_interventions": get_real_recent_interventions()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))