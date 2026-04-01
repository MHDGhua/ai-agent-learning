import os
import requests
from dotenv import load_dotenv

load_dotenv()

HEFENG_KEY = os.getenv("HEFENG_KEY")
WEATHER_URL = "https://pn5egmpvnu.re.qweatherapi.com/v7/weather/now"

CITY_CODES = {
     "北京": "101010100",
    # "上海": "101020100",
    # "广州": "101280101",
    # "深圳": "101280601",
    # "杭州": "101210101",
    # "成都": "101270101",
    # "重庆": "101040100",
    # "南京": "101190101",
    # "武汉": "101200101",
    # "西安": "101110101",
}

def get_weather(city: str) -> str:
    if not HEFENG_KEY:
        return "错误：未配置和风天气密钥"
    code = CITY_CODES.get(city)
    if not code:
        support = "、".join(CITY_CODES.keys())
        return f"暂不支持 {city}，目前支持：{support}"
    params = {"location": code, "key": HEFENG_KEY}
    try:
        resp = requests.get(WEATHER_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "200":
            now = data.get("now", {})
            temp = now.get("temp")
            text = now.get("text")
            return f"{city} 当前天气：{text}，温度 {temp}℃"
        else:
            return f"天气查询失败：{data.get('code')}"
    except Exception as e:
        return f"天气查询失败：{str(e)}"

if __name__ == "__main__":
    print(get_weather("北京"))