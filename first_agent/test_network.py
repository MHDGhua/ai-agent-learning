import requests

proxies = {
    "http": "http://127.0.0.1:7897",   # 替换成你的代理端口
    "https": "http://127.0.0.1:7897",
}

url = "https://atlas.microsoft.com/weather/currentConditions/json"
params = {"api-version": "1.0", "query": "39.9042,116.4074"}

try:
    resp = requests.get(url, params=params, proxies=proxies, timeout=10)
    print(f"状态码: {resp.status_code}")
except Exception as e:
    print(f"连接失败: {e}")