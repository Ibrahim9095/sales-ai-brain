# brain/app/services/fake_data_service.py
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class FakeDataService:
    """Dashboard üçün fake data generator"""
    
    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """Stats cards üçün data"""
        return {
            "total_users": 1247,
            "active_chats": 156,
            "messages_today": 2548,
            "avg_response_time": 2.4,
            "bot_online": True,
            "uptime_percent": 99.8,
            "high_risk_users": 5,
            "today_interventions": 12,
            "trends": {
                "users": {"change": 12.5, "type": "positive"},
                "chats": {"change": 8.2, "type": "positive"},
                "messages": {"change": -3.1, "type": "negative"},
                "response_time": {"change": -15.7, "type": "positive"}
            }
        }
    
    @staticmethod
    def get_alerts() -> List[Dict[str, Any]]:
        """Real-time alerts üçün data"""
        alerts = [
            {
                "id": "alert_001",
                "user_id": "user_001",
                "username": "İbrahim Əliyev",
                "risk_score": 92,
                "level": "high",
                "message": "Bahadır bu, qiymət çox yüksəkdir, rəqiblər daha ucuz satır",
                "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "tags": ["price", "urgent", "repeat"],
                "unread": True,
                "platform": "telegram"
            },
            {
                "id": "alert_002", 
                "user_id": "user_002",
                "username": "Leyla Məmmədova",
                "risk_score": 78,
                "level": "medium",
                "message": "Çatdırılma gecikir, pulumu qaytarın. 3 gün gözlədim",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "tags": ["delivery", "angry"],
                "unread": True,
                "platform": "telegram"
            },
            {
                "id": "alert_003",
                "user_id": "user_003", 
                "username": "Əli Hüseynov",
                "risk_score": 45,
                "level": "low",
                "message": "Məhsulun rəngi kataloqdan fərqlidir, dəyişdirmək istəyirəm",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "tags": ["quality"],
                "unread": False,
                "platform": "telegram"
            }
        ]
        return alerts
    
    @staticmethod
    def get_active_chats() -> List[Dict[str, Any]]:
        """Active chats üçün data"""
        chats = [
            {
                "id": "chat_001",
                "user_id": "user_001",
                "username": "İbrahim Əliyev",
                "last_message": "Bahadır bu, qiymətlər niyə belə yüksəkdir? Rəqibləriniz daha ucuz satır...",
                "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "risk_score": 92,
                "risk_level": "high",
                "unread_count": 3,
                "online": True
            },
            {
                "id": "chat_002",
                "user_id": "user_002",
                "username": "Leyla Məmmədova",
                "last_message": "Sifarişim hələ çatdırılmayıb, nə vaxt gələcək? Çox gecikir...",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "risk_score": 78,
                "risk_level": "medium", 
                "unread_count": 0,
                "online": True
            },
            {
                "id": "chat_003",
                "user_id": "user_003",
                "username": "Əli Hüseynov",
                "last_message": "Məhsulun rəngi kataloqdan fərqlidir, dəyişdirmək istəyirəm",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "risk_score": 45,
                "risk_level": "low",
                "unread_count": 0,
                "online": False
            }
        ]
        return chats
    
    @staticmethod
    def get_bot_status() -> Dict[str, Any]:
        """Bot status üçün data"""
        return {
            "online": True,
            "uptime": "48:15:22",
            "uptime_percent": 99.8,
            "response_time": 2.4,
            "active_sessions": 156,
            "total_requests": 12548,
            "memory_usage": 64,
            "cpu_usage": 42
        }
    
    @staticmethod
    def get_recent_interventions() -> List[Dict[str, Any]]:
        """Recent interventions üçün data"""
        return [
            {
                "id": "int_001",
                "user_id": "user_001",
                "username": "İbrahim Əliyev",
                "type": "discount",
                "action": "15% endirim təklifi",
                "result": "success",
                "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                "details": "15% endirim ilə qurtarıldı"
            },
            {
                "id": "int_002",
                "user_id": "user_002",
                "username": "Leyla Məmmədova",
                "type": "quick_reply",
                "action": "Sürətli cavab göndərildi",
                "result": "pending",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "details": "Çatdırılma izahı göndərildi"
            }
        ]