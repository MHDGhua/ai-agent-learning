import os
import requests
from dotenv import load_dotenv

load_dotenv()

HEFENG_KEY = os.getenv("HEFENG_KEY")

# 使用你的专属 Host（GeoAPI 也用同一个 Host，路径不同）
BASE_URL = "https://pn5egmpvnu.re.qweatherapi.com"
GEO_URL = f"{BASE_URL}/geo/v2/city/lookup"      # 城市搜索接口
WEATHER_URL = f"{BASE_URL}/v7/weather/now"      # 实时天气接口

def get_location_id(city_name: str) -> str:
    """
    调用和风天气 GeoAPI，根据城市名（支持中文、拼音、英文）获取 LocationID。
    返回 LocationID，如果失败返回 None。
    """
    params = {
        "location": city_name,
        "key": HEFENG_KEY
    }
    try:
        #使用 Python 的 requests 库发送一个 HTTP GET 请求，并将服务器返回的响应对象赋值给变量 resp。
        resp = requests.get(GEO_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "200":
            # 取第一个匹配的城市
            location = data.get("location", [])
            if location:
                return location[0]["id"]
            else:
                print(f"未找到城市: {city_name}")
                return None
        else:
            print(f"GeoAPI 错误码: {data.get('code')}")
            return None
    except Exception as e:
        print(f"GeoAPI 请求异常: {e}")
        return None

def get_weather(city: str) -> str:
    """查询任意城市的实时天气（自动获取 LocationID）"""
    if not HEFENG_KEY:
        return "错误：未配置和风天气 API Key，请在 .env 文件中设置 HEFENG_KEY"

    # 1. 动态获取 LocationID
    location_id = get_location_id(city)
    if not location_id:
        return f"抱歉，无法识别城市 '{city}'，请检查城市名是否正确。"

    # 2. 查询天气
    params = {
        "location": location_id,
        "key": HEFENG_KEY
    }
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
    print(get_weather("宜春"))