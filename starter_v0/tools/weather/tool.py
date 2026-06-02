from __future__ import annotations
import requests

def get_weather(location: str) -> dict:
    """Lấy thông tin thời tiết cho một địa điểm."""
    try:
        # Use wttr.in free API for real weather data
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current_condition", [{}])[0]
        temp = current.get("temp_C", "N/A")
        condition = current.get("lang_vi", [{}])[0].get("value") or current.get("weatherDesc", [{}])[0].get("value", "N/A")
        
        return {
            "items": [
                {
                    "location": location,
                    "temperature": f"{temp}°C",
                    "condition": condition,
                    "summary": f"Thời tiết tại {location} hiện tại là {condition}, nhiệt độ khoảng {temp}°C."
                }
            ]
        }
    except Exception as exc:
        return {
            "error": f"Không thể lấy thông tin thời tiết thực: {str(exc)}",
            "items": []
        }
