import hashlib

def get_weather(location: str) -> dict:
    """Lấy thông tin thời tiết cho một địa điểm."""
    loc_clean = location.strip().lower()
    
    # Deterministic hash to seed selection
    h = int(hashlib.md5(loc_clean.encode('utf-8')).hexdigest(), 16)
    
    if "hà nội" in loc_clean or "ha noi" in loc_clean:
        temp = 28 + (h % 6)  # 28 to 33°C
        conditions = ["Nắng nóng", "Nhiều mây", "Mưa rào"]
        condition = conditions[h % len(conditions)]
    elif "hồ chí minh" in loc_clean or "ho chi minh" in loc_clean or "sài gòn" in loc_clean or "sai gon" in loc_clean:
        temp = 31 + (h % 5)  # 31 to 35°C
        conditions = ["Nắng gắt", "Có mưa giông", "Nhiều mây"]
        condition = conditions[h % len(conditions)]
    elif "đà lạt" in loc_clean or "da lat" in loc_clean:
        temp = 16 + (h % 6)  # 16 to 21°C
        conditions = ["Mát mẻ, sương mù", "Mưa nhẹ", "Nhiều mây"]
        condition = conditions[h % len(conditions)]
    elif "sapa" in loc_clean:
        temp = 12 + (h % 7)  # 12 to 18°C
        conditions = ["Lạnh, sương mù", "Mưa phùn", "Nhiều mây"]
        condition = conditions[h % len(conditions)]
    else:
        temp = 22 + (h % 10)  # 22 to 31°C
        conditions = ["Nắng", "Nhiều mây", "Mưa", "Gió nhẹ"]
        condition = conditions[h % len(conditions)]
    
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
