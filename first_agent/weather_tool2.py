import random

def get_weather(city: str) -> str:
    """模拟天气查询（真实 API 可后续替换）"""
    weather_list = ["晴", "多云", "阴", "小雨", "中雨", "雷阵雨"]
    temp = random.randint(10, 35)
    weather = random.choice(weather_list)
    return f"{city} 当前天气：{weather}，温度 {temp}℃"