import os
import requests
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"

def ask_deepseek(message: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Sən satış və biznes üzrə ağıllı AI köməkçisən."},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as errh:
        print("❌ HTTP Error:", errh)
        return "DeepSeek API xətası: HTTP Error"
    except requests.exceptions.RequestException as err:
        print("❌ API Error:", err)
        return "DeepSeek API xətası: Unknown Error"
